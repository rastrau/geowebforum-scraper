# -*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import variables
import sqlite3
import datetime
import time
import langdetect
import hashlib
import pickle
from unidecode import unidecode


vars = variables.Variables()
topics = vars.topics

def connect_db(db_path = vars.db_path):
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    return connection, cursor

def create_tbl(cursor, name):
    cursor.execute(""" DROP TABLE IF EXISTS %s """ % name)
    cursor.execute(vars.create_tbl_sql[name])
    return

def parse_timestamp(ts):
    ts = ts.replace('Januar', 'January').replace('Februar', 'February')
    ts = ts.replace(u'März', 'March').replace('Mai', 'May')
    ts = ts.replace('Juni', 'June').replace('Juli', 'July')
    ts = ts.replace('Oktober', 'October').replace('Dezember', 'December')
    ts = datetime.datetime.strptime(ts, "%d.  %B  %y (%H:%M Uhr)")
    return datetime.datetime.strftime(ts, "%Y-%m-%d %H:%M:00.000")

def setup_triggers(cursor):
    cursor.execute(""" CREATE TRIGGER update_thread_count_topics INSERT ON threads
                       BEGIN
                       UPDATE topics SET thread_count = (SELECT COUNT FROM
                       (SELECT topic_id, COUNT(*) as COUNT from threads WHERE
                       topics.topic_id = threads.topic_id GROUP BY topic_id));
                       END; """)
    cursor.execute(""" CREATE TRIGGER update_post_count_topics INSERT ON posts
                       BEGIN
                       UPDATE topics SET post_count = (SELECT COUNT FROM
                       (SELECT topic_id, COUNT(*) as COUNT from posts WHERE
                       topics.topic_id = posts.topic_id GROUP BY topic_id));
                       END; """)
    cursor.execute(""" CREATE TRIGGER update_post_count_threads INSERT ON posts
                       BEGIN
                       UPDATE threads SET post_count = (SELECT COUNT FROM
                       (SELECT thread_id, COUNT(*) as COUNT from posts WHERE
                       threads.thread_id = posts.thread_id GROUP BY thread_id));
                       END; """)
    return


def ingest_topics(cursor, topics = vars.topics):
    for (topic_id, topic_name, topic_url) in topics:
        cursor.execute("INSERT INTO topics VALUES (?, ?, ?, ?, ?)",
                       [topic_id, topic_name, topic_url, 0, 0])
    return topics

def ingest_thread(cursor, thread_id, thread_name, thread_url, topic_id):
    cursor.execute("INSERT INTO threads VALUES (?, ?, ?, ?, ?)",
                   [thread_id, thread_name, thread_url, topic_id, 0])
    return

def detect_languages(post_text):
    try:
        langs = detect_langs(post_text)
        lang_dict = dict()
        for lang in langs:
            lang = lang.__repr__()
            lang_dict[lang.split(':')[0]] = float(lang.split(':')[1])
    except:
        lang_dict = dict()

    # Romansh (Rumantsch) cannot be detected by langdetect
    de = lang_dict.get('de', 0)
    fr = lang_dict.get('fr', 0)
    it = lang_dict.get('it', 0)
    en = lang_dict.get('en', 0)
    lang = 'unclassified'
    lang_loading = 0
    if de > lang_loading:
        lang = 'de'
        lang_loading = de
    if fr > lang_loading:
        lang = 'fr'
        lang_loading = fr
    if it > lang_loading:
        lang = 'it'
        lang_loading = it
    if en > lang_loading:
        lang = 'en'
    return lang, de, fr, it, en

def ingest_post(cursor, post_id, post_time, post_author, post_content,
                post_text, post_language, de, fr, it, en, thread_id,
                topic_id):
    cursor.execute("INSERT INTO posts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   [post_id, post_time, post_author, unicode(post_content),
                    post_text, post_language, de, fr, it, en, thread_id, topic_id])
    return

def write_metadata(cursor, comments=''):
    now = datetime.datetime.now()
    now = datetime.datetime.strftime(now, "%Y-%m-%d %H:%M")
    cursor.execute("INSERT INTO metadata VALUES (?, ?)", [now, comments])


from langdetect import detect_langs

connection, cursor = connect_db()

# Set up tables, and triggers to add counts to the various tables
create_tbl(cursor, 'posts')
create_tbl(cursor, 'threads')
create_tbl(cursor, 'topics')
create_tbl(cursor, 'metadata')
setup_triggers(cursor)
connection.commit()

