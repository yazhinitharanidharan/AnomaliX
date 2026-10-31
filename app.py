
import streamlit as st
import pandas as pd

# --------------------------------
# PAGE CONFIGURATION
# --------------------------------

st.set_page_config(
    page_title="AnomaliX | Network Intrusion Detection",
    page_icon="🛡️",
    layout="wide"
)

# --------------------------------
# HEADER
# --------------------------------

st.title("🛡️ AnomaliX")
st.subheader("Network Intrusion Detection System")

st.write(
    "Anomaly-based network traffic analysis "
    "using machine learning."
)

st.divider()

# --------------------------------
# PROJECT INTRODUCTION
# --------------------------------

st.markdown("### Welcome to AnomaliX")

st.write(
    """
    AnomaliX analyses network traffic records using a
    machine-learning anomaly detection model.

    Upload a network traffic CSV file to analyse records
    and identify potentially anomalous activity.
    """
)

# --------------------------------
# FILE UPLOAD
# --------------------------------

st.markdown("### Upload Network Traffic Data")

uploaded_file = st.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

if uploaded_file is not None:

    try:
        # Read uploaded CSV
        df = pd.read_csv(uploaded_file)

        st.success("CSV uploaded successfully!")

        st.markdown("### Dataset Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        # Dataset information
        st.markdown("### Dataset Information")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Total Records", len(df))

        with col2:
            st.metric("Total Columns", len(df.columns))

        # --------------------------------
        # MODEL PREDICTION
        # --------------------------------

        st.divider()
        st.markdown("### Anomaly Detection Results")

        with st.spinner("Analysing network traffic..."):

            from model_utils import predict_network_traffic

            predictions = predict_network_traffic(df)

        # Add predictions to original uploaded data
        results_df = df.copy()
        results_df["Prediction"] = predictions

        # Count predictions
        normal_count = predictions.count("Normal")
        anomaly_count = predictions.count("Anomaly")

        # Display metrics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Total Records Analysed",
                len(predictions)
            )

        with col2:
            st.metric(
                "Normal Traffic",
                normal_count
            )

        with col3:
            st.metric(
                "Anomalous Traffic",
                anomaly_count
            )

        # --------------------------------
        # DETECTION SUMMARY
        # --------------------------------

        st.markdown("### Detection Summary")

        summary_df = pd.DataFrame({
            "Traffic Classification": ["Normal", "Anomaly"],
            "Number of Records": [normal_count, anomaly_count]
        })

        st.bar_chart(
            summary_df.set_index("Traffic Classification")
        )

        # --------------------------------
        # ANOMALY DETAILS
        # --------------------------------

        st.markdown("### Detected Anomalies")

        anomaly_df = results_df[
            results_df["Prediction"] == "Anomaly"
        ]

        if not anomaly_df.empty:

            st.warning(
                f"{len(anomaly_df)} potentially anomalous "
                "records detected."
            )

            st.dataframe(
                anomaly_df,
                use_container_width=True
            )

        else:

            st.success("No anomalous records detected.")

        # --------------------------------
        # DOWNLOAD RESULTS
        # --------------------------------

        st.markdown("### Download Analysis Results")

        csv_data = results_df.to_csv(index=False).encode("utf-8")

        st.download_button(
            label="Download Prediction Results CSV",
            data=csv_data,
            file_name="anomaliX_prediction_results.csv",
            mime="text/csv"
        )

        st.caption(
            "Predictions are generated using the trained "
            "Isolation Forest model. Anomaly classifications "
            "indicate potentially suspicious traffic and "
            "should not be treated as confirmed attacks."
        )

    except Exception as e:

        st.error(
            f"An error occurred while analysing the dataset: {e}"
        )

else:

    st.info(
        "Please upload a network traffic CSV file to begin."
    )

# --------------------------------
# FOOTER
# --------------------------------

st.divider()

st.caption(
    "AnomaliX | Machine Learning Based "
    "Network Anomaly Detection"
)
