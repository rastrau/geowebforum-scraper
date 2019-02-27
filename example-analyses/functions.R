if (!require(here)) {
  install.packages('here')
  require(here)
}


# https://ggplot2.tidyverse.org/reference/theme.html
theme_geowebforumscraper <- function() {
  theme_minimal() +
    theme(
      text = element_text(color = "#22211d"),
      plot.title = element_text(lineheight=1, size = rel(2.1), family='serif', face='bold'),
      plot.subtitle = element_text(size = rel(1.2), lineheight=1),
      plot.caption = element_text(size = rel(0.7)),
      plot.background = element_rect(fill = '#FAFAFA', colour=NA),
      legend.position = 'top',
      legend.key.width = unit(1, 'cm'),
      legend.spacing.x = unit(0.3, 'cm'),
      legend.text = element_text(size = rel(1.1)),
      legend.title = element_blank(),
      panel.grid.minor.x = element_blank(),
      plot.margin = margin(5, 5, 5, 5, 'mm'))
}

