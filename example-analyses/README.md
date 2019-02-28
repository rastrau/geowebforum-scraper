# geowebforum-scraper: Example analyses
This folder collects avenues to analyse the contents of geowebforum.ch that were scraped into an SQLite database using https://github.com/rastrau/geowebforum-scraper/blob/master/scrape-geowebforum.py.

## Collaboration
If you'd like to further develop these analyses or talk about applications, I'm open. Please [get in touch through mail](mailto:ralph.straumann@gmail.com) or directly on GitHub.

## Dependencies and Development
- SQL files: none
- R files: as stated in the files themselves. Packages are loaded (or installed, if necessary) at the beginning of the R scripts using the `if (!require(<package-name>)) { }` construct.

The R code was developed and tested under R version 3.5.1. You can download R from [www.r-project.org](https://www.r-project.org).

## Example Results

### Find-longest-threads.sql
The SQL script [Find-longest-threads.sql](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/Find-posts-per-author.sql) queries the database for threads and sorts them in descending order by the number of posts contained in each thread.

### Find-posts-per-author.sql
The SQL script [Find-posts-per-author.sql](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/Find-posts-per-author.sql) queries the database for authors (encrypted names) and sorts them in descending order by the number of posts they have published on geowebforum.ch. You can use this script to analyse the so-called contributor bias of the forum.

### Count-post-languages.sql
The SQL script [Count-post-languages.sql](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/Count-post-languages.sql) queries the database for languages of public posts (as classified using Python's `langdetect`) and counts them. You can use this script to analyse the representation of language regions in the forum.

### Content-analysis.R
This script needs to be run from R (or RStudio with R installed). It uses the database and analyses the number of posts per year that mention a term or a set of terms. It then creates two graphs: One of the absolute number of posts mentioning the term(s) over time, and one of the some data where the data is indexed to the value of 1 in the year with the maximum number of mentions.

This script enables you to very easily run your own custom analyses. By adjusting the terms in the character vector on line 1 of the following snippet you can create your own visualizations (the analysis is case-insensitive):

```
terms <- c('geoig', 'geoiv')
data = query_topics(terms)
plot_absolute(data)
plot_indexed(data)
```

Some valid examples:
`terms <- c('analysing just one term')`
`terms <- c('term1', 'term2')`
`terms <- c('geo', 'gis', 'webgis')`

Below you can see some examples that are included in the script already.

#### The impulse program e-geo.ch that ran from 2003 to 2016
![e-geo](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/e-geo-per-year--absolute.png "e-geo")

#### The law
![geoig vs. geoiv](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/geoig-geoiv-per-year--absolute.png "geoig vs. geoiv")

#### 'Trendy' topics
![open, smart, 3d](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/open-smart-3d-per-year--absolute.png "open, smart, 3d")

#### The trendiest topic, maybe?
![bim](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/bim-per-year--absolute.png "bim")

#### Data formats
![shapefile, interlis, xml, csv (indexed)](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/shapefile-interlis-xml-csv-per-year--indexed.png "shapefile, interlis, xml, csv (indexed)")

#### Standardisation: data models
![mgdm, geodatenmodell](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/mgdm-geodatenmodell-per-year--absolute.png "mgdm, geodatenmodell")

#### Services
![wfs, wms, wmts](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/wfs-wms-wmts-per-year--absolute.png "wfs, wms, wmts")

#### Events
![geobeer, geosummit](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/geosummit-geobeer-per-year--absolute.png "geobeer, geosummit")

#### The blog by EBP
![geo.ebp.ch](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/geo.ebp.ch-per-year--absolute.png "geo.ebp.ch")

#### In which I stand no chance ;-)
![keller, straumann](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/keller-straumann-per-year--absolute.png "keller, straumann")





## Final notes
This code was written for a private project investigating the Swiss GIS community. It is definitely a bit rough around the edges, doesn't have proper logging or full-fledged exception handling.

Please use this code responsibly.
