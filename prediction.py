import configparser
import psycopg2
from sql_queries import prediction_data
import csv
import boto3
from io import StringIO



def generate_churn_predictor(cur, conn, churnDate):
    prediction_data(churnDate, preInterval = 3, churnEvaluationPeriod = 1)

def predict(churnDate):
    




def main():
    config = configparser.ConfigParser()
    config.read('C:\Files and Folders\project\dwh.cfg')

    conn = psycopg2.connect("host={} dbname={} user={} password={} port={}".format(*config['CLUSTER'].values()))
    cur = conn.cursor()
    
    generate_churn_predictor(cur,conn)

    conn.close()


if __name__ == "__main__":
    main(