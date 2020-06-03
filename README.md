## Introduction
The objective of this project is to implement a end-to-end machine learning project to predict customer churn in online e-commerce from user interaction logs. Identifying user churn is a very important data science application in e-Commerce and many other industries since it is much more cost-effective to retain an existing customer than to acquire a new customer. Churn rates are also used by industry to evaluate various other metrices like Customer Life Time value, Customer Satisfaction Index, Net Promoter Score etc. 

The project involves creating of data pipeline to synthesize labels for the purpose of churn identification and developing new features for the raw transactional log. The ingestional pipeline is provisioned using Amazon S3 and Amazon Redshift; the ETL process is orchestrated by python and postgreSQL. The modeling is performed using tree based boosting methods like XgBoost and AdaBoost.

## Project Diagram

![E2E process](/images/E2Eprocess.PNG)

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
4. __predictionChurn__ table provides churn prediction for future months in a rolling basis. It provides an important basis for evalution of the model in production enviornment. _(Note: Solutioning pending....)_

![ETL](/images/ETL.PNG)

Required SQL queries are saved in sql_queries.py file.

## Defining Churn and Feature Engineering

The __first step__ before modeling the data is to define churn in a meaningful way w.r.t. business requirement. Here we have defined that teh users have churned if 
_"the user who had minimum purchase activity within a stipulated period of prior months but have no activity within the evaluation month/months"_.
The definition of churn can vary based on the evaluation timeframe and therefore the time periods have to be parameterized inorder to accomadate changing business requirement. __Note: As a default, prior months is taken as 4 months and the churn evaluation timeperiod is taken as 3 month__

The __second step__ is to engineer relevant features to address the prediction problem at hand. The raw event logs provides transactions snippets of information about the customer preferences and activity within the site. For the _churn problem_, I have envision three major types of features.

1. __Basic Activity features__ :  These features are created from aggregating user activity for the last stipulated period of time(say 4 months). These features captures the activity of the user during a certain period of time and therefore can help in distinguishing loyal and active users from rest. This involves data about the number of visits, number of purchases, total purchase amount etc.

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

The features are same as the __Basic Activity Features__ but with a limited scope.

3. __Global Activity features__ : These features are created from aggregating user activity for the entire association with the website. It captures the overall activity of the user from the start.

Find below the complete list of features:
- nb_associated_months : Number of months between first activity and Evaluation date
- nb_days_last_activity : Number of days from last activity
- nb_days_last_purchase : Number of days from last puchase
- nb_active_months : Number of months with active vists to site
- nb_active_purchase_months : Number of months with purchases in site
- nb_purchase_total : Number of purchases for entire user activity
- amount_purchase_total : Total purchase amount for entire user activity

## Exploratory Data Analysis
#### Handling Missing Value
The training dataset has high degree of missing value due to its design. For e.g., if there is no user activity in the most recent month, the trend features will not have any data. Understanding this reason for missing values gives as insight into how to impute the value.
- For number/purchase amount features with missing value, the most probable reason is no activity/ no purchase during the stipulated time.
- nb_days_last_purchase will be missing for users who never purchased from the site, we can impute this vare with a very high value(say 99999) to categories these users differently from rest.

#### Feature correlation
Some features can be highly correlated with each other causing instability while building predictive model. Correlations can be visualized using correlation plots as given below.

![Correlation plot](/images/correlation.PNG)

As seen in the correlation matrix above, there is higher correlation between features of basic category and trend category. Also, number of days from last activity and purchase is found to be negatively correlated with all the features. Intuitively, an active users has more visits/ purchases and will have lower number of days from last visit.

#### Class Balance
Class imbalance in the dataset can create issues in while modeling the data. The current dataset appears to be fairly balanced.

![Churn Distribution plot](/images/ChurnDistribution.PNG)

#### Feature Importance

Since the categorical output, correlation matrix provides limited information about the actual correlation. A __t-test__ can be performed to ascertain if there is significant difference in data from churn and not-churn users. The following features showed < 0.05% significance. Log transformed data show sigficance, indicating log transformation required for linear - parameteric models

| Var1 | Var2 | tvalue | pvalue |
| --- | --- | --- | --- |
| amount_purchase | no_activity_evaluation_period | 1.598413 | 0.109958 |
| amount_purchase_last_month | no_activity_evaluation_period | 1.004236 | 0.315270 |
| nb_purchase_total | no_activity_evaluation_period | 1.544840 | 0.122392 |
| amount_purchase_total | no_activity_evaluation_period | 1.618743 | 0.105510 |

__Box Plots__ provides a nice visual representation of difference in distribution between two groups

![Box plot](/images/boxplot.PNG)

__Tree Based models__ provides feature importance which can be potentially used to filter non informative feature. Find below the top 10 feature importance from __Random Forest__ model in the decreasing order 

| Features | Importance|
| --- | --- |
| nb_active_months | 0.177715 |
| nb_days_last_activity | 0.121025 |
| nb_visits | 0.102029 |
| nb_distinct_category1 | 0.058217 |
| nb_days_last_purchase | 0.05582 |
| nb__distinct_products | 0.05526 |
| amount_purchase | 0.054337 |
| amount_purchase_total | 0.046802 |
| nb_products_seen | 0.036346 |
| nb_associated_months | 0.035496 |

## Modeling
#### Logistic Regression Model
A vanilla logistic regression model is found to perform poorly on the data. This is as expected due to the strong assumptions behind a linear model. As seen in EDA, we need to perform feature transformations and analyze interactions in data to properly tune the model. _(Note: Solutioning pending....)_

#### Tree Based Models
Tree based models like Random Forest and Tree based boosting models like AdaBoost, XgBoost is found to be much better than logistic model.

#### Hyperparameter Tuning
Hyperparameter tuning is performed using 5-fold Cross Validation. Note: Only Adaboost model hyperparameters have been tuned 

#### Results
The XgBoost model is found to have the highest accuracy of 80.85% and high recall of 86.62% on test dataset. 

| Model | TN | FP | FN | TP | Accuracy | Recall | Precision | AUC |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | 
| Logistic Regression | 246 | 101 | 55 | 371 | 79.82% | 87.09% | 78.60% | 0.79 |
| Random Forest | 261 | 86 | 63 | 363 | 80.72% | 85.21% | 80.85% | 0.80 | 
| Adaboost | 260 | 87 | 78 | 348 | 78.65% | 81.69% | 80.00% | 0.78 |
| XgBoost | 256 | 91 | 57 | 369 | 80.85% | 86.62% | 80.22% | 0.80 |



## Deployment and Evaluation
prediction.py is used to orchestrate monthly prediction in rolling basis. The ML model and necessary configuration are envisoned to be pickled and put in Amazon S3 datastore from which the model can be called when required. _(Note: Solutioning pending....)_


