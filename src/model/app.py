from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# =========================
# RUTAS (SIEMPRE BIEN)
# =========================
APP_DIR = Path(__file__).resolve().parent        # .../src/model
SRC_DIR = APP_DIR.parent                         # .../src
ASSETS_DIR = SRC_DIR / "assets"                  # .../src/assets
DATA_PATH = SRC_DIR / "data" / "processed" / "demog_clean.csv"


# =========================
# CONFIG PÁGINA
# =========================
st.set_page_config(page_title="Life Expectancy Project", layout="wide")


# =========================
# FUNCIONES ÚTILES
# =========================
def show_img(filename: str, caption: str | None = None):
    """Muestra imagen si existe. Si no, avisa sin romper la app."""
    p = ASSETS_DIR / filename
    if p.exists():
        st.image(str(p), caption=caption, use_container_width=True)
    else:
        st.warning(f"⚠️ No existe la imagen: {p.name} (ruta: {p})")


def safe_slider_range(series: pd.Series):
    """
    Evita el error de Streamlit cuando min == max.
    Si min=max, crea un margen pequeño.
    """
    s = pd.to_numeric(series, errors="coerce").dropna()
    if s.empty:
        return 0.0, 1.0
    mn = float(s.min())
    mx = float(s.max())
    if mn == mx:
        eps = 1.0 if mn == 0 else abs(mn) * 0.01
        return mn - eps, mx + eps
    return mn, mx


@st.cache_data
def load_data():
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"No encuentro el archivo: {DATA_PATH}\n"
            "Debe existir: src/data/processed/demog_clean.csv"
        )
    df = pd.read_csv(DATA_PATH)
    df.columns = [c.strip() for c in df.columns]
    return df


# =========================
# HEADER
# =========================
st.title("Envejecimiento poblacional y esperanza de vida")
st.write(
    "Aplicación interactiva para explorar **asociaciones** entre variables demográficas "
    "y la **esperanza de vida** (análisis correlacional, no causal)."
)

# Debug visual: ver qué imágenes detecta
with st.expander("📌 Verificación rápida (para comprobar imágenes y rutas)"):
    st.write("Ruta assets:", str(ASSETS_DIR))
    if ASSETS_DIR.exists():
        st.write("Archivos dentro de src/assets:")
        st.write(sorted([p.name for p in ASSETS_DIR.glob("*")]))
    else:
        st.error("No existe la carpeta src/assets (revisa tu estructura).")

# Portada con 2 columnas
col1, col2 = st.columns([2, 1])
with col2:
    # Cambia por la que te guste más (top_right.png suele verse mejor)
    show_img("top_right.png", caption="Contexto: envejecimiento global")

with col1:
    st.markdown("### Objetivo")
    st.write(
        "- Explorar la evolución y diferencias regionales de esperanza de vida.\n"
        "- Ver relaciones (correlación) entre variables.\n"
        "- Presentar resultados de forma clara para defensa."
    )

st.markdown("---")


# =========================
# CARGA DATOS
# =========================
try:
    df = load_data()
except Exception as e:
    st.error(str(e))
    st.stop()

# Ajuste de nombres comunes
if "region" not in df.columns:
    for alt in ["Region", "entity", "Entity", "location", "Location"]:
        if alt in df.columns:
            df = df.rename(columns={alt: "region"})
            break

if "life_expectancy_total" not in df.columns:
    for alt in ["Life expectancy", "life_expectancy", "value"]:
        if alt in df.columns:
            df = df.rename(columns={alt: "life_expectancy_total"})
            break

# Chequeo mínimo
if "region" not in df.columns or "life_expectancy_total" not in df.columns:
    st.error(
        "Tu dataset no tiene columnas necesarias.\n\n"
        f"Columnas actuales: {list(df.columns)}\n\n"
        "Necesito: 'region' y 'life_expectancy_total' (o equivalentes)."
    )
    st.stop()


# =========================
# SIDEBAR FILTROS
# =========================
st.sidebar.header("Filtros")

regions = sorted(df["region"].dropna().unique().tolist())
default_regions = ["Global"] if "Global" in regions else regions[:1]

selected_regions = st.sidebar.multiselect(
    "Selecciona regiones",
    options=regions,
    default=default_regions
)

df_f = df[df["region"].isin(selected_regions)].copy() if selected_regions else df.copy()


# =========================
# RESUMEN
# =========================
st.header("Resumen global")

c1, c2, c3 = st.columns(3)
c1.metric("Esperanza de vida media", f"{df_f['life_expectancy_total'].mean():.2f}")
c2.metric("Máxima esperanza de vida", f"{df_f['life_expectancy_total'].max():.2f}")
c3.metric("Mínima esperanza de vida", f"{df_f['life_expectancy_total'].min():.2f}")

st.markdown("---")


# =========================
# IMAGENES DE SECCIÓN (opcionales)
# =========================
st.subheader("Apoyo visual")
colA, colB = st.columns(2)
with colA:
    show_img("bottom_left.png", caption="Dataset y preparación")
