import streamlit as st
import pandas as pd
import re

st.set_page_config(page_title="Expectedness Checker", layout="wide")

st.title("✅ Expectedness Checker (Enhanced UI)")

# ---------- Functions ----------
def normalize_pt(pt):
    if pd.isna(pt):
        return ""
    text = str(pt).strip().lower()
    text = re.sub(r"\s*\(\d+\)\s*$", "", text)
    text = re.sub(r"\s+", " ", text)
    return text


def process_data(ref_list, df):
    ref_set = set([normalize_pt(x) for x in ref_list if x])

    df["PT_normalized"] = df["PT"].apply(normalize_pt)
    df["Expectedness"] = df["Expectedness"].str.strip().str.capitalize()

    df["Derived Expectedness"] = df["PT_normalized"].apply(
        lambda x: "Expected" if x in ref_set else "Unexpected"
    )

    df["Status"] = df.apply(
        lambda row: "Match" if row["Expectedness"] == row["Derived Expectedness"] else "Mismatch",
        axis=1
    )

    return df

# ---------- UI ----------
col1, col2 = st.columns(2)

with col1:
    ref_text = st.text_area("Paste Expected PT List (one per line)")

with col2:
    input_text = st.text_area("Paste Input (Flexible format)")
    file = st.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])

if st.button("🚀 Run Check"):
    ref_list = [x.strip() for x in ref_text.split("
") if x.strip()]

    df = None

    if input_text:
        rows = []
        for line in input_text.split("
"):
            line = line.strip()
            if not line:
                continue

            if "|" in line:
                parts = [x.strip() for x in line.split("|")]
            else:
                parts = line.split()

            if len(parts) >= 3:
                ai = parts[0]
                exp = parts[-1]
                pt = " ".join(parts[1:-1])
                rows.append([ai, pt, exp])

        if rows:
            df = pd.DataFrame(rows, columns=["Active Ingredients", "PT", "Expectedness"])

    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file, engine="openpyxl")

    if df is None:
        st.error("Provide input data")
    elif not ref_list:
        st.error("Provide reference list")
    else:
        result = process_data(ref_list, df)

        st.success("✅ Done")

        # highlight mismatch
        def highlight(row):
            return ['background-color: red' if row.Status == 'Mismatch' else '' for _ in row]

        st.dataframe(result.style.apply(highlight, axis=1))

        st.download_button("Download CSV", result.to_csv(index=False), "output.csv")
