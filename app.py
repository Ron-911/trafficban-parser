import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Traffic Ban Summary", layout="wide")
st.title("🚦 Traffic Ban Summary Dashboard")

csv_path = "Data/bans.csv"

if not os.path.exists(csv_path):
    st.error("❌ CSV файл не найден. Убедитесь, что парсер уже запускался и файл доступен.")
else:
    try:
        df = pd.read_csv(csv_path)

        if df.empty:
            st.warning("⚠️ Файл найден, но в нём нет данных.")
        else:
            st.success(f"✅ Данные загружены: {len(df)} записей")
            st.dataframe(df, use_container_width=True)

            with st.expander("📊 Фильтр по стране"):
                countries = df["Country"].unique().tolist()
                selected = st.multiselect("Выберите страны", countries, default=countries[:5])
                filtered_df = df[df["Country"].isin(selected)]
                st.dataframe(filtered_df, use_container_width=True)

    except Exception as e:
        st.exception(f"Ошибка при чтении CSV: {e}")
