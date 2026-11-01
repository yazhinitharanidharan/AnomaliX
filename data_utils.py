"""Dataset validation and prediction orchestration for AnomaliX.

This module never re-implements model inference. It validates uploads and
delegates predictions to the existing `model_utils.predict_network_traffic`
function so the trained preprocessing pipeline and feature order stay intact.
"""

from __future__ import annotations

import csv
import io
import logging
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

logger = logging.getLogger(__name__)

MAX_UPLOAD_BYTES = 100 * 1024 * 1024
MAX_HEADER_BYTES = 64 * 1024
ARTIFACT_NAME = "anomaliX_model_artifacts.joblib"
ARTIFACT_PATH = Path(__file__).resolve().with_name(ARTIFACT_NAME)


class DatasetError(Exception):
    """A user-facing dataset or prediction problem."""


def format_bytes(size: int) -> str:
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


def upload_signature(uploaded_file: Any) -> str:
    file_id = getattr(uploaded_file, "file_id", None)
    if file_id:
        return f"id:{file_id}"
    name = getattr(uploaded_file, "name", "dataset.csv")
    size = getattr(uploaded_file, "size", 0)
    return f"{name}:{size}"


@st.cache_resource(show_spinner="Loading detection model…")
def load_predictor() -> dict[str, Any]:
    """Load the existing model module once and report a safe status."""
    try:
        import model_utils

        expected: list[str] | None = None
        preprocessor = getattr(model_utils, "preprocessor", None)
        if preprocessor is not None and hasattr(preprocessor, "feature_names_in_"):
            expected = [str(name) for name in preprocessor.feature_names_in_]

        return {
            "predictor": model_utils.predict_network_traffic,
            "expected_columns": expected,
            "error": None,
        }
    except FileNotFoundError as exc:
        logger.warning("Model artifact not found during import: %s", exc)
        if ARTIFACT_PATH.exists():
            error = (
                "The model artifact exists in the project folder, but the app was "
                "started from a different working directory. Restart Streamlit from "
                "the project root."
            )
        else:
            error = (
                "The detection model artifact is missing. Place "
                "anomaliX_model_artifacts.joblib in the project root and restart."
            )
        return {"predictor": None, "expected_columns": None, "error": error}
    except Exception as exc:
        logger.exception("Failed to load the model artifact and preprocessing pipeline")
        return {
            "predictor": None,
            "expected_columns": None,
            "error": (
                f"The detection model could not be loaded ({type(exc).__name__}). "
                "Check the server logs and confirm that the installed scikit-learn "
                "version matches the saved artifact."
            ),
        }


def _read_header(raw: bytes) -> list[str]:
    sample = raw[:MAX_HEADER_BYTES].decode("utf-8-sig", errors="replace")
    lines = sample.splitlines()
    if not lines:
        return []
    try:
        return next(csv.reader([lines[0]]))
    except csv.Error:
        return []


def _duplicate_names(names: list[str]) -> list[str]:
    counts = Counter(name.strip() for name in names)
    return sorted(name for name, count in counts.items() if count > 1)


def _column_preview(columns: list[str], limit: int = 6) -> str:
    shown = ", ".join(columns[:limit])
    if len(columns) > limit:
        shown += f", +{len(columns) - limit} more"
    return shown


