from airflow.decorators import dag, task
from airflow.datasets import Dataset
from airflow.utils.dates import days_ago
import pandas as pd
from sklearn.datasets import load_iris

# Define asset identifiers
raw_data_asset = Dataset("file://./iris_raw.csv")
transformed_data_asset = Dataset("file://./iris_transformed.csv")
summary_data_asset = Dataset("file://./iris_summary.csv")

# Data processing functions
def load_iris_data():
    iris = load_iris()
    df = pd.DataFrame(iris.data, columns=iris.feature_names)
    df["species"] = pd.Categorical.from_codes(iris.target, iris.target_names)
    df.to_csv("./iris_raw.csv", index=False)
    print("Iris dataset saved to ./iris_raw.csv")

def transform_iris_data():
    df = pd.read_csv("./iris_raw.csv")
    df["petal area"] = df["petal length (cm)"] * df["petal width (cm)"]
    df.to_csv("./iris_transformed.csv", index=False)
    print("Transformed dataset saved to ./iris_transformed.csv")

def summarize_iris_data():
    df = pd.read_csv("./iris_transformed.csv")
    summary = df.groupby("species").agg("mean")
    summary.to_csv("./iris_summary.csv")
    print("Summary saved to ./iris_summary.csv")

# DAG 1: Load the Iris dataset and save as asset
@dag(start_date=days_ago(1), schedule="@daily", catchup=False, tags=["iris", "asset"])
def dag_load_iris():
    @task(outlets=[raw_data_asset])
    def download_iris():
        load_iris_data()

    download_iris()

# DAG 2: Transform the raw asset
@dag(start_date=days_ago(1), schedule=[raw_data_asset], catchup=False, tags=["iris", "asset"])
def dag_transform_iris():
    @task(outlets=[transformed_data_asset])
    def transform_iris():
        transform_iris_data()

    transform_iris()

# DAG 3: Analyze the transformed data
@dag(start_date=days_ago(1), schedule=[transformed_data_asset], catchup=False, tags=["iris", "asset"])
def dag_analyze_iris():
    @task(outlets=[summary_data_asset])
    def summarize_iris():
        summarize_iris_data()

    summarize_iris()

dag_load_iris_dag = dag_load_iris()
dag_transform_iris_dag = dag_transform_iris()
dag_analyze_iris_dag = dag_analyze_iris()
