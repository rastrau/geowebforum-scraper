class Variables:
    def __init__(self):
        # Path to the resulting database
        self.db_path = 'data.sqlite'
        
        # Topics, saved in the form id: title, url
        self.topics = [
            (0, 'News ueber Produkte und Projekte', 'https://geowebforum.ch/thema.php?themenID=449'),
            (1, 'SOGI-Fachgruppen', 'https://geowebforum.ch/thema.php?themenID=453'),
            (2, 'Veranstaltungen', 'https://geowebforum.ch/thema.php?themenID=425'),
            (3, 'Zeitschriften / Fachmedien', 'https://geowebforum.ch/thema.php?themenID=448'),
            (4, 'Aus- und Weiterbildung', 'https://geowebforum.ch/thema.php?themenID=9'),
            (5, 'Diskussionen zu Geoinformationen', 'https://geowebforum.ch/thema.php?themenID=15'),
            (6, 'Richtlinien und Standards', 'https://geowebforum.ch/thema.php?themenID=7'),
            (7, 'Jobs', 'https://geowebforum.ch/thema.php?themenID=454'),
            (8, 'Geodaten, Geodienste und Infrastruktur', 'https://geowebforum.ch/thema.php?themenID=2'),
            (9, 'Rechtliche Grundlagen', 'https://geowebforum.ch/thema.php?themenID=8'),
            (10, 'Nationale Projekte', 'https://geowebforum.ch/thema.php?themenID=428'),
            (11, 'Internationale Projekte', 'https://geowebforum.ch/thema.php?themenID=429'),
            (12, 'Nutzung des GEOWebforums', 'https://geowebforum.ch/thema.php?themenID=16')
        ]
        
        # Page size in topic pages
        self.offset_step = 10
        
        # Sleep time between HTTP requests
        self.sleep_time = 1

        self.create_tbl_sql = {
            'topics': """ CREATE TABLE topics (
                          topic_id integer PRIMARY KEY,
                          topic_name text NOT NULL,
                          topic_url text NOT NULL,
                          thread_count integer,
                          post_count integer); """,
            'threads': """ CREATE TABLE threads (
                          thread_id integer PRIMARY KEY,
                          thread_name text,
                          thread_url text NOT NULL,
                          topic_id integer NOT NULL,
                          post_count integer, 
                          FOREIGN KEY (topic_id) REFERENCES topics(topic_id)); """,
            'posts':  """ CREATE TABLE posts (
                          post_id integer PRIMARY KEY,
                          post_time text,
                          post_author text,
                          post_content text NOT NULL,
                          post_text text NOT NULL,
                          post_language text NOT NULL,
                          post_de real NOT NULL, 
                          post_fr real NOT NULL, 
                          post_it real NOT NULL, 
                          post_en real NOT NULL,
                          thread_id integer NOT NULL,
                          topic_id integer NOT NULL,
                          FOREIGN KEY (thread_id) REFERENCES threads(thread_id),
                          FOREIGN KEY (topic_id) REFERENCES topics(topic_id)); """,
            'metadata':  """ CREATE TABLE metadata (
                          last_updated text,
                          comments text); """   
        }
        
        self.threads_pickle_file = 'threads.pickle'
        
        
        