def load_uploaded_dataset(uploaded_file: Any) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Read and validate an uploaded CSV without letting bad files crash the app."""
    raw = uploaded_file.getvalue()
    size = len(raw)
    name = getattr(uploaded_file, "name", "uploaded_dataset.csv")

    if not name.lower().endswith(".csv"):
        raise DatasetError("Please upload a CSV file. Other file types are not supported.")

    if size == 0 or (size <= 4096 and not raw.strip()):
        raise DatasetError("This file is empty. Upload a CSV containing network traffic records.")

    if size > MAX_UPLOAD_BYTES:
        raise DatasetError(
            f"This file is {format_bytes(size)}. The maximum supported upload is "
            f"{format_bytes(MAX_UPLOAD_BYTES)}."
        )

    header_names = _read_header(raw)
    if not header_names:
        raise DatasetError("The CSV header could not be read. Check that the file is not corrupted.")

    duplicated = _duplicate_names(header_names)
    if duplicated:
        raise DatasetError(
            "Duplicate column names were found: "
            f"{_column_preview(duplicated)}. Rename duplicate columns before uploading."
        )

    try:
        df = pd.read_csv(io.BytesIO(raw), low_memory=False, encoding="utf-8-sig")
    except pd.errors.EmptyDataError:
        raise DatasetError("The file contains no readable rows.") from None
    except pd.errors.ParserError:
        raise DatasetError(
            "The CSV could not be parsed. Check for malformed rows, unclosed quotes, "
            "or inconsistent column counts."
        ) from None
    except UnicodeDecodeError:
        raise DatasetError("The file encoding could not be read. Save the CSV as UTF-8 and try again.") from None
    except Exception:
        logger.exception("Unexpected error while reading uploaded CSV %r", name)
        raise DatasetError(
            "The CSV could not be read because of an unexpected error. "
            "The file may be corrupted. See the server logs for details."
        ) from None

    if df.empty:
        raise DatasetError("The dataset has no data rows. Add network traffic records and try again.")

    df.columns = [str(column).strip() for column in df.columns]

    if any(not column for column in df.columns):
        raise DatasetError("One or more columns have an empty name. Rename them before uploading.")

    duplicated_after_cleanup = _duplicate_names(list(df.columns))
    if duplicated_after_cleanup:
        raise DatasetError(
            "Duplicate column names were found after trimming whitespace: "
            f"{_column_preview(duplicated_after_cleanup)}."
        )

    if "Prediction" in df.columns:
        raise DatasetError(
            "The column 'Prediction' is reserved for model output. "
            "Rename or remove it before uploading."
        )

    missing_values = [column for column in df.columns if df[column].isna().any()]
    if missing_values:
        raise DatasetError(
            "Missing values were found in: "
            f"{_column_preview(missing_values)}. Fill or remove incomplete records "
            "before running analysis."
        )

    predictor_bundle = load_predictor()
    expected_columns = predictor_bundle.get("expected_columns")
    ignored_columns: list[str] = []

    if expected_columns:
        missing_columns = [column for column in expected_columns if column not in df.columns]
        if missing_columns:
            raise DatasetError(
                f"{len(missing_columns)} required feature column(s) are missing: "
                f"{_column_preview(missing_columns)}. Use a dataset with the expected "
                "UNSW-NB15 feature schema."
            )
        ignored_columns = [column for column in df.columns if column not in expected_columns]

    metadata = {
        "name": name,
        "size": size,
        "size_label": format_bytes(size),
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "ignored_columns": ignored_columns,
        "expected_columns": expected_columns,
    }
    return df, metadata


def run_prediction(df: pd.DataFrame) -> pd.DataFrame:
    """Call the existing prediction function and append its labels."""
    bundle = load_predictor()
    predictor = bundle.get("predictor")

    if predictor is None:
        raise DatasetError(bundle.get("error") or "The detection model is unavailable.")

    try:
        predictions = predictor(df)
    except ValueError as exc:
        logger.warning("Model rejected the dataset values: %s", exc)
        raise DatasetError(
            "The dataset could not be processed by the model. Check that column names "
            "match the expected schema and that values use supported data types."
        ) from None
    except MemoryError:
        raise DatasetError(
            "The dataset is too large to analyse in available memory. Try a smaller CSV."
        ) from None
    except Exception:
        logger.exception("Unexpected failure during model prediction")
        raise DatasetError(
            "The analysis could not be completed because of an unexpected model error. "
            "Verify the feature values and try again. See the server logs for details."
        ) from None

    if len(predictions) != len(df):
        raise DatasetError("The model returned an unexpected number of predictions.")

    valid_labels = {"Normal", "Anomaly"}
    if any(label not in valid_labels for label in predictions):
        raise DatasetError("The model returned an unexpected prediction format.")

    results = df.copy()
    results["Prediction"] = list(predictions)
    return results


def results_csv(results: pd.DataFrame) -> bytes:
    """Export original columns plus the appended prediction labels."""
    return results.to_csv(index=False).encode("utf-8-sig")


def results_filename() -> str:
    stamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"anomaliX_results_{stamp}.csv"
