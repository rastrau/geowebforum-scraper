if (!require(lubridate)) {
  install.packages('lubridate')
  require(lubridate)
}
if (!require(here)) {
  install.packages('here')
  require(here)
}
if (!require(tidyverse)) {
  install.packages('tidyverse')
  require(tidyverse)
}
if (!require(magrittr)) {
  install.packages('magrittr')
  require(magrittr)
}
if (!require(RSQLite)) {
  install.packages('RSQLite')
  require(RSQLite)
}
if (!require(DBI)) {
  install.packages('DBI')
  require(RSQLite)
}

source(here('functions.R'))


# Set start and end year. Geowebforum was started in 2003.
min_year <- 2003
max_year <- 2018


# Set paths
wd <- here()
db <- here('..', 'data.sqlite')

# Establish the connection to the SQLite database
con <- dbConnect(RSQLite::SQLite(), db)
dbListTables(con)



query_topic_per_year <- function(con, topic, exact){
  # Function for querying the geowebforum SQLite database with a keyword (compared 
  # against the 'posts.post_text' after lower-casing)
  
  # <exact> needs more testing -- currently unsure if this option works properly already. 
  # For now, use 'exact = FALSE' which matches the lower-cased query string to any part of
  # lower-cased post_text in the database (without e.g. space-padding). This can be a 
  # problem if you search for short terms that are commonly part of other words, e.g. 
  # searching for 'AV' would also return hits for e.g. 'average', 'avisieren', 'avouer', 
  # etc.
  if (exact) {
    topic_string <- str_c('"% ', topic, ' %"')  
    comparison_string <- 'post_text'
  }
  else {
    topic_string <- str_c('LOWER("%', topic, '%")')  
    comparison_string <- 'LOWER(post_text)'
  }
  
  data <- data.frame(term = character(), 
                     year = integer(), 
                     count = integer()) 
  years = min_year:max_year
  for (year in years){ 
    query = str_c('SELECT * FROM posts WHERE LIKE(',
                  topic_string,
                  ', ', comparison_string, ') AND ',
                  'strftime("%Y-%m-%d %H:%M:00.000", post_time) BETWEEN "',
                  year, '-01-01" AND "',
                  year, '-12-31"')  
    results <- dbSendQuery(con, query)
    raw_data <- dbFetch(results)
    dbClearResult(results)
    annual_data <- raw_data %<>% 
      mutate(datetime = ymd_hms(post_time), year = year(datetime)) %>%
      group_by(year) %>%
      summarise(count = n()) %>%
      mutate(term=topic) %>%
      select(term, year, count)
    if (nrow(annual_data) == 0){
      annual_data[1, ] <- c(topic, year, 0)
    }
    data <- rbind(data, annual_data)
    
    # Despite the dataframe definition, also numeric data seems to be stored as characters
    data %<>%
      mutate(year = as.integer(year), count = as.integer(count))
  }
  return(data)
}


find_larger_five <- function(critical_value){
  # Function to find the smallest number divisible by 5 that is larger than the 
  # input value
  larger <- FALSE
  values <- seq(0, 10000, 5)
  for (value in values){
    if (value >= critical_value){
      return(value)
    }
  }
  return(100000)
}


find_larger_ten <- function(critical_value){
  # Function to find the smallest number divisible by 10 that is larger than the 
  # input value
  larger <- FALSE
  values <- seq(0, 10000, 10)
  for (value in values){
    if (value >= critical_value){
      return(value)
    }
  }
  return(100000)
}


query_topics <- function(topics){
  # Function for querying any number of topics (one or many) and for assembling the 
  # results into a tidy dataframe
  data <- data.frame(term = character(), 
                     year = integer(), 
                     count = integer()) 
  for (topic in topics){
    raw_data = query_topic_per_year(con, topic, exact=FALSE)
    data <- rbind(data, raw_data)
  }
  # Despite the dataframe definition, also numeric data seems to be stored as characters
  data %<>%
    mutate(year = as.integer(year), count = as.integer(count))
  return(data)
}


find_plot_title <- function(data){
  # Function for automatically generating a sensible title for a plot
  plot_title <- 'Occurrences of certain terms in geowebforum posts'
  
  if (length(unique(data$term)) == 2){
    plot_title <- paste('Occurrences of “', unique(data$term)[1], '” and “',
                        unique(data$term)[2], '”', sep='')
    plot_title <- paste(plot_title, 'in geowebforum posts', sep='\n')
  }
  else if (length(unique(data$term)) == 1){
    plot_title <- paste('Occurrences of the term “', unique(data$term)[1], '”', sep='')
    plot_title <- paste(plot_title, 'in geowebforum posts', sep='\n')
  }

  return(plot_title)
}

