"""AnomaliX — Intelligent Network Anomaly Detection."""

from __future__ import annotations

import logging

import altair as alt
import pandas as pd
import streamlit as st

from data_utils import (
    DatasetError,
    load_predictor,
    load_uploaded_dataset,
    results_csv,
    results_filename,
    run_prediction,
    upload_signature,
)
from styles import (
    PALETTE,
    empty_state,
    file_strip,
    footer,
    hero,
    inject_styles,
    kpi_grid,
    render_html,
    section_head,
    sidebar_brand,
    sidebar_status,
    status_card,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page configuration and session state
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="AnomaliX | Intelligent Network Anomaly Detection",
    page_icon=":material/shield:",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_styles()

NAV_ITEMS = [
    "Dashboard",
    "Traffic Analysis",
    "Upload Dataset",
    "Detection Results",
    "About the System",
]

DEFAULT_STATE = {
    "nav": "Dashboard",
    "dataset_df": None,
    "dataset_meta": None,
    "dataset_signature": None,
    "upload_attempt_signature": None,
    "results_df": None,
    "analysis_error": None,
    "upload_error": None,
    "upload_notice": None,
    "uploader_epoch": 0,
}

for state_key, default_value in DEFAULT_STATE.items():
    if state_key not in st.session_state:
        st.session_state[state_key] = default_value

# Widget-backed navigation must be updated before the radio is instantiated.
pending_view = st.session_state.pop("_pending_view", None)
if pending_view in NAV_ITEMS:
    st.session_state.nav = pending_view
if st.session_state.nav not in NAV_ITEMS:
    st.session_state.nav = "Dashboard"


def go_to(view: str) -> None:
    st.session_state.nav = view


def reset_workspace() -> None:
    st.session_state.dataset_df = None
    st.session_state.dataset_meta = None
    st.session_state.dataset_signature = None
    st.session_state.upload_attempt_signature = None
    st.session_state.results_df = None
    st.session_state.analysis_error = None
    st.session_state.upload_error = None
    st.session_state.upload_notice = None
    st.session_state.uploader_epoch = int(st.session_state.uploader_epoch) + 1
    st.session_state.nav = "Dashboard"


# ---------------------------------------------------------------------------
# Shared UI building blocks
# ---------------------------------------------------------------------------


def format_count(value: int) -> str:
    return f"{value:,}"


def render_uploader(location: str, compact: bool = False) -> None:
    render_html(
        '<p class="ax-muted" style="font-size:0.8rem;margin:0 0 0.55rem;">'
        "CSV only · up to 100 MB · UNSW-NB15 feature schema"
        "</p>"
    )

    uploaded_file = st.file_uploader(
        "Upload a network traffic dataset",
        type=["csv"],
        key=f"dataset_uploader_{st.session_state.uploader_epoch}",
        help="Upload a CSV whose columns match the UNSW-NB15 feature set used to train AnomaliX.",
        label_visibility="collapsed" if compact else "visible",
        max_upload_size=100,
    )

    if uploaded_file is None:
        st.session_state.upload_attempt_signature = None
        st.session_state.upload_error = None
        st.session_state.upload_notice = None
        if st.session_state.dataset_df is not None:
            st.caption(
                "A validated dataset remains loaded from your previous upload. "
                "Use Clear dataset to remove it."
            )
        return

    signature = upload_signature(uploaded_file)
    if st.session_state.upload_attempt_signature != signature:
        st.session_state.upload_attempt_signature = signature
        st.session_state.results_df = None
        st.session_state.analysis_error = None
        st.session_state.upload_error = None
        st.session_state.upload_notice = None

        try:
            with st.spinner("Validating dataset…"):
                dataset, metadata = load_uploaded_dataset(uploaded_file)
        except DatasetError as exc:
            st.session_state.dataset_df = None
            st.session_state.dataset_meta = None
            st.session_state.dataset_signature = None
            st.session_state.upload_error = str(exc)
        except Exception:
            logger.exception("Unexpected failure while validating an uploaded dataset")
            st.session_state.dataset_df = None
            st.session_state.dataset_meta = None
            st.session_state.dataset_signature = None
            st.session_state.upload_error = (
                "The dataset could not be validated because of an unexpected error. "
                "Check the file and try again. See the server logs for details."
            )
        else:
            st.session_state.dataset_df = dataset
            st.session_state.dataset_meta = metadata
            st.session_state.dataset_signature = signature
            st.session_state.upload_error = None
            if location == "upload":
                st.session_state.upload_notice = "Dataset validated successfully."

        st.rerun()

    if st.session_state.upload_notice:
        st.success(st.session_state.upload_notice)
        st.session_state.upload_notice = None
    if st.session_state.upload_error:
        st.error(st.session_state.upload_error)


def render_analysis_error() -> None:
    if st.session_state.analysis_error:
        st.error(st.session_state.analysis_error)


def render_dataset(show_preview: bool = False) -> None:
    dataset = st.session_state.dataset_df
    metadata = st.session_state.dataset_meta
    if dataset is None or metadata is None:
        return

    file_strip(
        metadata["name"],
        metadata["size_label"],
        metadata["rows"],
        metadata["columns"],
    )

    ignored = metadata.get("ignored_columns") or []
    expected = metadata.get("expected_columns")

    if expected:
        render_html(
            f'<p class="ax-muted" style="font-size:0.78rem;margin-top:-0.35rem;">'
            f"All {len(expected)} required model features are present. "
            f"{'Extra columns will be preserved in the export but ignored by the model.' if ignored else ''}"
            "</p>"
        )
    if ignored:
        preview = ", ".join(ignored[:8])
        if len(ignored) > 8:
            preview += f", +{len(ignored) - 8} more"
        st.caption(
            f"Unexpected columns preserved in the export but ignored by the model: {preview}."
        )

    if show_preview:
        with st.expander("Dataset preview", expanded=True):
            st.dataframe(
                dataset.head(50),
                width="stretch",
                hide_index=True,
            )
            st.caption(
                f"Showing the first {min(len(dataset), 50):,} of {len(dataset):,} records."
            )
    else:
        with st.expander("Dataset preview and upload details"):
            st.dataframe(
                dataset.head(30),
                width="stretch",
                hide_index=True,
            )
            st.caption(
                f"Showing the first {min(len(dataset), 30):,} of {len(dataset):,} records. "
                f"File size: {metadata['size_label']}."
            )


def analyse_dataset() -> None:
    dataset = st.session_state.dataset_df
    if dataset is None:
        return

    st.session_state.analysis_error = None
    try:
        with st.spinner("Analysing network traffic with the Isolation Forest model…"):
            results = run_prediction(dataset)
    except DatasetError as exc:
        st.session_state.results_df = None
        st.session_state.analysis_error = str(exc)
        st.rerun()
    except Exception:
        logger.exception("Unexpected failure while running anomaly analysis")
        st.session_state.results_df = None
        st.session_state.analysis_error = (
            "The analysis could not be completed because of an unexpected error. "
            "Verify the dataset and try again. See the server logs for details."
        )
        st.rerun()

    st.session_state.results_df = results
    st.session_state.analysis_error = None
    st.session_state["_pending_view"] = "Detection Results"
    st.rerun()


def render_dataset_actions(location: str, model_ready: bool, show_profile: bool = True) -> None:
    has_results = st.session_state.results_df is not None
    columns = st.columns([1.25, 1, 1])

    with columns[0]:
        if st.button(
            "Run analysis again" if has_results else "Run anomaly analysis",
            type="primary",
            key=f"analyse_{location}",
            disabled=not model_ready,
            width="stretch",
        ):
            analyse_dataset()

    with columns[1]:
        if show_profile:
            st.button(
                "View traffic profile",
                type="secondary",
                key=f"profile_{location}",
                on_click=go_to,
                args=("Traffic Analysis",),
                width="stretch",
            )
        elif has_results:
            st.button(
                "Open results",
                type="secondary",
                key=f"results_{location}",
                on_click=go_to,
                args=("Detection Results",),
                width="stretch",
            )

    with columns[2]:
        st.button(
            "Clear dataset",
            type="secondary",
            key=f"clear_{location}",
            on_click=reset_workspace,
            width="stretch",
        )

    if not model_ready:
        st.warning(
            "Analysis is unavailable because the detection model could not be loaded. "
            "The dataset can still be previewed and validated."
        )


def result_charts(results: pd.DataFrame) -> None:
    if results.empty or "Prediction" not in results.columns:
        return

    total = len(results)
    normal = int((results["Prediction"] == "Normal").sum())
    anomaly = int((results["Prediction"] == "Anomaly").sum())
    anomaly_pct = (anomaly / total * 100) if total else 0.0

    shares = [100.0 - anomaly_pct if total else 0.0, anomaly_pct]
    summary = pd.DataFrame(
        {
            "Classification": ["Normal traffic", "Potential anomaly"],
            "Records": [normal, anomaly],
            "Share": shares,
            "ShareLabel": [f"{share:.1f}%" for share in shares],
        }
    )

    colors = alt.Scale(
        domain=["Normal traffic", "Potential anomaly"],
        range=[PALETTE["taupe"], PALETTE["charcoal"]],
    )

    donut_base = alt.Chart(summary).encode(
        theta=alt.Theta("Records:Q", stack=True),
        color=alt.Color("Classification:N", scale=colors, legend=None),
        tooltip=[
            alt.Tooltip("Classification:N", title="Classification"),
            alt.Tooltip("Records:Q", title="Records", format=","),
            alt.Tooltip("Share:Q", title="Share (%)", format=".1f"),
        ],
    )
    donut = donut_base.mark_arc(innerRadius=78, outerRadius=116, cornerRadius=4, padAngle=2)
    center = (
        alt.Chart(pd.DataFrame({"text": [f"{anomaly_pct:.1f}%"]}))
        .mark_text(
            font="Fraunces, Georgia, serif",
            fontSize=34,
            fontWeight=500,
            color=PALETTE["charcoal"],
            dy=-4,
        )
        .encode(text="text:N")
    )
    donut_chart = (donut + center).properties(height=285)

    bars = (
        alt.Chart(summary)
        .mark_bar(cornerRadiusEnd=5, size=26)
        .encode(
            x=alt.X(
                "Share:Q",
                title="Share of records (%)",
                scale=alt.Scale(domain=[0, 100]),
                axis=alt.Axis(
                    grid=False,
                    format=".0f",
                    tickCount=5,
                    titleColor=PALETTE["grey"],
                    titleFontSize=10,
                    labelColor=PALETTE["grey"],
                    labelFontSize=10,
                ),
            ),
            y=alt.Y(
                "Classification:N",
                sort=["Normal traffic", "Potential anomaly"],
                axis=alt.Axis(labelColor=PALETTE["grey"], labelFontSize=11),
            ),
            color=alt.Color("Classification:N", scale=colors, legend=None),
            tooltip=[
                alt.Tooltip("Classification:N", title="Classification"),
                alt.Tooltip("Records:Q", title="Records", format=","),
                alt.Tooltip("Share:Q", title="Share (%)", format=".1f"),
            ],
        )
    )
    bar_labels = bars.mark_text(
        align="left",
        dx=6,
        font="Manrope, sans-serif",
        fontSize=11,
        fontWeight=600,
    ).encode(
        text=alt.Text("ShareLabel:N"),
        color=alt.value(PALETTE["charcoal"]),
    )
    bar_chart = (bars + bar_labels).properties(height=285)

    chart_left, chart_right = st.columns(2, gap="large")

    with chart_left:
        render_html('<div class="ax-chart-title">Classification split</div>')
        st.altair_chart(donut_chart, width="stretch")
        render_html(
            f'<div class="ax-chart-caption">{anomaly_pct:.1f}% of records are potential anomalies.</div>'
        )

    with chart_right:
        render_html('<div class="ax-chart-title">Share of analysed records</div>')
        st.altair_chart(bar_chart, width="stretch")
        render_html(
            '<div class="ax-chart-caption">Percentages are calculated from actual model predictions.</div>'
        )


def highlight_predictions(styler: pd.io.formats.style.Styler) -> pd.io.formats.style.Styler:
    def paint(value: object) -> str:
        if value == "Anomaly":
            return "background-color: #F3E0D9; color: #242321; font-weight: 600;"
        return "background-color: #EFF1E8; color: #3F4735; font-weight: 500;"

    if hasattr(styler, "map"):
        return styler.map(paint, subset=["Prediction"])
    return styler.applymap(paint, subset=["Prediction"])


def render_results_table(results: pd.DataFrame) -> None:
    filter_col, info_col = st.columns([0.6, 1.4], gap="large")

    with filter_col:
        selection = st.selectbox(
            "Show records",
            ["All records", "Potential anomalies", "Normal traffic"],
            key="results_filter",
        )

    if selection == "Potential anomalies":
        filtered = results[results["Prediction"] == "Anomaly"]
    elif selection == "Normal traffic":
        filtered = results[results["Prediction"] == "Normal"]
    else:
        filtered = results

    display = filtered.head(500)
    with info_col:
        render_html(
            f'<p class="ax-muted" style="font-size:0.78rem;padding-top:2rem;">'
            f"Showing {len(display):,} of {len(filtered):,} matching records. "
            "Use the table search to inspect values, or download the full CSV for the complete dataset."
            "</p>"
        )

    if display.empty:
        st.info("No records match this filter.")
        return

    styled = highlight_predictions(display.style)
    st.dataframe(
        styled,
        width="stretch",
        hide_index=True,
        height=430,
        column_config={
            "Prediction": st.column_config.TextColumn(
                "Prediction",
                help="Model output. An anomaly is a potential outlier, not a confirmed cyberattack.",
            )
        },
    )


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------


def page_dashboard(model_ready: bool, expected_count: int, model_error: str | None) -> None:
    dataset = st.session_state.dataset_df
    results = st.session_state.results_df
    rows = len(dataset) if dataset is not None else 0
    result_count = len(results) if results is not None else 0

    hero(model_ready, dataset is not None, rows, result_count)

    action_cols = st.columns([1, 1, 2.2])
    with action_cols[0]:
        st.button(
            "Upload a dataset",
            type="primary",
            key="dashboard_upload_cta",
            on_click=go_to,
            args=("Upload Dataset",),
            width="stretch",
        )
    with action_cols[1]:
        st.button(
            "View results",
            type="secondary",
            key="dashboard_results_cta",
            disabled=results is None,
            on_click=go_to,
            args=("Detection Results",),
            width="stretch",
        )

    render_html('<hr class="ax-divider">')

    upload_col, status_col = st.columns([1.5, 0.82], gap="large")

    with upload_col:
        section_head(
            "Start here",
            "Bring your network traffic.",
            "Drop in a CSV and AnomaliX will validate the schema before any prediction runs.",
        )
        render_uploader("dashboard", compact=True)
        render_analysis_error()
        if dataset is not None:
            render_dataset(show_preview=False)
            render_dataset_actions("dashboard", model_ready)

    with status_col:
        render_html('<div class="ax-eyebrow">Current state</div>')
        status_rows = [
            (
                "Detection model",
                "Ready" if model_ready else "Unavailable",
                "ready" if model_ready else "missing",
            ),
            (
                "Dataset",
                "Loaded" if dataset is not None else "Awaiting upload",
                "ready" if dataset is not None else "waiting",
            ),
            (
                "Records",
                format_count(rows) if dataset is not None else "—",
                "",
            ),
            (
                "Analysis",
                f"{format_count(result_count)} records" if results is not None else "Not run",
                "ready" if results is not None else "waiting",
            ),
        ]
        if expected_count:
            status_rows.append(("Model features", f"{expected_count} expected", ""))
        status_card(status_rows)

        if not model_ready and model_error:
            st.error(model_error)

        render_html(
            '<p class="ax-muted" style="font-size:0.74rem;margin-top:0.8rem;">'
            "All status values reflect the current application state. No simulated traffic "
            "or invented metrics are shown."
            "</p>"
        )

    render_html('<hr class="ax-divider">')
    section_head(
        "How it works",
        "Designed around careful analysis.",
        "Every result comes from the existing trained model and its saved preprocessing pipeline.",
    )

    steps = st.columns(3, gap="large")
    step_content = [
        (
            "01",
            "Validate",
            "Columns, duplicates, missing values, file size, and the expected UNSW-NB15 schema are checked before analysis.",
        ),
        (
            "02",
            "Analyse",
            "The saved Isolation Forest artifact and preprocessing pipeline classify each traffic record.",
        ),
        (
            "03",
            "Review",
            "Explore the distribution, inspect potential anomalies, and export the complete labelled dataset.",
        ),
    ]
    for column, (number, title, copy) in zip(steps, step_content):
        with column:
            render_html(
                f"""
                <div class="ax-card">
                    <div class="ax-step-number">{number}</div>
                    <h3>{title}</h3>
                    <p>{copy}</p>
                </div>
                """
            )


def page_traffic_analysis(model_ready: bool, expected_columns: list[str]) -> None:
    section_head(
        "Workspace",
        "Traffic analysis.",
        "A closer look at the uploaded dataset before and after the model produces its labels.",
    )

    dataset = st.session_state.dataset_df
    metadata = st.session_state.dataset_meta
    results = st.session_state.results_df

    if dataset is None or metadata is None:
        empty_state(
            "No dataset is loaded.",
            "Upload a network traffic CSV to see its structure, feature coverage, and analysis readiness.",
        )
        st.button(
            "Go to dataset upload",
            type="primary",
            key="profile_upload_cta",
            on_click=go_to,
            args=("Upload Dataset",),
        )
        return

    file_strip(metadata["name"], metadata["size_label"], metadata["rows"], metadata["columns"])

    present_expected = sum(1 for column in expected_columns if column in dataset.columns)
    kpi_grid(
        [
            {
                "label": "Records",
                "value": format_count(len(dataset)),
                "note": "Rows available for analysis",
            },
            {
                "label": "Columns",
                "value": format_count(dataset.shape[1]),
                "note": "Original dataset width",
            },
            {
                "label": "Feature coverage",
                "value": (
                    f"{present_expected}/{len(expected_columns)}"
                    if expected_columns
                    else "Unknown"
                ),
                "note": "Required model features present",
                "tone": "tint",
            },
            {
                "label": "Extra columns",
                "value": format_count(len(metadata.get("ignored_columns") or [])),
                "note": "Preserved, ignored by model",
            },
        ]
    )

    render_html('<div class="ax-eyebrow">Dataset profile</div>')
    sample = dataset if len(dataset) <= 50_000 else dataset.head(50_000)
    profile = pd.DataFrame(
        {
            "Column": sample.columns,
            "Data type": [str(dtype) for dtype in sample.dtypes],
            "Unique values": [int(sample[column].nunique(dropna=False)) for column in sample.columns],
        }
    )
    st.dataframe(profile, width="stretch", hide_index=True, height=360)
    if len(dataset) > len(sample):
        st.caption(
            f"Profile calculated from the first {len(sample):,} records to keep the interface responsive."
        )

    if expected_columns:
        with st.expander("Expected model feature schema"):
            st.dataframe(
                pd.DataFrame({"Required feature": expected_columns}),
                width="stretch",
                hide_index=True,
                height=300,
            )
            st.caption(
                "Feature order is controlled by the saved preprocessing pipeline and is not changed by the UI."
            )

    if results is not None:
        render_html('<hr class="ax-divider">')
        render_html('<div class="ax-eyebrow">Analysis complete</div>')
        render_html(
            f"<p>This dataset has {format_count(len(results))} labelled records ready to review.</p>"
        )
        st.button(
            "Open detection results",
            type="primary",
            key="profile_open_results",
            on_click=go_to,
            args=("Detection Results",),
        )
    else:
        render_html('<hr class="ax-divider">')
        render_analysis_error()
        render_dataset_actions("profile_page", model_ready, show_profile=False)


def page_upload(model_ready: bool) -> None:
    section_head(
        "Ingest",
        "Upload dataset.",
        "AnomaliX accepts CSV network traffic records that match the UNSW-NB15 feature schema.",
    )

    form_col, guide_col = st.columns([1.45, 0.85], gap="large")

    with form_col:
        render_uploader("upload", compact=False)
        render_analysis_error()

        dataset = st.session_state.dataset_df
        metadata = st.session_state.dataset_meta

        if dataset is not None and metadata is not None:
            render_html('<div style="height:0.45rem"></div>')
            render_dataset(show_preview=True)
            render_dataset_actions("upload_page", model_ready)
        else:
            render_html(
                '<p class="ax-muted" style="font-size:0.78rem;margin-top:0.8rem;">'
                "Your file is checked before prediction. Empty files, duplicate columns, "
                "missing features, invalid values, and oversized uploads are rejected with a "
                "clear explanation."
                "</p>"
            )

    with guide_col:
        render_html('<div class="ax-eyebrow">Upload checklist</div>')
        status_card(
            [
                ("File format", "CSV", ""),
                ("Maximum size", "100 MB", ""),
                ("Required schema", "UNSW-NB15 features", ""),
                (
                    "Detection model",
                    "Ready" if model_ready else "Unavailable",
                    "ready" if model_ready else "missing",
                ),
            ]
        )

        render_html(
            """
            <div class="ax-card" style="margin-top:1rem;">
                <h3>Before you upload</h3>
                <p>Keep the original feature columns. Identifier and label columns may remain —
                they are preserved in the export and ignored by the model.</p>
            </div>
            """
        )

        render_html(
            """
            <div class="ax-card" style="margin-top:1rem;">
                <h3>Data quality</h3>
                <p>Rows with missing values are rejected rather than silently imputed. This keeps
                the analysis aligned with the model's original preprocessing.</p>
            </div>
            """
        )


def page_results() -> None:
    results = st.session_state.results_df
    metadata = st.session_state.dataset_meta

    section_head(
        "Analysis",
        "Detection results.",
        "Model output is shown as normal traffic or potential anomalies — never as confirmed attacks.",
    )

    if results is None:
        if st.session_state.analysis_error:
            st.error(st.session_state.analysis_error)
        empty_state(
            "No analysis results yet.",
            "Upload a validated dataset and run the anomaly analysis to populate this workspace.",
        )
        st.button(
            "Upload a dataset",
            type="primary",
            key="results_upload_cta",
            on_click=go_to,
            args=("Upload Dataset",),
        )
        return

    if results.empty or "Prediction" not in results.columns:
        empty_state(
            "The analysis produced no usable rows.",
            "Run the analysis again from a validated dataset. If the problem continues, "
            "check the server logs for details.",
        )
        return

    total = len(results)
    normal = int((results["Prediction"] == "Normal").sum())
    anomaly = int((results["Prediction"] == "Anomaly").sum())
    anomaly_pct = (anomaly / total * 100) if total else 0.0

    if metadata:
        file_strip(metadata["name"], metadata["size_label"], metadata["rows"], metadata["columns"])

    kpi_grid(
        [
            {
                "label": "Total records",
                "value": format_count(total),
                "note": "Records analysed by the model",
            },
            {
                "label": "Normal traffic",
                "value": format_count(normal),
                "note": f"{100.0 - anomaly_pct:.1f}% of analysed records",
            },
            {
                "label": "Potential anomalies",
                "value": format_count(anomaly),
                "note": "Require further investigation",
                "tone": "tint",
            },
            {
                "label": "Anomaly rate",
                "value": f"{anomaly_pct:.1f}%",
                "note": "Actual model output, not a forecast",
                "tone": "dark",
            },
        ]
    )

    result_charts(results)

    render_html('<hr class="ax-divider">')
    section_head(
        "Records",
        "Inspect the labelled dataset.",
        "Filter by classification, search within the table, and review suspicious traffic in context.",
    )
    render_results_table(results)

    render_html('<hr class="ax-divider">')

    download_col, note_col = st.columns([0.8, 1.2], gap="large")
    with download_col:
        st.download_button(
            "Download complete results",
            data=results_csv(results),
            file_name=results_filename(),
            mime="text/csv",
            key="download_full_results",
            width="stretch",
        )
    with note_col:
        render_html(
            '<p class="ax-muted" style="font-size:0.78rem;padding-top:0.4rem;">'
            "The export keeps every original input column and appends the Prediction column. "
            "Anomaly labels identify statistical outliers, not confirmed cyberattacks."
            "</p>"
        )

    if anomaly > 0:
        anomaly_rows = results[results["Prediction"] == "Anomaly"]
        with st.expander(f"Inspect potential anomalies ({format_count(anomaly)})"):
            render_html(
                f'<p class="ax-muted" style="font-size:0.78rem;">'
                f"Showing the first {min(100, len(anomaly_rows)):,} suspicious records. "
                "Treat these as leads for investigation, not verified incidents."
                "</p>"
            )
            preview = anomaly_rows.head(100)
            st.dataframe(
                highlight_predictions(preview.style),
                width="stretch",
                hide_index=True,
                height=340,
            )
    else:
        st.success("No potential anomalies were detected in this dataset.")

    render_html('<div style="height:0.6rem"></div>')
    st.button(
        "Analyse a new dataset",
        type="secondary",
        key="results_new_dataset",
        on_click=reset_workspace,
    )


def page_about(model_ready: bool, expected_count: int, model_error: str | None) -> None:
    section_head(
        "About",
        "The system behind AnomaliX.",
        "A focused anomaly detection workspace built on a saved Isolation Forest model and the UNSW-NB15 dataset.",
    )

    intro_col, status_col = st.columns([1.45, 0.85], gap="large")

    with intro_col:
        render_html(
            """
            <p style="font-size:0.98rem;color:#4F4C45;max-width:720px;">
                AnomaliX is an anomaly-based network intrusion detection system. It does not
                assume that every unusual record is an attack. Instead, it highlights traffic
                that sits outside the behaviour learned by the Isolation Forest model so a human
                analyst can decide what deserves attention.
            </p>
            """
        )

        render_html(
            """
            <div class="ax-card" style="margin-top:1rem;">
                <h3>Responsible interpretation</h3>
                <p>Isolation Forest is an unsupervised anomaly detector. A label of
                <strong>Anomaly</strong> means the record is statistically unusual relative to the
                training data. It is not proof of malicious activity, compromise, or an attack.</p>
            </div>
            """
        )

    with status_col:
        status_card(
            [
                (
                    "Model artifact",
                    "Loaded" if model_ready else "Unavailable",
                    "ready" if model_ready else "missing",
                ),
                ("Algorithm", "Isolation Forest", ""),
                ("Training data", "UNSW-NB15", ""),
                (
                    "Expected features",
                    str(expected_count) if expected_count else "Unknown",
                    "",
                ),
                ("Output mapping", "-1 anomaly · 1 normal", ""),
            ]
        )
        if not model_ready and model_error:
            st.error(model_error)

    render_html('<hr class="ax-divider">')
    section_head("Technical foundation", "What stays fixed.")

    cards = st.columns(4, gap="medium")
    technical = [
        (
            "Model",
            "A saved Isolation Forest artifact is loaded through the existing model module. The UI never retrains or replaces it.",
        ),
        (
            "Preprocessing",
            "The saved pipeline transforms input columns in the original order before the selected feature set is passed to the model.",
        ),
        (
            "Labels",
            "Raw predictions are mapped consistently: -1 becomes Anomaly and 1 becomes Normal.",
        ),
        (
            "Data",
            "Original input columns are preserved. The exported CSV appends the prediction rather than discarding source fields.",
        ),
    ]
    for column, (title, copy) in zip(cards, technical):
        with column:
            render_html(
                f"""
                <div class="ax-card">
                    <h3>{title}</h3>
                    <p>{copy}</p>
                </div>
                """
            )

    render_html('<hr class="ax-divider">')
    section_head("Scope", "Known limitations.")

    st.markdown(
        "- The model should be evaluated against the traffic profile "
        "and feature schema it was trained on.\n"
        "- Uploaded files are processed within the running application "
        "session; no external service is used.\n"
        "- Missing values are rejected so that prediction behaviour stays "
        "consistent with the saved pipeline.\n"
        "- An anomaly flag is a prompt for review, not an automated incident verdict."
    )


# ---------------------------------------------------------------------------
# Sidebar and routing
# ---------------------------------------------------------------------------

predictor_bundle = load_predictor()
model_ready = predictor_bundle.get("predictor") is not None
model_error = predictor_bundle.get("error")
expected_columns = predictor_bundle.get("expected_columns") or []
expected_count = len(expected_columns)

with st.sidebar:
    sidebar_brand()
    render_html('<div class="ax-nav-label">Workspace</div>')
    active_view = st.radio(
        "Navigation",
        NAV_ITEMS,
        key="nav",
        label_visibility="collapsed",
    )
    current_results = st.session_state.results_df
    sidebar_status(
        model_ready,
        st.session_state.dataset_df is not None,
        len(current_results) if current_results is not None else 0,
    )
    render_html('<div style="height:0.55rem"></div>')
    st.button(
        "Reset workspace",
        key="sidebar_reset_workspace",
        on_click=reset_workspace,
        width="stretch",
    )

if active_view == "Dashboard":
    page_dashboard(model_ready, expected_count, model_error)
elif active_view == "Traffic Analysis":
    page_traffic_analysis(model_ready, expected_columns)
elif active_view == "Upload Dataset":
    page_upload(model_ready)
elif active_view == "Detection Results":
    page_results()
else:
    page_about(model_ready, expected_count, model_error)

footer()
