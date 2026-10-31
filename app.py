
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
        df = pd.read_csv(uploaded_file)

        st.success("CSV uploaded successfully!")

        st.markdown("### Dataset Preview")

        st.dataframe(
            df.head(10),
            use_container_width=True
        )

        st.markdown("### Dataset Information")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Total Records",
                len(df)
            )

        with col2:
            st.metric(
                "Total Columns",
                len(df.columns)
            )

        st.info(
            "Dataset uploaded successfully. "
            "Model integration is coming next."
        )

    except Exception as e:

        st.error(f"Could not read the CSV file: {e}")

else:

    st.info(
        "Please upload a CSV file to begin."
    )

# --------------------------------
# FOOTER
# --------------------------------

st.divider()

st.caption(
    "AnomaliX | Machine Learning Based "
    "Network Anomaly Detection"
)
