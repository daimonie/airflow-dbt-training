from airflow import DAG
from airflow.decorators import task
from airflow.utils.dates import days_ago
from pathlib import Path
import pandas as pd
from sklearn.datasets import load_iris

CSV_PATH = "/tmp/iris.csv"

with DAG(
    dag_id="iris_analysis_pipeline_cached",
    start_date=days_ago(1),
    schedule_interval=None,
    catchup=False,
    tags=["iris", "xcom", "self-contained"],
) as dag:

    @task
    def get_or_download_iris() -> str:
        if Path(CSV_PATH).exists():
            print(f"File exists: {CSV_PATH}")
        else:
            print(f"File not found. Downloading Iris dataset...")
            iris = load_iris()
            df = pd.DataFrame(iris.data, columns=iris.feature_names)
            df["species"] = pd.Categorical.from_codes(iris.target, iris.target_names)
            df.to_csv(CSV_PATH, index=False)
            print(f"Saved Iris dataset to {CSV_PATH}")
        return CSV_PATH

    @task
    def load_data(filepath: str) -> pd.DataFrame:
        df = pd.read_csv(filepath)
        print(f"Loaded {len(df)} rows")
        print("First few rows:\n", df.head())
        return df

    @task
    def compute_mean_per_species(df: pd.DataFrame) -> str:
        result = df.groupby("species").mean()
        out_path = "/tmp/iris_mean_per_species.csv"
        result.to_csv(out_path)
        print("Mean per species:\n", result)
        print(f"Saved to {out_path}")
        return out_path

    @task
    def compute_global_mean(df: pd.DataFrame) -> str:
        numeric = df.select_dtypes("number")
        result = numeric.mean().to_frame(name="global_mean").T
        out_path = "/tmp/iris_global_mean.csv"
        result.to_csv(out_path, index=False)
        print("Global mean vector:\n", result)
        print(f"Saved to {out_path}")
        return out_path

    @task
    def compute_correlation(df: pd.DataFrame) -> str:
        corr = df["petal length (cm)"].corr(df["petal width (cm)"])
        out_path = "/tmp/iris_petal_correlation.txt"
        result = f"Correlation between petal length and width: {corr:.4f}"
        with open(out_path, "w") as f:
            f.write(result)
        print(result)
        print(f"Saved to {out_path}")
        return out_path

    # DAG flow
    filepath = get_or_download_iris()
    df = load_data(filepath)
    compute_mean_per_species(df)
    compute_global_mean(df)
    compute_correlation(df)

