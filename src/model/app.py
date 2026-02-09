import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración
st.set_page_config(page_title="Life Expectancy Project", layout="wide")

# Título
st.title("Envejecimiento poblacional y esperanza de vida")

st.write("""
Aplicación interactiva para analizar factores asociados
a la esperanza de vida usando datos del Global Burden of Disease.
""")

# ==============================
# Cargar datos
# ==============================
df = pd.read_csv("src/data/processed/demog_clean.csv")
# ======================
# Métricas resumen
# ======================
col1, col2, col3 = st.columns(3)

col1.metric(
    "Esperanza de vida media",
    round(df["life_expectancy_total"].mean(), 2)
)

col2.metric(
    "Máxima esperanza de vida",
    round(df["life_expectancy_total"].max(), 2)
)

col3.metric(
    "Mínima esperanza de vida",
    round(df["life_expectancy_total"].min(), 2)
)


st.subheader("Vista previa del dataset")
st.dataframe(df.head())

# ==============================
# Top países por esperanza de vida
# ==============================
st.subheader("Top regiones por esperanza de vida")

top = df.sort_values("life_expectancy_total", ascending=False).head(20)

fig = px.bar(
    top,
    x="life_expectancy_total",
    y="region",
    orientation="h"
)

st.plotly_chart(fig, use_container_width=True)


