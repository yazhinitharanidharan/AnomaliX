
import joblib
import pandas as pd

# Load the trained model artifact
ARTIFACT_PATH = "anomaliX_model_artifacts.joblib"

artifacts = joblib.load(ARTIFACT_PATH)

preprocessor = artifacts["preprocessor"]
selected_model = artifacts["selected_model"]
selected_features = artifacts["selected_features"]
all_feature_names = artifacts["all_feature_names"]


def predict_network_traffic(df):
    """
    Predict whether network traffic records are
    normal or anomalous.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("Input must be a pandas DataFrame.")

    # Check the raw input columns expected by the preprocessor
    expected_columns = list(preprocessor.feature_names_in_)

    missing_columns = [
        col for col in expected_columns if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Keep only the expected input columns in their original order
    df = df[expected_columns].copy()

    # Apply the saved preprocessing pipeline
    transformed_data = preprocessor.transform(df)

    # Convert transformed data into a DataFrame
    transformed_df = pd.DataFrame(
        transformed_data.toarray()
        if hasattr(transformed_data, "toarray")
        else transformed_data,
        columns=all_feature_names,
        index=df.index
    )

    # Select the 56 features in the saved order
    selected_data = transformed_df[selected_features]

    # Run Isolation Forest predictions
    predictions = selected_model.predict(selected_data.to_numpy())

    # Convert model outputs into readable labels
    results = [
        "Anomaly" if prediction == -1 else "Normal"
        for prediction in predictions
    ]

    return results
