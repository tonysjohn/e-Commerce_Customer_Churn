import configparser


# CONFIG
config = configparser.ConfigParser()
config.read('C:\Files and Folders\project\dwh.cfg')

PRODUCT_DATA = config.get("S3","PRODUCT_DATA")
ARN = config.get("IAM_ROLE","ARN")
EVENTS_DATA = config.get("S3","EVENTS_DATA")
PREDICTION_DATA = config.get("S3","PREDICTION_DATA")

# DROP TABLES

staging_events_table_drop = "DROP TABLE IF EXISTS staging_events"
staging_product_table_drop = "DROP TABLE IF EXISTS staging_products"
product_table_drop = "DROP TABLE IF EXISTS products"
event_table_drop = "DROP TABLE IF EXISTS events"
completeEvents_table_drop = "DROP TABLE IF EXISTS completeEvents"
#artist_table_drop = "DROP TABLE IF EXISTS artists"
time_table_drop = "DROP TABLE IF EXISTS time"

# CREATE TABLES


## Staging Events
#user_id,event_timestamp,event_type,product_id,seller_id

staging_events_table_create= """CREATE TABLE IF NOT EXISTS staging_events
                                 (
                                 user_id TEXT,
                                 event_timestamp TIMESTAMP,
                                 event_type TEXT,
                                 product_id TEXT,
                                 seller_id TEXT
                                 )                                                                
"""

## Staging Products
#product_id,category_id_0,category_id_1,category_id_2,price

staging_products_table_create = """CREATE TABLE IF NOT EXISTS staging_products
                                 (product_id TEXT,
                                 category_id_0 TEXT,
                                 category_id_1 TEXT,
                                 category_id_2 TEXT,
                                 price TEXT)
"""

## Events Table
#event_id, user_id,event_timestamp,event_type,product_id,seller_id

events_table_create= """CREATE TABLE IF NOT EXISTS events
                                 (
                                 event_id INTEGER IDENTITY(0,1) NOT NULL PRIMARY KEY,
                                 user_id INTEGER DISTKEY,
                                 event_timestamp TIMESTAMP NOT NULL SORTKEY,
                                 event_type TEXT,
                                 product_id INTEGER,
                                 seller_id INTEGER
                                 )                                                                
"""

## Products Table
#product_id,category_id_0,category_id_1,category_id_2,price

products_table_create = """CREATE TABLE IF NOT EXISTS products
                                 (product_id INTEGER NOT NULL PRIMARY KEY,
                                 category_id_0 INTEGER,
                                 category_id_1 INTEGER,
                                 category_id_2 INTEGER,
                                 price DOUBLE PRECISION)
"""


user_analysis_table = """CREATE TABLE IF NOT EXISTS user_analysis
                                   (user_id INTEGER PRIMARY_KEY,
                                   first_activity_date DATE,
                                   first_purchase_date DATE,
                                   last_activity_date DATE,
                                   last_purchase_date DATE,
                                   total_purchase DOUBLE,
                                   total_visit INTEGER
                                   )
"""

user_activity_table = """CREATE TABLE IF NOT EXISTS vw_user_activity
                                   (user_id INTEGER PRIMARY_KEY,

                                   average_activity_breaks DOUBLE
                                   )
"""



songplay_table_create = ("""CREATE TABLE IF NOT EXISTS songplays(songplay_id INTEGER IDENTITY(0,1) NOT NULL PRIMARY KEY
                                                                   , start_time TIMESTAMP NOT NULL SORTKEY
                                                                   , user_id INTEGER NOT NULL DISTKEY
                                                                   , level VARCHAR(10)
                                                                   , song_id VARCHAR(50)
                                                                   , artist_id VARCHAR(50)
                                                                   , session_id INTEGER
                                                                   , location TEXT
                                                                   , user_agent TEXT);
""")

user_table_create = (""" CREATE TABLE IF NOT EXISTS users(user_id int NOT NULL PRIMARY KEY
                                           , first_name VARCHAR(100)
                                           , last_name VARCHAR(100)
                                           , gender CHAR
                                           , level VARCHAR(10) NOT NULL);
""")

song_table_create = (""" CREATE TABLE IF NOT EXISTS songs(song_id VARCHAR(50) NOT NULL PRIMARY KEY
                                           , title TEXT
                                           , artist_id VARCHAR(50)
                                           , year INTEGER
                                           , duration INTEGER);
""")

