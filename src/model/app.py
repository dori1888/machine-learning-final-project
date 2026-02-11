import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ======================
# CONFIG
# ======================
st.set_page_config(page_title="Life Expectancy Project", layout="wide")

BASE_DIR = Path(__file__).resolve().parents[1]
ASSETS = BASE_DIR / "assets"
DATA = BASE_DIR / "data" / "processed"

# ======================
# HEADER
# ======================
col1, col2 = st.columns([2,1])

with col1:
    st.title("Envejecimiento poblacional y esperanza de vida")
    st.write(
        "Aplicación interactiva para explorar asociaciones entre variables "
        "demográficas y la esperanza de vida (análisis correlacional)."
    )

with col2:
    header = ASSETS / "header.png"
    if header.exists():
        st.image(str(header), use_container_width=True)

# ======================
# LOAD DATA
# ======================
@st.cache_data
def load_data():
    return pd.read_csv(DATA / "demog_clean.csv")

df = load_data()

# ======================
# SIDEBAR
# ======================
st.sidebar.header("Filtros")

regions = sorted(df["region"].dropna().unique())
selected_regions = st.sidebar.multiselect(
    "Selecciona regiones",
    regions,
    default=["Global"] if "Global" in regions else regions[:3]
)

df_f = df[df["region"].isin(selected_regions)] if selected_regions else df.copy()

# ======================
# RESUMEN
# ======================
st.subheader("Resumen global")

c1, c2, c3 = st.columns(3)

c1.metric("Esperanza de vida media", round(df_f["life_expectancy_total"].mean(),2))
c2.metric("Máxima esperanza de vida", round(df_f["life_expectancy_total"].max(),2))
c3.metric("Mínima esperanza de vida", round(df_f["life_expectancy_total"].min(),2))

# ======================
# HEATMAP
# ======================
st.subheader("Correlación entre variables")

num_cols = df_f.select_dtypes(include="number").columns.tolist()

selected_cols = st.multiselect(
    "Variables",
    num_cols,
    default=num_cols[:6]
)

if len(selected_cols) >= 2:

    tmp = df_f[selected_cols].dropna()
    var_cols = [c for c in selected_cols if tmp[c].nunique() > 1]

    if len(var_cols) >= 2:
        corr = tmp[var_cols].corr()

        fig_corr = px.imshow(
            corr,
            text_auto=".2f",
            aspect="auto"
        )

        st.plotly_chart(fig_corr, use_container_width=True)
    else:
        st.warning("Variables sin variación con los filtros actuales.")

# ======================
# SCATTER
# ======================
st.subheader("Relación entre variables")

x_var = st.selectbox("Variable X", num_cols, index=0)
y_var = st.selectbox("Variable Y", num_cols, index=1)

fig = px.scatter(
    df_f,
    x=x_var,
    y=y_var,
    hover_name="region"
)

st.plotly_chart(fig, use_container_width=True)

# ======================
# CONCLUSIONES
# ======================
st.subheader("Conclusiones")

st.info(
    """
    El análisis muestra asociaciones entre esperanza de vida y variables
    demográficas como mortalidad infantil, gasto sanitario o educación.
    Es importante recordar que los resultados son correlacionales,
    no implican causalidad directa.
    """
)

with st.expander("Guion breve para defensa"):
    st.write(
        """
        1. Este proyecto analiza factores asociados a la esperanza de vida global.
        2. Se utilizó un dataset demográfico internacional procesado.
        3. Se aplicaron visualizaciones exploratorias: heatmap de correlaciones,
           gráficos de dispersión y métricas resumen.
        4. Los resultados indican asociaciones claras entre mortalidad infantil
           y esperanza de vida.
        5. El análisis es correlacional, útil para exploración inicial de datos.
        """
    )


    

    



