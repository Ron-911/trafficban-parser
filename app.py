import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Traffic Ban Summary", layout="wide")

st.markdown("🚦 **Traffic Ban Summary Dashboard**")

csv_path = "./Data/bans.csv"

if not os.path.exists(csv_path):
    st.error("CSV файл не найден.")
else:
    df = pd.read_csv(csv_path)

    st.success(f"Данные загружены: {len(df)} записей")

    if "Country" in df.columns:
        country_counts = df["Country"].value_counts()
        missing_data_countries = country_counts[country_counts == 0].index.tolist()

        if missing_data_countries:
            with st.expander("⚠️ Страны без данных"):
                for country in missing_data_countries:
                    st.write(f"- {country}")

    st.dataframe(df, use_container_width=True)
