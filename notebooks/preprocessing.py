import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

def build_preprocessor(X):
    num_cols = X.select_dtypes(include=["int64", "float64"]).columns
    cat_cols = X.select_dtypes(include=["object", "category", "bool"]).columns

    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("num", num_pipeline, num_cols),
        ("cat", cat_pipeline, cat_cols)
    ])

    return preprocessor

def add_features(df):
    df = df.copy()
    df["study_per_absence"] = df["studytime"] / (df["absences"] + 1)
    df["failure_impact"] = df["failures"] * df["absences"]
    return df

def load_and_split(path):
    df = pd.read_csv(path, sep=";")

    df = add_features(df)
    
    X = df.drop("G3", axis=1)
    y = df["G3"]

    return train_test_split(
        X, y, test_size=0.2, random_state=42
    )