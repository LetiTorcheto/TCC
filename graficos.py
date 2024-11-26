import streamlit as st
import pandas as pd
import requests
from streamlit_echarts import st_pyecharts
from pyecharts.charts import Line
from pyecharts import options as opts
import pytz 



@st.cache_data
def data_coletas():
    requisicao = requests.get("https://metlab.rexlab.ufsc.br/api/dados?qntPorPag=10000")
    dados = requisicao.json()['coletas']
    df = pd.DataFrame(dados)
    df['dataDoEnvio'] = pd.to_datetime(df['dataDoEnvio'])
    return df

df = data_coletas()

st.sidebar.header("Filtragem de Dados por Data e Horário")

# Filtro por data
data_inicio = st.sidebar.date_input("Data de Início", df['dataDoEnvio'].min().date())
data_fim = st.sidebar.date_input("Data de Fim", df['dataDoEnvio'].max().date())

# Filtro por horário
timezone = pytz.UTC
horario_inicio = st.sidebar.time_input("Horário de início filtrado ", value=pd.Timestamp.min.time())
horario_fim = st.sidebar.time_input("Horário de fim filtrado", value=pd.Timestamp.max.time())

# Combina data e horário 
datetime_inicio = timezone.localize(pd.Timestamp(f"{data_inicio} {horario_inicio}"))
datetime_fim = timezone.localize(pd.Timestamp(f"{data_fim} {horario_fim}"))


# Filtra o DataFrame
df_filtrado = df[(df['dataDoEnvio'] >= datetime_inicio) & (df['dataDoEnvio'] <= datetime_fim)]

# Seleção do sensor
sensores = ["temperatura", "umidadeAr", "umidadeSolo", "pressao", "iluminacao", 
            "nivelUV", "alcool", "tolueno", "acetona", "NH4", "CO", "CO2"]

sensor_selecionado = st.selectbox("Selecione o sensor para visualização", sensores)

def plot_sensor_data(sensor):
    line_chart = (
        Line()
        .add_xaxis(df_filtrado['dataDoEnvio'].dt.strftime("%Y-%m-%d %H:%M:%S").tolist())
        .add_yaxis(sensor, df_filtrado[sensor].tolist(), is_smooth=True)
        .set_global_opts(
            title_opts=opts.TitleOpts(title=f"Leitura do Sensor: {sensor.capitalize()} - {datetime_inicio} até {datetime_fim}"),
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
    st.write("Nenhuma coleta encontrada para o intervalo de datas e horários selecionado.")
