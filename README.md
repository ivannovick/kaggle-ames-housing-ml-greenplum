# Greenplum + MADlib Housing Regression Demo

This project builds a simple **Greenplum / MADlib pipeline** using the **Kaggle Ames Housing dataset**.  
It walks through Bronze → Silver → ML stages, training Linear Regression and GLM models entirely in-database.

---

## Repository Contents

- **bronze_schema.sql** – Creates the Bronze table `training_bronze` with all raw Ames Housing columns
- **load.sql** – Loads `train.csv` into the Bronze table 
- **split_neighborhoods.py** – Creates schema `training_silver_hoods` and splits Bronze data into one table per neighborhood  
- **create_training_data.sql** – Builds the Silver half-sample `training_silver_halfdata`, selecting half of each neighborhood for training  
- **train_regressions.py** – Trains MADlib Linear and GLM models, generates predictions, and reports R² and RMSE metrics
---

## Prerequisites

- Greenplum 7.5+ with MADlib installed  
- Python 3 with `psycopg2`  
- `train.csv` (Ames Housing) from Kaggle
---

## Run Steps

## 1. Create Bronze Layer

Begin by defining the Bronze layer, which serves as the raw data foundation for the pipeline.
This step creates the training_bronze table and loads the full Ames Housing dataset into Greenplum.
The Bronze layer mirrors the original source structure and preserves all columns and values exactly as they appear in the raw CSV file.
It provides a consistent, immutable baseline from which subsequent Silver and model-training datasets are derived.

## 2. Build Silver Training Data

This stage prepares the **Silver layer**, a cleaner and more structured subset of the Ames Housing dataset for model training.  
It includes two main workflows: creating a half-sample for overall model training and generating neighborhood-specific tables for localized analysis.

---

### Create the Silver Half-Sample

The half-sample is generated from the Bronze layer by selecting approximately half of the rows for each neighborhood.  
This ensures that every neighborhood is represented evenly in the training dataset, preventing skew from areas with higher sample counts.  
The resulting table, `training_silver_halfdata`, is randomly selected and distributed across the cluster for balanced parallel processing.

---

### Split by Neighborhood

In addition to the global half-sample, each neighborhood from the Bronze dataset is extracted into its own table within a new schema called `training_silver_hoods`.  
Each table corresponds to one neighborhood and includes all relevant records from the Bronze layer.  
This structure allows targeted model experiments or separate regression analysis by location.  
The process automatically discovers all distinct neighborhood names and creates corresponding tables.

---

### Verify the Silver Layer

After processing, you should have:
- A single `training_silver_halfdata` table containing half of each neighborhood’s rows  
- Multiple tables under the `training_silver_hoods` schema, one for each neighborhood  

Together, these represent your **Silver training datasets**, ready for modeling and evaluation.

---

## 3. Train and Evaluate Models

Once the Silver data is prepared, the next step is to train predictive models using **MADlib** within Greenplum.  
Two regression techniques are applied:
- **Linear Regression** to fit continuous relationships between home features and sale price  
- **Generalized Linear Model (GLM)** to capture broader relationships with configurable statistical families

Both models are trained on the Silver half-sample and evaluated on the full Bronze dataset to measure generalization performance.  
Evaluation metrics include:
- **R² (Coefficient of Determination)** – how well the model explains variance in sale prices  
- **RMSE (Root Mean Squared Error)** – the average deviation between predicted and actual prices

After training, model artifacts, predictions, and metric tables are automatically stored in the database for inspection or comparison.  
The results provide a quick benchmark for model quality and serve as a foundation for further feature engineering or advanced modeling.
