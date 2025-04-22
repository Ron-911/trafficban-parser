import streamlit as st
import pandas as pd

st.set_page_config(page_title="Traffic Bans Dashboard", layout="wide")
st.title("🚛 Traffic Ban Overview for European Countries")

try:
    df = pd.read_csv("data/bans.csv")
    st.success(f"Loaded {len(df)} bans")
    country_filter = st.selectbox("Filter by country", ["All"] + sorted(df.Country.unique().tolist()))

    if country_filter != "All":
        df = df[df.Country == country_filter]

    st.dataframe(df, use_container_width=True)
except FileNotFoundError:
    st.warning("No data available. Run the scraper first.")
