
import joblib

artifact_path = "anomaliX_model_artifacts.joblib"

artifacts = joblib.load(artifact_path)

print("\n--- MODEL ARTIFACT CONTENTS ---")

print("Artifact type:", type(artifacts))

if isinstance(artifacts, dict):
    for key, value in artifacts.items():
        print(f"\nKey: {key}")
        print("Object type:", type(value))

        if key == "selected_features":
            print("Number of selected features:", len(value))
            print("First 10 features:", value[:10])

        elif key == "all_feature_names":
            print("Number of total features:", len(value))
            print("First 10 features:", value[:10])

else:
    print("The artifact is not a dictionary.")