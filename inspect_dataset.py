
import pandas as pd
from pathlib import Path

# Find the UNSW testing CSV
files = list(Path("sample_data").glob("*testing*.csv"))

if not files:
    print("Testing CSV not found. Check the filename and folder.")
else:
    file_path = files[0]

    print("Dataset:", file_path.name)

    # Read only a few rows for inspection
    df = pd.read_csv(file_path, nrows=5)

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nNumber of columns:", len(df.columns))

    print("\nFirst 3 records:")
    print(df.head(3).to_string(index=False))
