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
    text = re.sub(r"\s*\(\d+\)\s*$", "", text)  # remove MedDRA code
    text = re.sub(r"\s+", " ", text)
    return text


def process_data(ref_list, df):
    ref_set = set([normalize_pt(x) for x in ref_list if x])

    df["PT_normalized"] = df["PT"].apply(normalize_pt)
    df["Expectedness"] = df["Expectedness"].astype(str).str.strip().str.capitalize()

    df["Derived Expectedness"] = df["PT_normalized"].apply(
        lambda x: "Expected" if x in ref_set else "Unexpected"
    )

    df["Status"] = df.apply(
        lambda row: "Match"
        if row["Expectedness"] == row["Derived Expectedness"]
        else "Mismatch",
        axis=1,
    )

    return df


# ---------- UI ----------
col1, col2 = st.columns(2)

with col1:
    ref_text = st.text_area(
        "📌 Paste Expected PT List (one per line)",
        height=300
    )

with col2:
    input_text = st.text_area(
        "📌 Paste Input (Flexible format)",
        height=200
    )

    file = st.file_uploader("Upload CSV/Excel", type=["csv", "xlsx"])


# ---------- Run ----------
if st.button("🚀 Run Check"):

    # ✅ FIXED LINE (THIS CAUSED YOUR ERROR)
    ref_list = [x.strip() for x in ref_text.split("\n") if x.strip()]

    df = None

    # ---------- Text parsing ----------
    if input_text:
        rows = []
        for line in input_text.split("\n"):
            line = line.strip()
            if not line:
                continue

            # Support both formats
            if "|" in line:
                parts = [x.strip() for x in line.split("|")]
            else:
                parts = line.split()

            if len(parts) >= 3:
                ai = parts[0]
                expectedness = parts[-1]
                pt = " ".join(parts[1:-1])

                rows.append([ai, pt, expectedness])

        if rows:
            df = pd.DataFrame(
                rows,
                columns=["Active Ingredients", "PT", "Expectedness"]
            )

    # ---------- File upload ----------
    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        else:
            try:
                df = pd.read_excel(file, engine="openpyxl")
            except Exception as e:
                st.error(f"❌ Excel read error: {str(e)}")
                st.stop()

    # ---------- Validation ----------
    if df is None:
        st.error("❌ Please provide input data")
    elif not ref_list:
        st.error("❌ Please provide reference list")
    else:
        result = process_data(ref_list, df)

        st.success("✅ Done")

        # ✅ Highlight mismatches
        def highlight(row):
            return [
                "background-color: #ffcccc" if row["Status"] == "Mismatch" else ""
                for _ in row
            ]

        st.dataframe(result.style.apply(highlight, axis=1), use_container_width=True)

        # ✅ Download
        st.download_button(
            "📥 Download Output",
            result.to_csv(index=False),
            file_name="expectedness_output.csv"
        )
