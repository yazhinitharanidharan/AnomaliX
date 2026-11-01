"""Executable self-checks for AnomaliX without rendering the Streamlit UI."""

from __future__ import annotations

import io
import sys
import traceback
from pathlib import Path
from typing import Callable

import pandas as pd

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "selftest_results.txt"


class FakeUpload:
    def __init__(self, raw: bytes, name: str = "upload.csv", file_id: str = "selftest-file"):
        self._raw = raw
        self.name = name
        self.size = len(raw)
        self.file_id = file_id

    def getvalue(self) -> bytes:
        return self._raw


def _record(results: list[tuple[str, bool, str]], name: str, check: Callable[[], str]) -> None:
    try:
        results.append((name, True, check()))
    except Exception as exc:
        results.append(
            (name, False, f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
        )


def run(write_report: bool = True) -> list[tuple[str, bool, str]]:
    import altair as alt

    import data_utils
    import model_utils
    import styles

    expected = [str(column) for column in model_utils.preprocessor.feature_names_in_]
    real_predictor = model_utils.predict_network_traffic
    data_utils.load_predictor = lambda: {
        "predictor": real_predictor,
        "expected_columns": expected,
        "error": None,
    }

    sample_raw = (ROOT / "sample_data" / "sample_network_traffic.csv").read_bytes()
    sample_df = pd.read_csv(io.BytesIO(sample_raw), encoding="utf-8-sig")
    results: list[tuple[str, bool, str]] = []

    def compile_sources() -> str:
        names = ["app.py", "data_utils.py", "styles.py", "model_utils.py", "selftest.py"]
        for name in names:
            source = (ROOT / name).read_text(encoding="utf-8")
            compile(source, name, "exec")
        return f"{len(names)} source files compiled"

    def valid_upload() -> str:
        frame, metadata = data_utils.load_uploaded_dataset(FakeUpload(sample_raw))
        assert len(frame) == len(sample_df)
        assert metadata["rows"] == len(sample_df)
        assert metadata["expected_columns"] == expected
        return f"{len(frame)} rows, {len(frame.columns)} columns"

    def predict_sample() -> str:
        frame, _ = data_utils.load_uploaded_dataset(FakeUpload(sample_raw))
        results_frame = data_utils.run_prediction(frame)
        assert len(results_frame) == len(frame)
        assert "Prediction" in results_frame.columns
        labels = set(results_frame["Prediction"].unique())
        assert labels <= {"Normal", "Anomaly"}, labels
        normal = int((results_frame["Prediction"] == "Normal").sum())
        anomaly = int((results_frame["Prediction"] == "Anomaly").sum())
        assert normal + anomaly == len(results_frame)
        return f"Normal={normal}, Anomaly={anomaly}"

    def expect_error(
        label: str,
        raw: bytes,
        fragment: str,
        name: str = "upload.csv",
    ) -> str:
        try:
            data_utils.load_uploaded_dataset(FakeUpload(raw, name=name))
        except data_utils.DatasetError as exc:
            message = str(exc)
            assert fragment.lower() in message.lower(), message
            return f"{label}: {message}"
        raise AssertionError(f"{label} did not raise DatasetError")

    def empty_file() -> str:
        return expect_error("empty", b"", "empty")

    def whitespace_file() -> str:
        return expect_error("whitespace", b"   \n\t\n", "empty")

    def wrong_extension() -> str:
        return expect_error("extension", b"a,b\n1,2\n", "CSV", name="data.txt")

    def duplicate_columns() -> str:
        return expect_error("duplicates", b"a,a\n1,2\n", "Duplicate")

    def missing_values() -> str:
        frame = sample_df.copy()
        frame.iloc[0, 0] = None
        raw = frame.to_csv(index=False).encode("utf-8")
        return expect_error("missing values", raw, "Missing values")

    def missing_feature() -> str:
        frame = sample_df.drop(columns=[expected[0]])
        raw = frame.to_csv(index=False).encode("utf-8")
        return expect_error("missing feature", raw, "required feature")

    def reserved_prediction() -> str:
        frame = sample_df.copy()
        frame["Prediction"] = "Normal"
        raw = frame.to_csv(index=False).encode("utf-8")
        return expect_error("reserved column", raw, "reserved")

    def malformed_csv() -> str:
        return expect_error("malformed", b"a,b\n1,2,3,4\n", "could not be parsed")

    def extra_columns() -> str:
        frame = sample_df.copy()
        frame["extra_column"] = 1
        raw = frame.to_csv(index=False).encode("utf-8")
        loaded, metadata = data_utils.load_uploaded_dataset(FakeUpload(raw))
        assert "extra_column" in metadata["ignored_columns"]
        assert "extra_column" in loaded.columns
        return "extra column preserved and ignored by the model"

    def csv_roundtrip() -> str:
        frame, _ = data_utils.load_uploaded_dataset(FakeUpload(sample_raw))
        results_frame = data_utils.run_prediction(frame)
        exported = data_utils.results_csv(results_frame)
        reloaded = pd.read_csv(io.BytesIO(exported), encoding="utf-8-sig")
        assert len(reloaded) == len(results_frame)
        assert "Prediction" in reloaded.columns
        return f"{len(reloaded)} rows exported and reloaded"

    def render_html_cleanup() -> str:
        captured: list[str] = []
        original = styles.st.markdown
        styles.st.markdown = lambda body, **kwargs: captured.append(body)
        try:
            styles.render_html(
                """
                <div class="demo">
                    <span>ok</span>
                </div>
                """
            )
        finally:
            styles.st.markdown = original
        assert captured
        body = captured[0]
        assert body.startswith("<div")
        assert "<span>ok</span>" in body
        indented = [line for line in body.splitlines() if line.startswith(" ")]
        assert not indented, indented
        return "indented HTML was dedented before rendering"

    def altair_schema() -> str:
        source = (ROOT / "app.py").read_text(encoding="utf-8")
        assert "title=None" not in source
        summary = pd.DataFrame(
            {
                "Classification": ["Normal traffic", "Potential anomaly"],
                "Records": [90, 10],
                "Share": [90.0, 10.0],
                "ShareLabel": ["90.0%", "10.0%"],
            }
        )
        colors = alt.Scale(
            domain=["Normal traffic", "Potential anomaly"],
            range=["#A09B85", "#242321"],
        )
        donut_base = alt.Chart(summary).encode(
            theta=alt.Theta("Records:Q", stack=True),
            color=alt.Color("Classification:N", scale=colors, legend=None),
            tooltip=[
                alt.Tooltip("Classification:N"),
                alt.Tooltip("Records:Q", format=","),
                alt.Tooltip("Share:Q", format=".1f"),
            ],
        )
        donut = donut_base.mark_arc(innerRadius=78, outerRadius=116)
        center = (
            alt.Chart(pd.DataFrame({"text": ["10.0%"]}))
            .mark_text(fontSize=34)
            .encode(text="text:N")
        )
        donut_chart = (donut + center).properties(height=285)
        donut_chart.to_dict()
        bars = (
            alt.Chart(summary)
            .mark_bar()
            .encode(
                x=alt.X("Share:Q", scale=alt.Scale(domain=[0, 100])),
                y=alt.Y("Classification:N", sort=["Normal traffic", "Potential anomaly"]),
                color=alt.Color("Classification:N", scale=colors, legend=None),
            )
        )
        bar_labels = bars.mark_text(dx=6).encode(
            text=alt.Text("ShareLabel:N"),
            color=alt.value("#242321"),
        )
        bar_chart = (bars + bar_labels).properties(height=285)
        bar_chart.to_dict()
        return "donut and bar Altair specs validated"

    checks = [
        ("compile sources", compile_sources),
        ("valid upload", valid_upload),
        ("real model prediction", predict_sample),
        ("empty file rejected", empty_file),
        ("whitespace file rejected", whitespace_file),
        ("wrong extension rejected", wrong_extension),
        ("duplicate columns rejected", duplicate_columns),
        ("missing values rejected", missing_values),
        ("missing feature rejected", missing_feature),
        ("reserved Prediction column rejected", reserved_prediction),
        ("malformed CSV rejected", malformed_csv),
        ("extra columns preserved", extra_columns),
        ("CSV export round trip", csv_roundtrip),
        ("HTML dedenting", render_html_cleanup),
        ("Altair schema", altair_schema),
    ]

    for name, check in checks:
        _record(results, name, check)

    if write_report:
        lines = ["AnomaliX self-test report", ""]
        for name, passed, detail in results:
            status = "PASS" if passed else "FAIL"
            lines.append(f"[{status}] {name}")
            lines.append(f"    {detail}")
            lines.append("")
        REPORT_PATH.write_text("\n".join(lines), encoding="utf-8")

    return results


if __name__ == "__main__":
    checks = run()
    for check_name, passed, detail in checks:
        print(f"{'PASS' if passed else 'FAIL'} {check_name}: {detail.splitlines()[0]}")
    sys.exit(0 if all(passed for _, passed, _ in checks) else 1)