# Load topics into DB
topics = ingest_topics(cursor)

# Collect threads
all_threads = []
thread_id = 1
for topic_id in range(0, len(topics)):

    topic_title = topics[topic_id][1]
    topic_url = topics[topic_id][2]

    print '\nWorking on topic "%s"...' % topic_title
    success = True

    offset = 0
    while(success):
        time.sleep(vars.sleep_time)
        print '\n  Parsing URL with offset %s: %s&offset=%s...' % (offset,
                                                                   topic_url,
                                                                   offset)
        try:
            page = urllib2.urlopen('%s&offset=%s' % (topic_url, offset))
        except (urllib2.HTTPError, urllib2.URLError) as e:
            print e.code
            success = False

        soup = BeautifulSoup(page, 'lxml')
        thread_links = soup.find_all('a', {'class': ['threadtitle']})
        print '  Found %s threads.' % len(thread_links)

        # Even when using too big an offset, geowebforum doesn't return an HTTP
        # error but an empty-ish page
        if len(thread_links) == 0:
            # We increased offset too much and found an empty page only
            success = False
        else:
            for thread_link in thread_links:
                #thread_id = thread_link['href'].split('threadID=')[1]
                thread_name = thread_link.string
                thread_url = 'https://geowebforum.ch/%s' % thread_link['href']

                # Store the thread information
                all_threads.append((thread_id, thread_name, thread_url,
                                    topic_id))
                ingest_thread(cursor, thread_id, thread_name, thread_url,
                              topic_id)

                thread_id += 1

        offset += vars.offset_step

connection.commit()

# Store the data as pickle file
with open(vars.threads_pickle_file, 'wb') as f:
    pickle.dump(all_threads, f)

# Collect posts
all_posts = []
post_id = 1
for (thread_id, thread_name, thread_url, topic_id) in all_threads:
    time.sleep(vars.sleep_time)

    print ''
    success = True
    offset = 0
    while(success):
        time.sleep(vars.sleep_time)
        print 'Parsing thread %s with offset %s: %s&offset=%s...' % (thread_id,
                                                                     offset,
                                                                     thread_url,
                                                                     offset)
        try:
            thread_page = urllib2.urlopen('%s&offset=%s' % (thread_url, offset))
        except (urllib2.HTTPError, urllib2.URLError) as e:
            print e.code
            success = False

        thread_soup = BeautifulSoup(thread_page, 'lxml')
        posts = thread_soup.find_all('div', {'class': ['visible']})

        # Even when using too big an offset, geowebforum doesn't return an HTTP
        # error but an empty-ish page
        if len(posts) == 0:
            # We increased offset too much and found an empty page only
            success = False
            print '  Found no more posts.'
        else:
            print '  Parsing %s post(s)...' % (len(posts)/2)
            for i in range(0, len(posts), 2):
                # Find the author and the timestamp of this post
                post_author = ''
                authorship_div = posts[i]
                for match in authorship_div.findAll('span'):
                    match.unwrap()
                for line in authorship_div.text.split('\n'):
                    line = line.strip()
                    if line != '':
                        if 'Beitragsnummer' in line:
                            post_time = line.split('Beitragsnummer: ')[0]
                        else:
                            post_author = line

                post_time = parse_timestamp(post_time)

                content_div = posts[i+1]
                post_content = content_div
                post_text = content_div.text.strip()
                post_language, de, fr, it, en = detect_languages(post_text)

                if isinstance(post_author, unicode):
                    post_author = hashlib.sha256(unidecode(post_author)).hexdigest()
                elif isinstance(post_author, str):
                    post_author = hashlib.sha256(post_author).hexdigest()

                # Collect posts in a list. Because pagination is broken on some
                # geowebforum pages, there are threads where certain posts appear
                # on two pages. We can consolidate this list before transferring
                # the data into the DB in order to solve this issue
                all_posts.append((post_id, post_time, post_author, post_content,
                                  post_text, post_language, de, fr, it, en, thread_id, topic_id))

                post_id += 1

        offset += vars.offset_step

# Make the posts unique. Necessity of this: see above comment.
all_posts = list(set(all_posts))

for (post_id, post_time, post_author, post_content, post_text, post_language, de,
     fr, it, en, thread_id, topic_id) in all_posts:
    ingest_post(cursor, post_id, post_time, post_author, post_content, post_text,
                post_language, de, fr, it, en, thread_id, topic_id)

write_metadata(cursor)

connection.commit()
connection.close()