artist_table_create = (""" CREATE TABLE IF NOT EXISTS artists(artist_id VARCHAR(50) NOT NULL PRIMARY KEY
                                              , name TEXT
                                              , location TEXT
                                              , latitude DOUBLE PRECISION
                                              , longitude DOUBLE PRECISION);
""")

time_table_create = (""" CREATE TABLE IF NOT EXISTS time(event_timestamp TIMESTAMP NOT NULL PRIMARY KEY
                                           , hour INTEGER
                                           , day INTEGER
                                           , week INTEGER
                                           , month INTEGER
                                           , year INTEGER
                                           , weekday INTEGER);
""")

# STAGING TABLES

staging_events_copy = ("""COPY staging_events FROM {}
                          CREDENTIALS 'aws_iam_role={}'
                          region 'us-east-1'
                          delimiter ',' gzip
                          IGNOREHEADER 1
                          dateformat 'auto'
""").format(EVENTS_DATA, ARN)
staging_products_copy = ("""COPY staging_products FROM {}
                         CREDENTIALS 'aws_iam_role={}'
                         region 'us-east-1'
                         delimiter ',' gzip
                         IGNOREHEADER 1
""").format(PRODUCT_DATA, ARN)

# FINAL TABLES

def prediction_data(finalChurnDate, preInterval = 3, churnEvaluationPeriod = 1):
       query = training_Churn(finalChurnDate = finalChurnDate, preInterval = preInterval, churnEvaluationPeriod = churnEvaluationPeriod)
       prediction_data = ("""unload ('{}')
                            to '{}+/ChurnData_{}'
                            iam_role '{}'
                            format csv
                            delimiter ','
                            GZIP
                            parallel off""").format(query,PREDICTION_DATA, finalChurnDate, ARN)

events_table_insert = ("""INSERT INTO events
                                 (
                                 user_id,
                                 event_timestamp,
                                 event_type,
                                 product_id,
                                 seller_id
                                 ) 
                            SELECT user_id::numeric::int,
                                 event_timestamp,
                                 event_type,
                                 CASE WHEN product_id <> '' THEN
                                   product_id::numeric::int
                                 ELSE NULL END,
                                 seller_id::numeric::int                             
                            FROM staging_events
                            WHERE event_timestamp is NOT NULL
""")

products_table_insert = ("""INSERT INTO products
                                 (
                                 product_id,
                                 category_id_0,
                                 category_id_1,
                                 category_id_2,
                                 price
                                 ) 
                            SELECT product_id::numeric::int,
                                 CASE WHEN category_id_0 <> '' THEN
                                   category_id_0::numeric::int
                                 ELSE NULL END,
                                 category_id_1::numeric::int,
                                 category_id_2::numeric::int,
                                 CASE WHEN price <> '' THEN
                                   price::numeric
                                 ELSE NULL END                              
                            FROM staging_products
""")

user_table_insert = ("""DELETE FROM users
                        WHERE user_id in (SELECT DISTINCT userId FROM staging_events);
                        
                        INSERT INTO users(user_id
                                           , first_name
                                           , last_name
                                           , gender
                                           , level)
                                    SELECT userId
                                           , firstName
                                           , lastName
                                           , gender
                                           , level
                                    FROM(
                                    SELECT userId
                                           , firstName
                                           , lastName
                                           , gender
                                           , level
                                           , ROW_NUMBER() OVER(PARTITION BY userid ORDER BY ts DESC) as row
                                    FROM staging_events e
                                    WHERE page = 'NextSong') c
                                    WHERE c.row = 1;
""")

song_table_insert = ("""DELETE FROM songs
                        WHERE song_id in (SELECT DISTINCT song_id FROM staging_songs);
                        
                        INSERT INTO songs(song_id
                                        , title
                                        , artist_id
                                        , year
                                        , duration)
                                    SELECT DISTINCT song_id
                                        , title
                                        , artist_id
                                        , year
                                        , duration
                                    FROM staging_songs;
""")

artist_table_insert = ("""DELETE FROM artists
                        WHERE artist_id in (SELECT DISTINCT artist_id FROM staging_songs);
                        INSERT INTO artists(artist_id
                                              , name
                                              , location
                                              , latitude
                                              , longitude)
                                      SELECT DISTINCT artist_id
                                              , artist_name
                                              , artist_location
                                              , artist_latitude
                                              , artist_longitude
                                      FROM staging_songs
""")

