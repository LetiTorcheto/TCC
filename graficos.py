import streamlit as st
import pandas as pd
import requests
from streamlit_echarts import st_pyecharts
from pyecharts.charts import Line
from pyecharts import options as opts


@st.cache_data
def data_coletas():
    requisicao = requests.get("https://metlab.rexlab.ufsc.br/api/dados")
    dados = requisicao.json()['coletas']
    df = pd.DataFrame(dados)
    df['dataDoEnvio'] = pd.to_datetime(df['dataDoEnvio'])
    return df
df = data_coletas()

st.sidebar.header("Filtragem de Dados por Data")
data_inicio = st.sidebar.date_input("Data de Início", df['dataDoEnvio'].min().date())
data_fim = st.sidebar.date_input("Data de Fim", df['dataDoEnvio'].max().date())


df_filtrado = df[(df['dataDoEnvio'].dt.date >= data_inicio) & (df['dataDoEnvio'].dt.date <= data_fim)]

sensores = ["temperatura", "umidadeAr", "umidadeSolo", "pressao", "iluminacao", 
            "nivelUV", "alcool", "tolueno", "acetona", "NH4", "CO", "CO2"]

sensor_selecionado = st.selectbox("Selecione o sensor para visualização", sensores)

def plot_sensor_data(sensor):
    line_chart = (
        Line()
        .add_xaxis(df_filtrado['dataDoEnvio'].dt.strftime("%Y-%m-%d %H:%M:%S").tolist())
        .add_yaxis(sensor, df_filtrado[sensor].tolist(), is_smooth=True)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"Leitura do Sensor: {sensor.capitalize()} - {data_inicio} até {data_fim}"),
            xaxis_opts=opts.AxisOpts(name="Data e Hora da Coleta", type_="category"),
            yaxis_opts=opts.AxisOpts(name=sensor.capitalize()),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            datazoom_opts=[opts.DataZoomOpts(type_="slider", range_start=0, range_end=100)],
        )
    )
    return line_chart


if not df_filtrado.empty:
    st_pyecharts(plot_sensor_data(sensor_selecionado))
else:
    st.write("Nenhuma coleta encontrada para o intervalo de datas selecionado.")
