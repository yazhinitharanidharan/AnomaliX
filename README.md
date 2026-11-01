# AnomaliX

**Intelligent Network Anomaly Detection**

AnomaliX is a Streamlit-based network intrusion detection workspace that identifies statistically unusual network traffic using an Isolation Forest model trained on the UNSW-NB15 dataset.

## Features

- Warm, editorial-style interface with a custom AnomaliX identity
- Guided dataset upload with schema, duplicate-column, missing-value, and file-size validation
- Dataset preview, dimensions, file size, and feature coverage reporting
- Anomaly analysis through the existing saved model artifact and preprocessing pipeline
- KPI summary, classification charts, filterable results table, and suspicious-record review
- Complete CSV export with original columns preserved and prediction labels appended
- Graceful handling of missing model artifacts, malformed CSVs, and oversized uploads

## Technology Stack

- Python
- Streamlit
- Pandas
- NumPy
- Scikit-learn 1.6.1
- Joblib
- Altair

## Project Structure

- `app.py` — application layout, navigation, and views
- `model_utils.py` — existing model loading and prediction logic (unchanged)
- `data_utils.py` — upload validation and prediction orchestration
- `styles.py` — design system and shared presentation helpers
- `sample_data/` — sample UNSW-NB15 traffic data
- `anomaliX_model_artifacts.joblib` — saved preprocessor, selected model, and feature list

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Model Behaviour

Predictions are produced by the saved Isolation Forest artifact. Raw model outputs are mapped consistently: `-1` becomes **Anomaly** and `1` becomes **Normal**. An anomaly label indicates unusual traffic that warrants review, not a confirmed cyberattack.

## Dataset

UNSW-NB15.

## Team

Manasvinee Ramnarayanan  
Yazhini T
