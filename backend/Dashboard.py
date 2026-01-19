#Importaciones
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

#Configuración
st.set_page_config(page_title="Dashboard de Métricas Ambientales (streaming)", page_icon="🌍", layout="wide")

# Constantes
np.random.seed(42)
METRICS = ['Humedad', 'Temperatura', 'Presión', 'Velocidad del Viento']
WINDOW_SECONDS = 120  # ventana mostrada en segundos

# Escalas de ruido y amplitudes por métrica (ajusta para más/menos movimiento)
NOISE_SCALE = {
    'Humedad': 2.5,
    'Temperatura': 0.8,
    'Presión': 1.2,
    'Velocidad del Viento': 1.5
}
SEASONAL_AMP = {
    'Humedad': 6.0,
    'Temperatura': 3.0,
    'Presión': 0.8,
    'Velocidad del Viento': 2.5
}
SEASONAL_FREQ = 1 / 60  # ciclos por segundo (baja frecuencia para notar oscilaciones)

# Título
st.title("🌍 Dashboard de Métricas Ambientales (streaming por segundo)")
st.subheader("Datos sintéticos actualizándose cada segundo")
st.markdown("---")

# Sidebar: filtros
st.sidebar.header("Filtros")
Metrica_seleccionada = st.sidebar.multiselect(
    "Selecciona las métricas a visualizar",
    options=METRICS,
    default=["Humedad"]
)
streaming = st.sidebar.checkbox("Streaming (actualizar cada segundo)", value=True)

# Autorefresh cada 1000 ms para re-ejecutar el script y actualizar la gráfica
st_autorefresh(interval=1000, key="autorefresh")

# Inicializar dataframe y valores previos en session_state
if 'df_stream' not in st.session_state:
    st.session_state.df_stream = pd.DataFrame(columns=['Fecha'] + METRICS)
if 'prev_values' not in st.session_state:
    st.session_state.prev_values = {m: float(np.random.uniform(20, 70)) for m in METRICS}

# Añadir una muestra por ejecución si el streaming está activado
if streaming:
    now = pd.to_datetime(datetime.now())
    t = now.timestamp()
    new_row = {'Fecha': now}
    for m in METRICS:
        prev = st.session_state.prev_values.get(m, float(np.random.uniform(20, 70)))
        noise = np.random.normal(scale=NOISE_SCALE.get(m, 1.0))
        seasonal = SEASONAL_AMP.get(m, 0) * np.sin(2 * np.pi * SEASONAL_FREQ * t)
        val = prev + noise + seasonal
        val = float(np.clip(val, 0, 200))  # límite razonable
        new_row[m] = val
        st.session_state.prev_values[m] = val

    st.session_state.df_stream = pd.concat([st.session_state.df_stream, pd.DataFrame([new_row])], ignore_index=True)
    cutoff = now - pd.Timedelta(seconds=WINDOW_SECONDS)
    st.session_state.df_stream = st.session_state.df_stream[st.session_state.df_stream['Fecha'] >= cutoff].reset_index(drop=True)

# Mostrar warning si no hay métricas seleccionadas
if len(Metrica_seleccionada) == 0:
    st.warning("Selecciona al menos una métrica para visualizar.")
else:
    # Preparar datos a graficar (usar todo lo almacenado en session_state)
    df_recent = st.session_state.df_stream.copy()
    if not df_recent.empty:
        df_recent['Fecha'] = pd.to_datetime(df_recent['Fecha'])
        # Asegurar que las métricas solicitadas existen en el dataframe
        cols = [c for c in Metrica_seleccionada if c in df_recent.columns]
        if len(cols) == 0:
            st.info("Las métricas seleccionadas no están disponibles todavía.")
        else:
            # Convertir a formato largo para evitar error de tipos mixtos
            df_plot = df_recent[["Fecha"] + cols].melt(
                id_vars='Fecha', var_name='Métrica', value_name='Valor'
            )
            df_plot['Valor'] = pd.to_numeric(df_plot['Valor'], errors='coerce')
            df_plot = df_plot.dropna(subset=['Valor'])
            if df_plot.empty:
                st.info("No hay valores numéricos para graficar aún.")
            else:
                fig = px.line(
                    df_plot,
                    x='Fecha',
                    y='Valor',
                    color='Métrica',
                    title=f"Métricas (últimos {WINDOW_SECONDS}s)"
                )
                fig.update_layout(legend_title_text='Métricas', xaxis_title='Tiempo', yaxis_title='Valor')
                fig.update_traces(line=dict(width=2))
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Esperando datos...")