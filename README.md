# Greenplum + MADlib Housing Regression Demo

This project builds a simple **Greenplum / MADlib pipeline** using the **Kaggle Ames Housing dataset**.  
It walks through Bronze → Silver → ML stages, training Linear Regression and GLM models entirely in-database.

---

## Repository Contents

- **bronze_schema.sql** – Creates the Bronze table `training_bronze` with all raw Ames Housing columns:contentReference[oaicite:0]{index=0}.  
- **load.sql** – Loads `train.csv` into the Bronze table from `/home/gpadmin/housing/`:contentReference[oaicite:1]{index=1}.  
- **create_training_data.sql** – Builds the Silver half-sample `training_silver_halfdata`, selecting half of each neighborhood for training:contentReference[oaicite:2]{index=2}.  
- **split_neighborhoods.py** – Creates schema `training_silver_hoods` and splits Bronze data into one table per neighborhood:contentReference[oaicite:3]{index=3}.  
- **train_regressions.py** – Trains MADlib Linear and GLM models, generates predictions, and reports R² and RMSE metrics:contentReference[oaicite:4]{index=4}.

---

## Prerequisites

- Greenplum 7.5+ with MADlib installed  
- Python 3 with `psycopg2`  
- `train.csv` (Ames Housing) in `/home/gpadmin/housing/`

---

## Run Steps

### 1. Create Bronze layer
```bash
psql -d housing -f bronze_schema.sql
psql -d housing -f load.sql

## 2. Build Silver Training Data

This step prepares the **Silver layer** — a curated subset of the Ames Housing dataset used for model training.  
Two different approaches are included:

- A half-sample table (`training_silver_halfdata`)
- Per-neighborhood split tables under the schema `training_silver_hoods`

---

### Create the Silver Half-Sample

This SQL script selects half of each neighborhood’s records from the Bronze table.

```bash
psql -d housing -f create_training_data.sql
