import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer, make_column_selector
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split


def add_features(df):
    df = df.copy()

    # cap outlier absences
    df["absences"] = df["absences"].clip(upper=20)

    # feature engineering
    df["study_per_absence"] = df["studytime"] / (df["absences"] + 1)
    df["failure_impact"] = df["failures"] * df["absences"]

    return df


def build_preprocessor():
    num_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="mean")),
        ("scaler", StandardScaler())
    ])

    cat_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer([
        ("num", num_pipeline, make_column_selector(dtype_include=["number"])),
        ("cat", cat_pipeline, make_column_selector(dtype_include=["object", "string", "category", "bool"]))
    ])

    return preprocessor




def load_and_split(path):
    df = pd.read_csv(path, sep=";")

    df = add_features(df)

    selected_features = [
     'G1',
    'failures',
    'absences',
    'higher',
    'Medu',
    'Fedu',
    'goout',
    'traveltime',
    'age',
    'studytime',

        "study_per_absence",
        "failure_impact"
        
    ]

    X = df[selected_features]
    y = df["G3"]

    return train_test_split(
        X, y, test_size=0.2, random_state=42
    )