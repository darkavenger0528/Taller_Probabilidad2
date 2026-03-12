import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tiempos de desplazamiento", layout="centered")

st.title("Taller: Probabilidad aplicada a movilidad urbana")
st.write("Análisis de tiempos de desplazamiento de estudiantes hacia la universidad.")

@st.cache_data
def cargar_datos(ruta_excel: str) -> pd.DataFrame:
    df = pd.read_excel(ruta_excel)
    # Ajusta estos nombres según aparezcan exactamente en tu archivo
    df.columns = [
        "marca_temporal",
        "localidad",
        "medio_transporte",
        "tiempo_pico",
        "tiempo_valle",
    ]
    # Asegurar que los tiempos sean numéricos
    df["tiempo_pico"] = pd.to_numeric(df["tiempo_pico"], errors="coerce")
    df["tiempo_valle"] = pd.to_numeric(df["tiempo_valle"], errors="coerce")
    df = df.dropna(subset=["tiempo_pico", "tiempo_valle"])
    return df

# Carga de datos
ruta_archivo = "Workshop-Inferentaial-Stadistics-3.xlsx"
st.sidebar.header("Configuración de datos")
st.sidebar.write(f"Usando archivo: `{ruta_archivo}`")

df = cargar_datos(ruta_archivo)

st.subheader("Vista de los datos originales")
st.dataframe(df.head())

# Controles de usuario
st.sidebar.header("Parámetros de análisis")

opcion_hora = st.sidebar.radio(
    "Selecciona el tipo de tiempo a analizar",
    ("Horas pico", "Horas valle"),
)

columna_tiempo = "tiempo_pico" if opcion_hora == "Horas pico" else "tiempo_valle"

medios = ["Todos"] + sorted(df["medio_transporte"].unique())
medio_sel = st.sidebar.selectbox(
    "Filtrar por medio de transporte",
    medios,
)

if medio_sel != "Todos":
    df_filtrado = df[df["medio_transporte"] == medio_sel]
else:
    df_filtrado = df.copy()

st.markdown(
    f"### Distribución de tiempos de desplazamiento ({opcion_hora.lower()})"
    + (f" - Medio: **{medio_sel}**" if medio_sel != "Todos" else "")
)

st.write(f"Número de observaciones en el filtro actual: {len(df_filtrado)}")

# Cálculo de frecuencia, probabilidad y probabilidad acumulada
frecuencias = (
    df_filtrado[columna_tiempo]
    .value_counts()
    .sort_index()
)

tabla = pd.DataFrame({
    "Tiempo_minutos": frecuencias.index,
    "Frecuencia": frecuencias.values
})
tabla["Probabilidad"] = tabla["Frecuencia"] / tabla["Frecuencia"].sum()
tabla["Probabilidad_acumulada"] = tabla["Probabilidad"].cumsum()

st.subheader("Tabla de distribución de probabilidad empírica")
st.dataframe(tabla)

# Ejemplo de cálculo de probabilidad para un umbral seleccionado
st.subheader("Probabilidad acumulada hasta un umbral")

min_t, max_t = int(tabla["Tiempo_minutos"].min()), int(tabla["Tiempo_minutos"].max())
umbral = st.slider(
    "Selecciona un tiempo (en minutos) para calcular P(X ≤ umbral)",
    min_value=min_t,
    max_value=max_t,
    value=min_t,
    step=1,
)

prob_acum_hasta_umbral = tabla.loc[
    tabla["Tiempo_minutos"] <= umbral, "Probabilidad"
].sum()

st.write(
    f"La probabilidad de tardar **menos o igual que {umbral} minutos** "
    f"es aproximadamente **{prob_acum_hasta_umbral:.2f}**."
)

# Histograma / gráfico de barras
st.subheader("Histograma de tiempos de desplazamiento")

fig = px.bar(
    tabla,
    x="Tiempo_minutos",
    y="Frecuencia",
    labels={
        "Tiempo_minutos": "Tiempo de desplazamiento (minutos)",
        "Frecuencia": "Frecuencia",
    },
    title=f"Histograma de tiempos ({opcion_hora.lower()})",
)
st.plotly_chart(fig, use_container_width=True)

# También se puede mostrar en términos de probabilidad
st.subheader("Distribución en términos de probabilidad")

fig_prob = px.bar(
    tabla,
    x="Tiempo_minutos",
    y="Probabilidad",
    labels={
        "Tiempo_minutos": "Tiempo de desplazamiento (minutos)",
        "Probabilidad": "Probabilidad empírica",
    },
    title=f"Distribución de probabilidad ({opcion_hora.lower()})",
)
st.plotly_chart(fig_prob, use_container_width=True)
