import configparser
import psycopg2
from sql_queries import copy_table_queries, insert_table_queries, training_Churn

CHURNDATE = '2014-11-01'


def load_staging_tables(cur, conn):
    for query in copy_table_queries:
        cur.execute(query)
        conn.commit()


def insert_tables(cur, conn):
    for query in insert_table_queries:
        #print(f'Running {query}')
        cur.execute(query)
        conn.commit()

def analysis_tables(cur, conn, churnDate,preInterval = 4, churnEvaluationPeriod = 3):
    query = training_Churn(churnDate, preInterval = preInterval, churnEvaluationPeriod = churnEvaluationPeriod)
    cur.execute(query)
    conn.commit()

def main():
    config = configparser.ConfigParser()
    config.read('C:\Files and Folders\project\dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    #load_staging_tables(cur, conn)
    #insert_tables(cur, conn)
    analysis_tables(cur, conn,CHURNDATE)

    conn.close()


if __name__ == "__main__":
    main()