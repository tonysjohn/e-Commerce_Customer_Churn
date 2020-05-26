## Introduction
The objective of this project is to implement a end-to-end machine learning project to predict customer churn in online e-commerce from user interaction logs. Identifying user churn is a very important data science application in e-Commerce and many other industries since it is much more cost-effective to retain an existing customer than to acquire a new customer. Churn rates are also used by industry to evaluate various other metrices like Customer Life Time value, Customer Satisfaction Index, Net Promoter Score etc. 

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

__create_tables.py__ is used to create the necessary tables in Amazon Redshift database.
1. Create staging tables for events and products.
2. Create Events and Products and Time tables for final datastore after data cleaning.  


__etl.py__ file is used to implement the ETL process
1. __Product Metadata__ files from Amazon S3 data store are fed to __staging_products__ table in AWS Redshift database using COPY command. The data is thereafter cleaned and type casted to proper columns in __Products__ tables.
2. __User Activity log__ files from Amazon S3 data store are fed to __staging_events__ table in AWS Redshift database using COPY command. The data is thereafter cleaned and type casted to proper columns in __Events__ and __Time__ tables.
3. __trainingChurn__ table is created using data aggregation of __Events__ and __Product__ tables on a user level. This table is contains a labeled dataset for churned users(Current Project) and user purchases(Future project). The query is parameterized to control the _Churn evaluation date_ and _evalation time period_. The table also contains new features engineered from the user activity and user purchases during the _parameterized timeframe_.
4. __predictionChurn__ table provides churn prediction for future months in a rolling basis. It provides an important basis for evalution of the model in production enviornment. (Note: Solutioning pending....)

![ETL](/images/ETL.PNG)

Required SQL queries are saved in sql_queries.py file.

## Defining Churn and Feature Engineering

The first step before modeling the data is to define churn in a meaningful way w.r.t. business requirement. Here we have defined that teh users have churned if _the user who had any activity within a stipulated period of prior months but have no activity within the evaluation month/months_. The definition of churn can vary based on the evaluation timeframe and therefore the time periods have to be parameterized inorder to accomadate changing business requirement. __Note: As a default, prior months is taken as 3 months and the churn evaluation timeperiod is taken as 1 month__

The second step is to engineer relevant features to address the prediction problem at hand. The raw event logs provides transactions snippets of information about the customer preferences and activity within the site. For the _churn problem_, I have envision three major types of features.

1. __Basic Activity features__ :  These features are created from aggregating user activity for the last stipulated period of time(say 3 months). These features captures the activity of the user during a certain period of time and therefore can help in distinguishing loyal and active users from rest. This involves data about the number of visits, number of purchases, total purchase amount etc.

Find below the complete list of features (Note: All features are created for a stipulated time):
- nb_visits : Number of user activity
- nb_purchase : Number of user purchases
- amount_purchase : Amount purchased
- nb_products_seen : Number of products seen by user
- nb__distinct_products : number of distinct products seen by user
- nb_distinct_category0 : number of distinct categories seen by user
- nb_distinct_category1 : number of distinct sub-categories seen by user 
- nb_distinct_category2 : number of distinct sub-categories seen by user
- nb_distinct_product_purchased : number of distinct products purchased by user 
- nb_distinct_category_purchased : number of distinct categories purchased by user 

2. __Trend Activity features__ :  These features are created from aggregating user activity for the most recent time period(say 1 months). These features capture the trend of user activity in the recent past. This involves data about the number of visits, number of purchases, total purchase amount etc.

Find below the complete list of features (Note: All features are for most recent period):
- nb_visits : Number of user activity
- nb_purchase : Number of user purchases
- amount_purchase : Amount purchased
- nb_products_seen : Number of products seen by user
- nb__distinct_products : number of distinct products seen by user
- nb_distinct_category0 : number of distinct categories seen by user
- nb_distinct_category1 : number of distinct sub-categories seen by user 
- nb_distinct_category2 : number of distinct sub-categories seen by user
- nb_distinct_product_purchased : number of distinct products purchased by user 
- nb_distinct_category_purchased : number of distinct categories purchased by user 


3. __Global Activity features__ : These features are created from aggregating user activity for the entire association with the website. It captures the overall activity of the user from the start.

Find below the complete list of features:
- nb_associated_months : Number of months between first activity and Evaluation date
- nb_days_last_activity : Number of days from last activity
- nb_days_last_purchase : Number of days from last puchase
- nb_active_months : Number of months with active vists to site
- nb_active_purchase_months : Number of months with purchases in site
- nb_purchase_total : Number of purchases for entire user activity
- amount_purchase_total : Total purchase amount for entire user activity





