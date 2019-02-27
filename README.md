# geowebforum-scraper
A scraper for structuring the content of [geowebforum.ch](https://geowebforum.ch) into a database. Thanks go to [Stefan Keller](https://www.twitter.com/sfkeller) for running geowebforum.ch and declaring it open data.

This scraper retrieves [geowebforum.ch](https://geowebforum.ch) content, transforms it into a relational structure and stores it in an [SQLite database](https://www.sqlite.org/index.html). Not yet implemented is an easy way for updating the database with the most recent geowebforum posts. The obvious avenue for this would be to periodically parse the feed at [geowebforum.ch/last_entries.php](https://geowebforum.ch/last_entries.php) (which exposes the 50 latest geowebforum posts), filter out posts that are not yet present in the database and add them. The database is already equipped with triggers which update thread and post counts in all pertinent tables as soon as a new thread or post is added to the database.

The code is licensed under the [GNU General Public License v3.0](https://github.com/rastrau/geowebforum-scraper/blob/master/LICENSE). Conditions by [geowebforum](https://geowebforum.ch/benutzungsordnung.php) might apply for the data.

## Collaboration
If you'd like to further develop this code or talk about applications, I'm open. Please [get in touch through mail](mailto:ralph.straumann@gmail.com) or directly on GitHub.

## Dependencies and Development
Non-core Python packages:
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup): A package for website scraping
- [langdetect](https://github.com/Mimino666/langdetect): A package for detecting the language of text
- [unidecode](https://pypi.org/project/Unidecode): A package for deriving ASCII representations of unicode strings

Core Python packages:
- urllib2
- sqlite3
- datetime
- time
- hashlib

This code was developed and tested under Python 2.7 (on a Mac OS X platform).

## Inputs
The script requires no input. Important variables can (and should) be adjusted directly by editing the file `Variables.py`:

- `db_path`: Here you can adjust the name of the output SQLite database.
- `topics`: Here you can make adjustments if you are only interested in a subset of the topics on geowebforum.ch or if geowebfom.ch decides to add additional topics.

## Usage

Open a command line / shell in the `geowebforum-scraper` directory and issue the following command:

`python scrape-geowebforum.py`

## Outputs
The script creates an SQLite database named `data.sqlite` by default. You can further analyse the data in this database using any SQLite-compatible database client, such as [DBeaver](https://dbeaver.io), or, for example, Packages such as [RSQLite](https://db.rstudio.com/databases/sqlite/) to issue queries from within R.

The database contains data extracted from geowebforum.ch. The data is structured into 4 tables:
- `metadata`
- `topics`
- `threads`
- `posts`

These each hold the following contents:

### Table `metadata`
- `last_updated` (text; SQLite has no datetime format): Timestamp of when the last run of `scrape-geowebforum.py` finished. The timestamp follows the format `%Y-%m-%d %H:%M`.
- `comments`: currently empty, you could enter text using the function `write_metadata()`.
### Table `topics`
- `topic_id` (int, primary key): numeric ID of the geowebforum topic (not linked to geowebforum.ch, but inherent to *geowebforum-scraper*).
- `topic_name` (text): name of the geowebforum topic.
- `topic_url` (text): URL of the geowebforum topic.
- `thread_count` (int): Number of threads contained in the geowebforum topic.
- `post_count` (int): Number of individual posts contained in the geowebforum topic.
### Table `threads`
- `thread_id` (int, primary key): numeric ID of the geowebforum thread (not linked to geowebforum.ch, but inherent to *geowebforum-scraper*).
- `thread_name` (text): name of the geowebforum thread.
- `thread_url` (text): URL of the geowebforum thread.
- `topic_id` (int, foreign key): numeric ID of the geowebforum topic that contains this thread.
- `post_count` (int): Number of individual posts contained in the geowebforum topic.
### Table `posts`
- `post_id` (int, primary key): numeric ID of the geowebforum post (not linked to geowebforum.ch, but inherent to
- `post_time` (text; SQLite has no datetime format): Timestamp of when the post was made. The timestamp follows the format `%Y-%m-%d %H:%M:00.000`.
- `post_author` (text): Hashed (encrypted) name of the author of the post.
- `post_content` (text): Content of the post *complete with HTML tags*, i.e. `post_content` for example contains link targets.
- `post_text` (text): Same as `post_content` but *with HTML code removed*. `post_text` corresponds to the text you see when you read a post in your browser.
- `post_lang` (text): Most likely language of the post as detected using the Python package `langdetect`. Possible values are `de`, `fr`, `it` and `en` for German, French, Italian and English, respectively. Romansh / Rumantsch cannot be detected by `langdetect`.
- `de` (real): probability in the interval of 0 to 1 of the post being in German.
- `fr` (real): probability in the interval of 0 to 1 of the post being in French.
- `it` (real): probability in the interval of 0 to 1 of the post being in Italian.
- `en` (real): probability in the interval of 0 to 1 of the post being in English.
- `thread_id` (int, foreign key): numeric ID of the geowebforum thread that contains this post.
- `topic_id` (int, foreign key): numeric ID of the geowebforum topic that contains this post.

## Analyses
Once you have scraped the contents of geowebforum.ch into an SQLite database, you can run some further analyses.

The folder `example-analyses` contains the following examples how the data can be queried using any SQLite-compatible database client, such as [DBeaver](https://dbeaver.io):
- [Count-post-languages.sql](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/Count-post-languages.sql)
- [Find-longest-threads.sql](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/Find-longest-threads.sql)
- [Find-posts-per-author.sql](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/Find-posts-per-author.sql) 

The same folder also contains some examples of visualisations of simple content analyses carried out from within [R](https://www.r-project.org) (version 3.5.1):

![e-geo](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/e-geo-per-year--absolute.png "e-geo")
![geoig vs. geoiv](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/geoig-geoiv-per-year--absolute.png "geoig vs. geoiv")
![wfs, wms, wmts](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/wfs-wms-wmts-per-year--absolute.png "wfs, wms, wmts")
![shapefile, interlis, xml, csv (indexed)](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/shapefile-interlis-xml-csv-per-year--indexed.png "shapefile, interlis, xml, csv (indexed)")
![open, smart, 3d](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/open-smart-3d-per-year--absolute.png "open, smart, 3d")
![bim](https://github.com/rastrau/geowebforum-scraper/blob/master/example-analyses/bim-per-year--absolute.png "bim")

## Final notes
This code was written for a private project investigating the Swiss GIS community. It is definitely a bit rough around the edges, doesn't have proper logging or full-fledged exception handling.

Please use this code responsibly.
