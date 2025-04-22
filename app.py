import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="🚛 Traffic Bans", layout="wide")
st.title("🚦 Traffic Ban Summary Dashboard")

data_path = "data/bans.csv"

if not os.path.exists(data_path):
    st.warning("Файл data/bans.csv не найден. Запусти парсер через GitHub Actions.")
else:
    df = pd.read_csv(data_path)
    st.success(f"Данные загружены: {len(df)} записей")
    country = st.selectbox("Страна", ["Все"] + sorted(df["Country"].unique()))
    if country != "Все":
        df = df[df["Country"] == country]
    st.dataframe(df, use_container_width=True)
