import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title='Workforce Calculator', layout='wide')

st.title('Workforce & HC Calculator')

# --- Input Section ---
st.sidebar.header('Parámetros de Contactos y Horas')
# Contact volumes
vol_calls = st.sidebar.number_input('Volumen de llamadas (unidades)', value=1000, min_value=0)
vol_chats = st.sidebar.number_input('Volumen de chats', value=500, min_value=0)
vol_emails = st.sidebar.number_input('Volumen de emails', value=300, min_value=0)

# AHT per type (minutes)
aht_calls = st.sidebar.number_input('AHT llamadas (minutos)', value=5.0, step=0.1, min_value=0.0)
aht_chats = st.sidebar.number_input('AHT chats (minutos)', value=4.0, step=0.1, min_value=0.0)
aht_emails = st.sidebar.number_input('AHT emails (minutos)', value=6.0, step=0.1, min_value=0.0)

# Horas por agente por período (horas)
sched_hours = st.sidebar.number_input('Horario Programado por agente (h)', value=8.0, step=0.5, min_value=0.0)
attendance_rate = st.sidebar.number_input('Tasa de Attendance (%)', value=95.0, min_value=0.0, max_value=100.0)/100.0
productive_rate = st.sidebar.number_input('Tasa Productiva (%)', value=85.0, min_value=0.0, max_value=100.0)/100.0
transactional_rate = st.sidebar.number_input('Tasa Transaccional (%)', value=75.0, min_value=0.0, max_value=100.0)/100.0

# Occupancy
occupancy = st.sidebar.number_input('Occupancy (%)', value=80.0, min_value=0.0, max_value=100.0)/100.0

# Shrinkage adjustments (e.g., breaks, trainings)
shrinkage = st.sidebar.number_input('Shrinkage (%)', value=20.0, min_value=0.0, max_value=100.0)/100.0

# Puerto para cálculo inverso
st.sidebar.header('Cálculo Inverso: Horas a Agentes')
inv_type = st.sidebar.selectbox('Tipo de hora', ['Schedule', 'Attendance', 'Productiva', 'Transaccional'])
inv_hours = st.sidebar.number_input('Total horas disponibles', value=100.0, min_value=0.0)

# --- Cálculos Principales ---
# Total minutos de contacto
min_calls = vol_calls * aht_calls
min_chats = vol_chats * aht_chats
min_emails = vol_emails * aht_emails

total_contact_mins = min_calls + min_chats + min_emails

# Horas requeridas de trabajo efectivo (service minutes / occupancy)
required_work_mins = total_contact_mins / occupancy
required_work_hours = required_work_mins / 60.0

# Ajuste por tasas y shrinkage para pasar de horas efectivas a agentes
# Effective hours per agent
eff_hours_per_agent = sched_hours * attendance_rate * productive_rate * (1 - shrinkage)

# Required agents
agents_required = required_work_hours / eff_hours_per_agent

# --- Resumen de Métricas ---
st.header('Resumen de Cálculos')
metrics = {
    'Total Contact Minutes': total_contact_mins,
    'Required Work Hours': required_work_hours,
    'Effective Hours/Agent': eff_hours_per_agent,
    'Agentes Requeridos': agents_required
}

st.metric('Agentes Requeridos', f"{agents_required:.2f}")
st.write(pd.DataFrame.from_dict(metrics, orient='index', columns=['Valor']).style.format('{:.2f}'))

# --- Visualizaciones ---
st.header('Visualizaciones de Horas y Tasas')

# Dataframe para gráfica
df_vis = pd.DataFrame({
    'Métrica': ['Schedule Hours', 'Attendance Hours', 'Productive Hours', 'Transactional Hours'],
    'Horas': [
        agents_required * sched_hours,
        agents_required * sched_hours * attendance_rate,
        agents_required * sched_hours * attendance_rate * productive_rate,
        agents_required * sched_hours * attendance_rate * transactional_rate,
    ]
})

fig = px.bar(df_vis, x='Métrica', y='Horas', title='Distribución de Horas por Métrica')
st.plotly_chart(fig, use_container_width=True)

# In-office vs Out-office (ejemplo split)
in_office = df_vis.loc[df_vis['Métrica']=='Productive Hours', 'Horas'].values[0]
out_office = df_vis.loc[df_vis['Métrica']=='Schedule Hours', 'Horas'].values[0] - in_office

st.subheader('In-office vs Out-office')
col1, col2 = st.columns(2)
col1.metric('In-office Hours', f"{in_office:.2f}")
col2.metric('Out-office Hours', f"{out_office:.2f}")

# --- Cálculo Inverso ---
st.header('Cálculo Inverso: Horas -> Agentes')
if inv_type == 'Schedule':
    inv_agent = inv_hours / sched_hours
elif inv_type == 'Attendance':
    inv_agent = inv_hours / (sched_hours * attendance_rate)
elif inv_type == 'Productiva':
    inv_agent = inv_hours / (sched_hours * attendance_rate * productive_rate)
else:
    inv_agent = inv_hours / (sched_hours * attendance_rate * transactional_rate)

st.write(f"Agentes necesarios para {inv_hours:.2f}h de {inv_type}: **{inv_agent:.2f}**")

st.markdown('---')
st.write('Desarrollado por tu equipo de Workforce en Streamlit.')
