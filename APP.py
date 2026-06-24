import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Expectedness Checker", layout="wide")

st.title("✅ Expectedness Checker (Simple UI)")

# -------------------------
# Helper functions
# -------------------------
def normalize_pt(pt):
    if pd.isna(pt):
        return ""
    text = str(pt).strip().lower()
    text = re.sub(r"\s*\(\d+\)\s*$", "", text)  # remove MedDRA code
    text = re.sub(r"\s+", " ", text)
    return text

def process_data(ref_list, df):
    ref_set = set([normalize_pt(x) for x in ref_list if x])

    df["PT_normalized"] = df["PT"].apply(normalize_pt)

    df["Derived Expectedness"] = df["PT_normalized"].apply(
        lambda x: "Expected" if x in ref_set else "Unexpected"
    )

    df["Status"] = df.apply(
        lambda row: "Match" if row["Expectedness"] == row["Derived Expectedness"] else "Mismatch",
        axis=1
    )

    return df

# -------------------------
# UI Layout
# -------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📌 Paste Reference Expected PT List")
    reference_input = st.text_area(
        "One PT per line",
        height=300,
        placeholder="rash\nhypertension\nurinary tract infection"
    )

with col2:
    st.subheader("📌 Paste Input Data (OR Upload File)")
    input_text = st.text_area(
        "Paste: Active Ingredients | PT | Expectedness",
        height=200,
        placeholder="ABIRATERONE | Rash | Expected"
    )

    uploaded_file = st.file_uploader("Upload CSV or Excel", type=["csv", "xlsx"])

# -------------------------
# Process Button
# -------------------------
if st.button("🚀 Run Check"):

    # ----- Reference list -----
    ref_list = []
    if reference_input:
        ref_list = [line.strip() for line in reference_input.split("\n") if line.strip()]

    # ----- Input data -----
    df = None

    # Option A: Text input
    if input_text:
        rows = []
        for line in input_text.split("\n"):
            parts = [x.strip() for x in line.split("|")]
            if len(parts) == 3:
                rows.append(parts)

        if rows:
            df = pd.DataFrame(rows, columns=["Active Ingredients", "PT", "Expectedness"])

    # Option B: File upload
    if uploaded_file:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

    # ----- Validation -----
    if df is None:
        st.error("❌ Please provide input data")
    elif not ref_list:
        st.error("❌ Please provide reference expected list")
    else:
        try:
            result_df = process_data(ref_list, df)

            st.success("✅ Done")

            st.dataframe(result_df)

            st.download_button(
                "📥 Download Output",
                result_df.to_csv(index=False),
                "expectedness_output.csv"
            )

        except Exception as e:
            st.error(f"Error: {str(e)}")