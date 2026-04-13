# ---------------------------------------------------------
# TRAINING SCRIPT
# This file:
# 1) loads the dataset we created
# 2) prepares text + numeric features
# 3) trains a machine learning model
# 4) tests model accuracy
# 5) saves the trained model to a file
# ---------------------------------------------------------

import joblib
import pandas as pd

# ColumnTransformer lets us process different column types differently
from sklearn.compose import ColumnTransformer

# Converts symptoms text into numbers the model can learn from
from sklearn.feature_extraction.text import TfidfVectorizer

# Used to evaluate how well the model performs
from sklearn.metrics import classification_report, accuracy_score

# Splits data into training part and testing part
from sklearn.model_selection import train_test_split

# Lets us chain preprocessing + model in one object
from sklearn.pipeline import Pipeline

# Converts gender values like M/F into machine-readable columns
from sklearn.preprocessing import OneHotEncoder

# Our classifier
from sklearn.ensemble import RandomForestClassifier


# File path of the dataset we generated
DATA_PATH = "triage_data.csv"

# File name where the trained model will be saved
MODEL_PATH = "triage_model.pkl"


def main():
    # ---------------------------------------------------------
    # STEP 1: Load dataset
    # ---------------------------------------------------------
    df = pd.read_csv(DATA_PATH)

    print("Dataset loaded successfully.")
    print("Shape:", df.shape)
    print(df.head())

    # ---------------------------------------------------------
    # STEP 2: Separate inputs (X) and output label (y)
    # X = features used for prediction
    # y = target we want to predict
    # ---------------------------------------------------------
    X = df.drop(columns=["triage_label"])
    y = df["triage_label"]

    # ---------------------------------------------------------
    # STEP 3: Define which columns are:
    # - text
    # - categorical
    # - numeric
    # ---------------------------------------------------------
    text_features = "symptoms"
    categorical_features = ["gender"]
    numeric_features = [
        "age",
        "temperature_c",
        "heart_rate",
        "systolic_bp",
        "diastolic_bp",
        "spo2",
        "respiratory_rate",
    ]

    # ---------------------------------------------------------
    # STEP 4: Build preprocessing pipeline
    #
    # symptoms -> TF-IDF vectorization
    # gender   -> one-hot encoding
    # numbers  -> passed as they are
    # ---------------------------------------------------------
    preprocessor = ColumnTransformer(
        transformers=[
            ("text", TfidfVectorizer(max_features=120, ngram_range=(1, 2)), text_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features),
        ]
    )

    # ---------------------------------------------------------
    # STEP 5: Build full ML pipeline
    # It first preprocesses data, then trains classifier
    # ---------------------------------------------------------
    model = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", RandomForestClassifier(
                n_estimators=250,
                max_depth=12,
                random_state=42
            )),
        ]
    )

    # ---------------------------------------------------------
    # STEP 6: Split dataset
    # 80% training, 20% testing
    # stratify=y keeps label distribution balanced
    # ---------------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    print("\nTraining set size:", X_train.shape)
    print("Testing set size:", X_test.shape)

    # ---------------------------------------------------------
    # STEP 7: Train the model
    # ---------------------------------------------------------
    model.fit(X_train, y_train)

    # ---------------------------------------------------------
    # STEP 8: Predict on test set
    # ---------------------------------------------------------
    y_pred = model.predict(X_test)

    # ---------------------------------------------------------
    # STEP 9: Print evaluation metrics
    # accuracy = overall correct predictions
    # classification report = precision/recall/f1 by class
    # ---------------------------------------------------------
    print("\nAccuracy:", round(accuracy_score(y_test, y_pred), 4))
    print("\nClassification Report:\n")
    print(classification_report(y_test, y_pred))

    # ---------------------------------------------------------
    # STEP 10: Save trained model
    # ---------------------------------------------------------
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved as {MODEL_PATH}")


# Run only when this file is executed directly
if __name__ == "__main__":
    main()