time_table_insert = ("""INSERT INTO time(event_timestamp
                                           , hour
                                           , day
                                           , week
                                           , month
                                           , year
                                           , weekday)
                                      SELECT DISTINCT event_timestamp
                                           , EXTRACT(HOUR FROM event_timestamp)
                                           , EXTRACT(DAY FROM event_timestamp)
                                           , EXTRACT(WEEK FROM event_timestamp)
                                           , EXTRACT(MONTH FROM event_timestamp)
                                           , EXTRACT(YEAR FROM event_timestamp)
                                           , EXTRACT(DOW FROM event_timestamp)
                                     FROM staging_events
                                     WHERE event_timestamp is NOT NULL
""")

def training_Churn(finalChurnDate, preInterval = 3, churnEvaluationPeriod = 1):

       query = f"""
       DROP TABLE IF EXISTS trainingChurn;

       SELECT 
              all_activity.user_id,
              nb_visits,
              NVL(nb_purchase,0) as nb_purchase,
              NVL(amount_purchase,0) as amount_purchase,
              nb_products_seen,
              nb__distinct_products,
              nb_distinct_category0,
              nb_distinct_category1,
              nb_distinct_category2,
              NVL(nb_distinct_product_purchased,0) as nb_distinct_product_purchased,
              NVL(nb_distinct_category_purchased,0) as nb_distinct_category_purchased,
              NVL(nb_visits_last_month,0) as nb_visits_last_month,
              NVL(nb_purchase_last_month,0) as nb_purchase_last_month,
              NVL(amount_purchase_last_month,0) as amount_purchase_last_month,
              NVL(nb_products_seen_last_month,0) as nb_products_seen_last_month,
              NVL(nb__distinct_products_last_month,0) as nb__distinct_products_last_month,
              NVL(nb_distinct_category0_last_month,0) as nb_distinct_category0_last_month,
              NVL(nb_distinct_category1_last_month,0) as nb_distinct_category1_last_month,
              NVL(nb_distinct_category2_last_month,0) as nb_distinct_category2_last_month,
              NVL(nb_distinct_product_purchased_last_month,0) as nb_distinct_product_purchased_last_month,
              NVL(nb_distinct_category_purchased_last_month,0) as nb_distinct_category_purchased_last_month,
              DATEDIFF(month, first_activity_date,last_activity_date) as nb_associated_months,
              DATEDIFF(day, last_activity_date, TIMESTAMP '{finalChurnDate}'- INTERVAL '{churnEvaluationPeriod} months') as nb_days_last_activity,
              NVL(DATEDIFF(day, last_purchase_date, TIMESTAMP '{finalChurnDate}'- INTERVAL '{churnEvaluationPeriod} months'),99999) as nb_days_last_purchase,
              nb_active_months,
              nb_active_purchase_months,
              nb_purchase_total,
              NVL(amount_purchase_total,0) as amount_purchase_total,
              CASE WHEN current_month.user_id IS NULL THEN 1 ELSE 0 END as no_activity_evaluation_period,
              NVL(current_month_purchase,0) as amount_purchase_evaluation_period,
              CASE WHEN current_month_purchase > 0 THEN 0 ELSE 1 END as no_purchase_evaluation_period
       INTO trainingChurn
       FROM
       (SELECT 
              user_id,
              COUNT(event_id) as nb_visits,
              SUM((event_type = 'buy_order')::int) as nb_purchase,
              SUM(price::numeric * (event_type = 'buy_order')::int) amount_purchase,
              COUNT(products.product_id) as nb_products_seen,
              COUNT(DISTINCT products.product_id) as nb__distinct_products,
              COUNT(DISTINCT products.category_id_0) as nb_distinct_category0,
              COUNT(DISTINCT products.category_id_1) as nb_distinct_category1,
              COUNT(DISTINCT products.category_id_2) as nb_distinct_category2,
              COUNT(DISTINCT CASE WHEN event_type = 'buy_order' THEN products.product_id END) as nb_distinct_product_purchased,
              COUNT(DISTINCT CASE WHEN event_type = 'buy_order' THEN products.category_id_0 END) as nb_distinct_category_purchased
              FROM events LEFT JOIN products ON events.product_id = products.product_id INNER JOIN time on events.event_timestamp = time.event_timestamp
              WHERE events.event_timestamp <  TIMESTAMP '{finalChurnDate}'
                                   - INTERVAL '{churnEvaluationPeriod} months'
              AND events.event_timestamp >= TIMESTAMP '{finalChurnDate}'
                                   - INTERVAL '{churnEvaluationPeriod} months'
                                   - INTERVAL '{preInterval} months'
              GROUP BY user_id
              HAVING amount_purchase > 35) all_activity
       LEFT JOIN
       (SELECT 
              user_id,
              COUNT(event_id) as nb_visits_last_month,
              SUM((event_type = 'buy_order')::int) as nb_purchase_last_month,
              SUM(price::numeric * (event_type = 'buy_order')::int) amount_purchase_last_month,
              COUNT(products.product_id) as nb_products_seen_last_month,
              COUNT(DISTINCT products.product_id) as nb__distinct_products_last_month,
              COUNT(DISTINCT products.category_id_0) as nb_distinct_category0_last_month,
              COUNT(DISTINCT products.category_id_1) as nb_distinct_category1_last_month,
              COUNT(DISTINCT products.category_id_2) as nb_distinct_category2_last_month,
              COUNT(DISTINCT CASE WHEN event_type = 'buy_order' THEN products.product_id END) as nb_distinct_product_purchased_last_month,
              COUNT(DISTINCT CASE WHEN event_type = 'buy_order' THEN products.category_id_0 END) as nb_distinct_category_purchased_last_month
              FROM events LEFT JOIN products ON events.product_id = products.product_id INNER JOIN time on events.event_timestamp = time.event_timestamp
              WHERE events.event_timestamp <  TIMESTAMP '{finalChurnDate}'
                                   - INTERVAL '{churnEvaluationPeriod} months'
              AND events.event_timestamp >= TIMESTAMP '{finalChurnDate}'
                                   - INTERVAL '{churnEvaluationPeriod} months'
                                   - INTERVAL '1 months'
              GROUP BY user_id
              ) last_month ON all_activity.user_id = last_month.user_id
       INNER JOIN
       (SELECT DISTINCT
              user_id,
              MIN(events.event_timestamp::date) as first_activity_date,
              MIN(CASE WHEN event_type = 'buy_order' THEN events.event_timestamp::date END) as first_purchase_date,
                     MAX(events.event_timestamp::date) as last_activity_date,
              MAX(CASE WHEN event_type = 'buy_order' THEN events.event_timestamp::date END) as last_purchase_date,
                     COUNT(DISTINCT month::text+year::text) as nb_active_months,
              COUNT(DISTINCT CASE WHEN event_type = 'buy_order' THEN month::text+year::text END) as nb_active_purchase_months,
                     SUM((event_type = 'buy_order')::int) as nb_purchase_total,
              SUM(price::numeric * (event_type = 'buy_order')::int) amount_purchase_total
              FROM events LEFT JOIN products ON events.product_id = products.product_id INNER JOIN time on events.event_timestamp = time.event_timestamp
              WHERE events.event_timestamp <  TIMESTAMP '{finalChurnDate}'
                                   - INTERVAL '{churnEvaluationPeriod} months'
              GROUP BY user_id) global ON all_activity.user_id = global.user_id
       LEFT JOIN
       (SELECT DISTINCT
              user_id,
              sum((event_type = 'buy_order')::int) as current_month_purchase
              FROM events
              WHERE events.event_timestamp >=  TIMESTAMP '{finalChurnDate}'
                                   - INTERVAL '{churnEvaluationPeriod} months'
              and events.event_timestamp <  TIMESTAMP '{finalChurnDate}'
              GROUP BY user_id
       ) current_month ON current_month.user_id = all_activity.user_id;
       """
       return query


# QUERY LISTS

create_table_queries = [staging_events_table_create, staging_products_table_create,products_table_create,events_table_create,time_table_create]
drop_table_queries = [staging_events_table_drop, staging_product_table_drop,product_table_drop,event_table_drop,time_table_drop]
copy_table_queries = [staging_events_copy, staging_products_copy]
insert_table_queries = [events_table_insert, products_table_insert,time_table_insert]

