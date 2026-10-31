
import pandas as pd
from pathlib import Path

# Load the original UNSW testing dataset
input_file = Path("sample_data/UNSW_NB15_testing-set (1).csv")

df = pd.read_csv(input_file)

# Remove identifier and ground-truth labels
traffic_data = df.drop(
    columns=["id", "attack_cat", "label"]
)

# Take 100 real network traffic records
sample_data = traffic_data.head(100).copy()

# Save the sample CSV
output_file = Path("sample_data/sample_network_traffic.csv")
sample_data.to_csv(output_file, index=False)

print("Sample CSV created successfully!")
print("Records:", len(sample_data))
print("Columns:", len(sample_data.columns))
print("Saved to:", output_file)
print("\nFirst 5 records:")
print(sample_data.head())
