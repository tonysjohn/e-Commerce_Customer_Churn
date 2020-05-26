## Introduction
The objective of this project is to implement a end-to-end machine learning project to predict customer churn in online e-commerce from user interaction logs. 

The project involves creating of data pipeline to synthesize labels for the purpose of churn identification and developing new features for the raw transactional log. The ingestional pipeline is provisioned using Amazon S3 and Amazon Redshift; the ETL process is orchestrated by python and postgreSQL. The modeling is performed using tree based boosting methods like XgBoost and AdaBoost.

## Project Datasets
#### Product Metadata Dataset
The first dataset is metadata about the products available in the e-commerce website. The file is in csv format and contains metadata about the product main and sub categories and price. The data is assumed to be loaded in Amazon S3 data lake store within approriate folder taxonomy.

Below is an example of the data available in csv format from the 800k record dataset.

| product_id | category_id_0 | category_id_1 | category_id_2 | price |
| --- | --- | --- | --- | --- |
| 0 | 9.0 | 38 | 166 | 20.04 |
| 1 | 5.0 | 37 | 109 | 7.02 |

#### User Activity Log Dataset
The second dataset consists of user activity logs in the website in CSV format. The user interaction is generated when a user visits a "product page", "seller page" or commits a transaction through  a "buy order". The data is assumed to be loaded in Amazon S3 data lake store within approriate folder taxonomy.

Below is an example of the data available in csv format from the 3M record dataset.

| user_id | event_timestamp | event_type | product_id | seller_id |
| --- | --- | --- | --- | --- |
| 53189 | 2014-09-08 22:00:00 | product_page | 399135 | 118464.0 |
| 23481 | 2014-09-08 14:00:00 | seller_page |  | 255.0 |

## Schema for Database
Using the user activity data and product information metadata we can do churn analysis. This includes the following tables.

![Schema Diagram](/images/schema.PNG)

## ETL Process

create_tables.py 

etl.py file is used to implement the ETL process
1. __Song Metadata__ files from Amazon S3 data store are fed to __staging_events__ table in AWS Redshift database using COPY command. The data is thereafter cleaned and type casted to proper columns in __Songs__ and __Artists__ tables.
2. __User Activity log__ files from Amazon S3 data store are fed to __staging_songs__ table in AWS Redshift database using COPY command. The data is thereafter cleaned and type casted to proper columns in __Songplays__, __Users__ and __Time__ tables.

![ETL](/images/ETL.PNG)

Required SQL queries are saved in sql_queries.py file.


