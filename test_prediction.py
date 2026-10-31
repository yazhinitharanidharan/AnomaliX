
import pandas as pd
from model_utils import predict_network_traffic

# Load our sample network traffic
df = pd.read_csv(
    "sample_data/sample_network_traffic.csv"
)

# Run anomaly detection
predictions = predict_network_traffic(df)

print("\n--- ANOMALIX PREDICTION TEST ---")
print("Total records:", len(df))

print("Normal records:", predictions.count("Normal"))
print("Anomalous records:", predictions.count("Anomaly"))

print("\nFirst 10 predictions:")
print(predictions[:10])
