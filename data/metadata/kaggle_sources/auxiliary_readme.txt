## Project Title: 
### BNPL Credit Risk Analysis and Default Prediction

## Project Objective: 
### Analyze user default behavior in BNPL services and build predictive models for credit risk management.

## Dataset
Source: https://www.kaggle.com/datasets/shree0910/buy-now-and-pay-later-fintech-ml-dataset  
Shape: 10345 rows × 17 columns  
Introduction:  
Buy Now, Pay Later (BNPL) is one of the fastest-growing fintech segments globally. This synthetic dataset simulates 10,345 BNPL transactions across 6 countries (2023–2024), designed for building credit risk and default prediction models. In this project, we use the data related to financial risk from this dataset to explore what characteristics defaulting users have and to predict users' default risk.

## Workflow
EDA  
Feature Engineering  
Modeling (Logistic regression, Random forest, XGBoost)  
SHAP Interpretation  
Business Insights  

## Model evaluation

We used three machine learning models to predict users’ default risk (default flag = 1):
 1. Logistic Regression
 2. Random Forest
 3. XGBoost

The results are as follows：
### Logistic Regression Results

##### Overall Metrics

| Metric    | Score  |
| --------- | ------ |
| Accuracy  | 0.7252 |
| Precision | 0.7823 |
| Recall    | 0.4077 |
| F1 Score  | 0.5361 |
| AUC       | 0.7666 |

---

##### Classification Report

| Class | Precision | Recall | F1-score | Support |
| ----- | --------- | ------ | -------- | ------- |
| 0     | 0.71      | 0.93   | 0.80     | 1258    |
| 1     | 0.78      | 0.41   | 0.54     | 802     |

---

##### Average Scores

| Average Type | Precision | Recall | F1-score | Support |
| ------------ | --------- | ------ | -------- | ------- |
| Accuracy     | -         | -      | 0.73     | 2060    |
| Macro Avg    | 0.75      | 0.67   | 0.67     | 2060    |
| Weighted Avg | 0.74      | 0.73   | 0.70     | 2060    |



### Random Forest Results

##### Overall Metrics

| Metric    | Score  |
| --------- | ------ |
| Accuracy  | 0.6771 |
| Precision | 0.5678 |
| Recall    | 0.7252 |
| F1 Score  | 0.6370 |
| AUC       | 0.7845 |

---

##### Classification Report

| Class | Precision | Recall | F1-score | Support |
| ----- | --------- | ------ | -------- | ------- |
| 0     | 0.79      | 0.65   | 0.71     | 1261    |
| 1     | 0.57      | 0.73   | 0.64     | 808     |

---

##### Average Scores

| Average Type | Precision | Recall | F1-score | Support |
| ------------ | --------- | ------ | -------- | ------- |
| Accuracy     | -         | -      | 0.68     | 2069    |
| Macro Avg    | 0.68      | 0.69   | 0.67     | 2069    |
| Weighted Avg | 0.70      | 0.68   | 0.68     | 2069    |


### XGBoost Results

##### Overall Metrics

| Metric    | Score  |
| --------- | ------ |
| Accuracy  | 0.7211 |
| Precision | 0.7143 |
| Recall    | 0.4765 |
| F1 Score  | 0.5716 |
| AUC       | 0.7816 |

---

##### Classification Report

| Class | Precision | Recall | F1-score | Support |
| ----- | --------- | ------ | -------- | ------- |
| 0     | 0.72      | 0.88   | 0.79     | 1261    |
| 1     | 0.71      | 0.48   | 0.57     | 808     |

---

##### Average Scores

| Average Type | Precision | Recall | F1-score | Support |
| ------------ | --------- | ------ | -------- | ------- |
| Accuracy     | -         | -      | 0.72     | 2069    |
| Macro Avg    | 0.72      | 0.68   | 0.68     | 2069    |
| Weighted Avg | 0.72      | 0.72   | 0.71     | 2069    |


Among the models, Logistic Regression performed the best in identifying non-default users (default flag = 0), achieving an F1-score of 0.80. For identifying default users (default flag = 1), the Random Forest model achieved the best performance, with an F1-score of 0.64. The AUC scores of all three models ranged from 0.76 to 0.79, indicating that the models have a reasonable level of predictive capability.

In practice, however, the results are still not entirely satisfactory, despite extensive efforts in feature engineering and parameter tuning. I believe this is mainly due to the quality of the original dataset. After examining a large amount of the raw data, I noticed that many users who clearly exhibit characteristics associated with default did not actually default. Such seemingly “misclassified” data points may have negatively affected the overall performance of the models.


## Business Impact
The project demonstrates how machine learning can support fintech risk control strategies through user risk segmentation and predictive analytics.

We found that users with the following characteristics tend to have a higher risk of default:
 1. Low income
 2. Low credit score
 3. Multiple missed payments
 4. High number of repayment delay days

Among these factors, credit score is the most important one, indicating that it plays the strongest role in determining whether a user is likely to default. Users who exhibit several of these characteristics simultaneously are at an even higher risk of default.

## Technologies
Pandas  
Logistic regression  
Random forest  
XGBoost  
SHAP  
Matplotlib  
Seaborn