plot_absolute <- function(data, out_file=NULL){
  # Function for drawing and saving a plot showing absolute numbers
  if (is.null(out_file)) {
    out_f <- paste(c(unique(data$term), 'per-year--absolute.png'), sep="-", collapse="-")
  }
  else {
    out_f <- out_file
  }

  plot_title <- find_plot_title(data)
  if (max(data$count) <= 30){
    max_y <- find_larger_five(max(data$count))
    step_size <- 5
  }
  else{
    max_y <- find_larger_ten(max(data$count))
    step_size <- 10
  }
  
  p <- ggplot(data, aes(x=year, y=count, color=term)) +
    theme_geowebforumscraper() + 
    geom_line(size=2) +
    scale_y_continuous(limits=c(0, max_y), breaks=seq(0, max_y, step_size)) +
    scale_x_continuous(breaks=c(min_year:max_year)) +
    scale_colour_brewer(palette='Set2') +
    labs(title=plot_title, 
         subtitle='\nThe number of times each term has been mentioned at least once in a post on geowebforum.ch, per year\n', 
         caption='made using data from https://github.com/rastrau/geowebforum-scraper',
         x='\nYear',
         y='Number of mentions\n')
  ggsave(here(out_f), p, width=25, height=17, units='cm')
  print(paste('-> Saved figure to', here(out_f)))
  return(p)
}


plot_indexed <- function(data, out_file=NULL){
  # Function for drawing and saving a plot showing max-indexed numbers
  if (is.null(out_file)) {
    out_f <- paste(c(unique(data$term), 'per-year--indexed.png'), sep="-", collapse="-")
  }
  else {
    out_f <- out_file
  }
  
  plot_title <- find_plot_title(data)
  plot_title <- paste(plot_title, '(indexed)') 
  
  indexed_data <- data %>%
    full_join(data %>%
                group_by(term) %>%
                summarise(max_count = max(count)),
              'term')
  indexed_data %<>%
    mutate(prominence = count / max_count)
  
  q <- ggplot(indexed_data, aes(x=year, y=prominence, color=term)) +
    theme_geowebforumscraper() + 
    geom_line(size=2) +
    scale_x_continuous(breaks=c(min_year:max_year)) +
    scale_colour_brewer(palette='Set2') +
    labs(title=plot_title, 
         subtitle='\nThe number of times each term has been mentioned at least once in a post on geowebforum.ch, per year,\nindexed to the year with maximum number of mentions\n', 
         caption='made using data from https://github.com/rastrau/geowebforum-scraper',
         x='\nYear',
         y='Number of mentions, indexed\n')
  ggsave(here(out_f), width=25, height=17, units='cm')
  print(paste('-> Saved figure to', here(out_f)))
  return(q)
}


# Run some example analyses, create plots and save them to disk

# Events
terms <- c('geosummit', 'geobeer')
data = query_topics(terms)
plot_absolute(data)
plot_indexed(data)

# Data formats
terms <- c('shapefile', 'interlis', 'xml', 'csv')
data = query_topics(terms)
plot_absolute(data)
plot_indexed(data)

# Services
terms <- c('wfs', 'wms', 'wmts')
data = query_topics(terms)
plot_absolute(data)
plot_indexed(data)

# The impulse program e-geo.ch that ran from 2003 to 2016
terms <- c('e-geo')
data = query_topics(terms)
plot_absolute(data)
plot_indexed(data)

# Standardisation: data models
terms <- c('mgdm', 'geodatenmodell')
data = query_topics(terms)
plot_absolute(data)
plot_indexed(data)

# The law
terms <- c('geoig', 'geoiv')
data = query_topics(terms)
plot_absolute(data)
plot_indexed(data)

# ;-) In which I stand no chance
terms <- c('keller', 'straumann')
data = query_topics(terms)
plot_absolute(data)
plot_indexed(data)

# The blog by EBP
terms <- c('geo.ebp.ch')
data = query_topics(terms)
plot_absolute(data)
plot_indexed(data)

# 'Trendy' topics
terms <- c('open', 'smart', '3d')
data = query_topics(terms)
plot_absolute(data)
plot_indexed(data)

dbDisconnect(con)