with colB:
    show_img("bottom_right.png", caption="Análisis y visualizaciones")

st.markdown("---")


# =========================
# HEATMAP CORRELACIÓN
# =========================
st.header("Correlación entre variables")

num_cols = df_f.select_dtypes(include="number").columns.tolist()
if len(num_cols) < 2:
    st.info("No hay suficientes variables numéricas para un heatmap.")
else:
    selected_cols = st.multiselect(
        "Elige variables para el heatmap",
        options=num_cols,
        default=num_cols[:8] if len(num_cols) >= 8 else num_cols
    )

    if len(selected_cols) < 2:
        st.info("Selecciona al menos 2 variables.")
    else:
        corr = df_f[selected_cols].corr(numeric_only=True)
        fig = px.imshow(corr, text_auto=True, aspect="auto", title="Matriz de correlación")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")


# =========================
# TOP REGIONES
# =========================
st.header("Top regiones por esperanza de vida")
top = df_f.sort_values("life_expectancy_total", ascending=False).head(20)

fig_top = px.bar(
    top.sort_values("life_expectancy_total"),
    x="life_expectancy_total",
    y="region",
    orientation="h",
    title="Top 20 regiones (según filtro)"
)
st.plotly_chart(fig_top, use_container_width=True)

st.markdown("---")


# =========================
# SCATTER PRINCIPAL
# =========================
st.header("Relación con esperanza de vida (scatter)")

# Candidatas (si existen)
candidate_x = [
    "under5_mortality",
    "total_deaths",
    "life_expectancy_male",
    "life_expectancy_female",
    "gdp_per_capita",
    "health_exp_pct_gdp",
    "schooling_years",
]
candidate_x = [c for c in candidate_x if c in df_f.columns and c in num_cols]
if not candidate_x:
    candidate_x = [c for c in num_cols if c != "life_expectancy_total"]

x_var = st.selectbox("Variable X", options=candidate_x)

fig_sc = px.scatter(
    df_f,
    x=x_var,
    y="life_expectancy_total",
    hover_name="region",
    title=f"{x_var} vs life_expectancy_total"
)
st.plotly_chart(fig_sc, use_container_width=True)

st.info("Nota: análisis **correlacional** (no causal).")

st.markdown("---")


# =========================
# SCATTER CON FILTRO RANGO (sin romper min=max)
# =========================
st.header("Scatter con filtros por rango (sin errores)")

if len(num_cols) >= 2:
    colx, coly, colc = st.columns(3)

    with colx:
        x2 = st.selectbox("Variable X (rango)", options=num_cols, index=0, key="x2")
    with coly:
        y2 = st.selectbox(
            "Variable Y (rango)",
            options=num_cols,
            index=num_cols.index("life_expectancy_total") if "life_expectancy_total" in num_cols else 1,
            key="y2",
        )
    with colc:
        color2 = st.selectbox("Color opcional", options=["(ninguno)"] + num_cols, key="color2")

    xmn, xmx = safe_slider_range(df_f[x2])
    ymn, ymx = safe_slider_range(df_f[y2])

    xr = st.slider(f"Rango {x2}", min_value=float(xmn), max_value=float(xmx), value=(float(xmn), float(xmx)))
    yr = st.slider(f"Rango {y2}", min_value=float(ymn), max_value=float(ymx), value=(float(ymn), float(ymx)))

    df_r = df_f[(df_f[x2] >= xr[0]) & (df_f[x2] <= xr[1]) & (df_f[y2] >= yr[0]) & (df_f[y2] <= yr[1])].copy()
    st.caption(f"Filas tras filtrar: {len(df_r):,}")

    kwargs = {}
    if color2 != "(ninguno)":
        kwargs["color"] = color2

    fig2 = px.scatter(df_r, x=x2, y=y2, hover_name="region", title=f"{x2} vs {y2}", **kwargs)
    st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")


# =========================
# CONCLUSIONES (lo que pedías)
# =========================
st.header("Conclusiones")

st.write(
    "- La esperanza de vida varía significativamente entre regiones.\n"
    "- Se observan asociaciones entre variables demográficas y esperanza de vida.\n"
    "- El heatmap ayuda a detectar relaciones fuertes (positivas/negativas).\n"
    "- Limitación clave: datos agregados → **correlación ≠ causalidad**.\n"
    "- Aplicación práctica: útil para discutir envejecimiento real (más demanda sanitaria y cuidados de larga duración)."
)

with st.expander("Guion para defensa "):
    st.write(
        "**(1) Contexto :** Envejecimiento global y uso de esperanza de vida como indicador.\n\n"
        "**(2) Datos :** Dataset procesado en `demog_clean.csv`, filtrable por regiones.\n\n"
        "**(3) Visualizaciones :** Resumen, top regiones, correlación (heatmap), scatter.\n\n"
        "**(4) Interpretación :** relaciones asociativas, no causalidad.\n\n"
        "**(5) Cierre :** limitaciones y posibles ampliaciones (gasto sanitario, educación, modelos temporales)."
    )

    )



