import streamlit as st
import pandas as pd

st.title("Traffic Ban Table")

df = pd.read_csv('data/bans.csv')

st.dataframe(df, use_container_width=True)
