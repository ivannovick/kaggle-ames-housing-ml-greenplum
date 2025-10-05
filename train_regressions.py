#!/usr/bin/env python3
import psycopg2
import math

DB_NAME = "housing"
DB_USER = "gpadmin"
DB_HOST = "localhost"
DB_PORT = "5432"

# -----------------------------
# Tables: Train on Silver, Test on Bronze
# -----------------------------
TRAIN_TABLE = "public.training_silver_halfdata"
TEST_TABLE  = "public.training_bronze"

# -----------------------------
# Numeric features (INT + FLOAT, excluding Id and SalePrice)
# -----------------------------
FEATURES = """
COALESCE(mssubclass,0), COALESCE(lotfrontage,0), COALESCE(lotarea,0),
COALESCE(overallqual,0), COALESCE(overallcond,0), COALESCE(yearbuilt,0),
COALESCE(yearremodadd,0), COALESCE(masvnrarea,0),
COALESCE(bsmtfinsf1,0), COALESCE(bsmtfinsf2,0), COALESCE(bsmtunfsf,0),
COALESCE(totalbsmtsf,0),
COALESCE("1stFlrSF",0), COALESCE("2ndFlrSF",0), COALESCE(lowqualfinsf,0),
COALESCE(grlivarea,0),
COALESCE(bsmtfullbath,0), COALESCE(bsmthalfbath,0),
COALESCE(fullbath,0), COALESCE(halfbath,0),
COALESCE(bedroomabvgr,0), COALESCE(kitchenabvgr,0),
COALESCE(totrmsabvgrd,0), COALESCE(fireplaces,0),
COALESCE(garageyrblt,0), COALESCE(garagecars,0), COALESCE(garagearea,0),
COALESCE(wooddecksf,0), COALESCE(openporchsf,0),
COALESCE(enclosedporch,0), COALESCE("3SsnPorch",0),
COALESCE(screenporch,0), COALESCE(poolarea,0),
COALESCE(miscval,0), COALESCE(mosold,0), COALESCE(yrsold,0)
"""

# -----------------------------
# Model configurations: Linear Regression + GLM
# -----------------------------
MODELS = [
    {
        "name": "linear",
        "train_sql": f"""
            SELECT madlib.linregr_train(
                '{TRAIN_TABLE}',
                'public.linear_evaltest_model',
                'saleprice',
                'ARRAY[{FEATURES}]',
                NULL,
                FALSE
            );
        """
    },
    {
        "name": "glm",
        "train_sql": f"""
            SELECT madlib.glm(
                '{TRAIN_TABLE}',
                'public.glm_evaltest_model',
                'saleprice',
                'ARRAY[{FEATURES}]',
                'family=gaussian, link=identity',
                NULL,
                NULL,
                TRUE
            );
        """
    }
]


def run_models():
    conn = psycopg2.connect(
        dbname=DB_NAME, user=DB_USER, host=DB_HOST, port=DB_PORT
    )
    conn.autocommit = True
    cur = conn.cursor()

    for m in MODELS:
        prefix = f"{m['name']}_evaltest"
        display_name = "LINEAR REGRESSION" if m["name"] == "linear" else "GLM"
        print(f"\n🚀 Training {display_name} model...")

        # Drop old artifacts
        cur.execute(f"""
            DROP TABLE IF EXISTS public.{prefix}_model CASCADE;
            DROP TABLE IF EXISTS public.{prefix}_model_summary CASCADE;
            DROP TABLE IF EXISTS public.{prefix}_predictions CASCADE;
            DROP TABLE IF EXISTS public.{prefix}_metrics CASCADE;
            DROP TABLE IF EXISTS public.{prefix}_metrics_mse CASCADE;
        """)

        # Train
        cur.execute(m["train_sql"])
        print(f"✅ {display_name} training completed.")

        # -----------------------------
        # Predictions on TEST_TABLE (Bronze data)
        # -----------------------------
        if m["name"] == "linear":
            predict_sql = f"""
                SELECT id, saleprice,
                       madlib.linregr_predict(m.coef, ARRAY[{FEATURES}]) AS estimate
                INTO public.{prefix}_predictions
                FROM {TEST_TABLE} t,
                     public.{prefix}_model m;
            """
        else:  # GLM
            predict_sql = f"""
                SELECT id, saleprice,
                       madlib.glm_predict(m.coef, ARRAY[{FEATURES}], 'identity') AS estimate
                INTO public.{prefix}_predictions
                FROM {TEST_TABLE} t,
                     public.{prefix}_model m;
            """

        cur.execute(predict_sql)

        # -----------------------------
        # Evaluation using MADlib metrics
        # -----------------------------
        metrics_table = f"public.{prefix}_metrics"

        cur.execute(f"DROP TABLE IF EXISTS {metrics_table};")
        cur.execute(f"DROP TABLE IF EXISTS {metrics_table}_mse;")

        # R²
        cur.execute(f"""
            SELECT madlib.r2_score(
                'public.{prefix}_predictions',
                '{metrics_table}',
                'estimate',
                'saleprice',
                NULL
            );
        """)
        cur.execute(f"SELECT r2_score FROM {metrics_table};")
        r2 = cur.fetchone()[0]

        # MSE → RMSE
        cur.execute(f"""
            SELECT madlib.mean_squared_error(
                'public.{prefix}_predictions',
                '{metrics_table}_mse',
                'estimate',
                'saleprice',
                NULL
            );
        """)
        cur.execute(f"SELECT mean_squared_error FROM {metrics_table}_mse;")
        mse = cur.fetchone()[0]
        rmse = math.sqrt(mse)

        print(f"📊 {display_name} results → R²: {r2:.4f}, RMSE: {rmse:.2f}")

    cur.close()
    conn.close()
    print("\n✅ Linear Regression and GLM models trained and evaluated successfully.")


if __name__ == "__main__":
    run_models()

