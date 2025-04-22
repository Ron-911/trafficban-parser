import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Traffic Ban Summary Dashboard", layout="wide")

st.title("🚦 Traffic Ban Summary Dashboard")

# CSV loader
if os.path.exists("traffic_bans.csv"):
    df = pd.read_csv("traffic_bans.csv")
    st.success(f"Данные загружены: {len(df)} записей")
else:
    st.error("CSV файл не найден.")

# Ошибочные страны
if os.path.exists("failed_countries.txt"):
    with open("failed_countries.txt", "r", encoding="utf-8") as f:
        failed_countries = [line.strip() for line in f.readlines() if line.strip()]
    if failed_countries:
        with st.expander("⚠️ Страны, для которых не удалось получить данные"):
            st.write(", ".join(failed_countries))
else:
    failed_countries = []

# Отображение данных
if 'df' in locals():
    st.dataframe(df, use_container_width=True)