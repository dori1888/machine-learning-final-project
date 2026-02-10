import streamlit as st
import pandas as pd
import plotly.express as px

# Configuración de página
st.set_page_config(page_title="Life Expectancy Project", layout="wide")

# Imagen
st.image("src/assets/top_left.png", use_container_width=True)

st.title("Envejecimiento poblacional y esperanza de vida")


st.write("""
Aplicación interactiva para analizar factores asociados
a la esperanza de vida usando datos del Global Burden of Disease.
""")


# Imagen Iris
st.subheader("Ejemplo de imágenes (Iris)")
st.image("src/assets/iris1.png", use_container_width=True)


# ==============================
# Cargar datos
# ==============================
@st.cache_data
def load_data():
    return pd.read_csv("src/data/processed/demog_clean.csv")

df = load_data()
st.subheader("Mapa de correlaciones (heatmap)")

# Seleccionamos solo columnas numéricas
num_cols = df.select_dtypes(include="number").columns.tolist()

# Opción para elegir qué variables incluir
selected_cols = st.multiselect(
    "Elige variables para el heatmap",
    options=num_cols,
    default=num_cols
)

if len(selected_cols) < 2:
    st.info("Selecciona al menos 2 variables para ver el heatmap.")
else:
    corr = df[selected_cols].corr()

    fig_corr = px.imshow(
        corr,
        text_auto=True,
        aspect="auto",
        title="Correlación entre variables"
    )

    st.plotly_chart(fig_corr, use_container_width=True)

# ==============================
# Sidebar: filtros
# ==============================
st.sidebar.header("Filtros")

regions = sorted(df["region"].dropna().unique().tolist())
selected_regions = st.sidebar.multiselect(
    "Selecciona regiones",
    options=regions,
    default=["Global"] if "Global" in regions else []
)

if selected_regions:
    df_f = df[df["region"].isin(selected_regions)].copy()
else:
    df_f = df.copy()

st.sidebar.markdown("---")

# Variable X para análisis explicativo
candidate_x = [
    "under5_mortality",
    "total_deaths",
    "life_expectancy_male",
    "life_expectancy_female",
]
candidate_x = [c for c in candidate_x if c in df.columns]

x_var = st.sidebar.selectbox(
    "Variable para comparar con esperanza de vida",
    options=candidate_x,
    index=0
)

# ======================
# Métricas resumen
# ======================
st.subheader("Resumen global")

col1, col2, col3 = st.columns(3)
col1.metric("Esperanza de vida media", round(df_f["life_expectancy_total"].mean(), 2))
col2.metric("Máxima esperanza de vida", round(df_f["life_expectancy_total"].max(), 2))
col3.metric("Mínima esperanza de vida", round(df_f["life_expectancy_total"].min(), 2))

# ======================
# Vista previa
# ======================
st.subheader("Vista previa del dataset (filtrado)")
st.dataframe(df_f.head(20), width="stretch")

# ==============================
# Top regiones por esperanza de vida
# ==============================
st.subheader("Top regiones por esperanza de vida (según filtro)")

top = df_f.sort_values("life_expectancy_total", ascending=False).head(20)

fig_top = px.bar(
    top.sort_values("life_expectancy_total"),
    x="life_expectancy_total",
    y="region",
    orientation="h",
    title="Top 20 regiones por esperanza de vida"
)
st.plotly_chart(fig_top, width="stretch")

# ==============================
# Scatter explicativo
# ==============================
st.subheader(f"Relación entre {x_var} y esperanza de vida")

fig_scatter = px.scatter(
    df_f,
    x=x_var,
    y="life_expectancy_total",
    hover_name="region",
    title=f"{x_var} vs life_expectancy_total"
)
st.plotly_chart(fig_scatter, width="stretch")

# ==============================
# Nota interpretativa
# ==============================
st.info(
    "Nota: Este análisis es **correlacional** (no causal). "
    "Sirve para explorar asociaciones entre variables a nivel agregado."
)

st.subheader("Relaciones entre variables (scatter con filtros por rango)")

num_cols = df.select_dtypes(include="number").columns.tolist()

c1, c2, c3 = st.columns(3)

with c1:
    x_var = st.selectbox(
        "Variable X",
        options=num_cols,
        index=num_cols.index("under5_mortality") if "under5_mortality" in num_cols else 0
    )

with c2:
    y_var = st.selectbox(
        "Variable Y",
        options=num_cols,
        index=num_cols.index("life_expectancy_total") if "life_expectancy_total" in num_cols else 0
    )

with c3:
    color_var = st.selectbox(
        "Color (opcional)",
        options=["(ninguno)"] + num_cols,
        index=0
    )

# --- Sliders de rango ---
x_min, x_max = float(df[x_var].min()), float(df[x_var].max())
y_min, y_max = float(df[y_var].min()), float(df[y_var].max())

x_range = st.slider(
    f"Rango de {x_var}",
    min_value=x_min,
    max_value=x_max,
    value=(x_min, x_max)
)

y_range = st.slider(
    f"Rango de {y_var}",
    min_value=y_min,
    max_value=y_max,
    value=(y_min, y_max)
)

# Filtrado por rangos
df_f = df[
    (df[x_var] >= x_range[0]) & (df[x_var] <= x_range[1]) &
    (df[y_var] >= y_range[0]) & (df[y_var] <= y_range[1])
].copy()

st.caption(f"Filas tras filtrar: {len(df_f):,}")

kwargs = {}
if color_var != "(ninguno)":
    kwargs["color"] = color_var

fig_scatter = px.scatter(
    df_f,
    x=x_var,
    y=y_var,
    hover_name="region" if "region" in df_f.columns else None,
    **kwargs
)

st.plotly_chart(fig_scatter, use_container_width=True)




