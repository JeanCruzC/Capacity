import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title='Workforce & HC por Semana', layout='wide')
st.title('Calculadora de HC Semanal para Call Center')

# --- Parámetros de Contactos y AHT ---
st.sidebar.header('Volumen y AHT por Tipo de Contacto')
vol_calls = st.sidebar.number_input('Volumen de llamadas (por semana)', value=1000, min_value=0)
aht_calls = st.sidebar.number_input('AHT llamadas (minutos)', value=5.0, step=0.1, min_value=0.0)

vol_chats = st.sidebar.number_input('Volumen de chats (por semana)', value=500, min_value=0)
aht_chats = st.sidebar.number_input('AHT chats (minutos)', value=4.0, step=0.1, min_value=0.0)
conc_chats = st.sidebar.number_input('Concurrentes chat', value=2, min_value=1)

vol_emails = st.sidebar.number_input('Volumen de emails (por semana)', value=300, min_value=0)
aht_emails = st.sidebar.number_input('AHT emails (minutos)', value=6.0, step=0.1, min_value=0.0)
conc_emails = st.sidebar.number_input('Concurrentes email', value=1, min_value=1)

# --- Tasas y Shrinkage ---
st.sidebar.header('Tasas y Shrinkage')
productive_rate = st.sidebar.number_input('Productividad (%)', value=85.0, min_value=0.0, max_value=100.0)/100.0
shrinkage = st.sidebar.number_input('Shrinkage (%)', value=20.0, min_value=0.0, max_value=100.0)/100.0

# --- Semana y Perspectiva Semanal ---
st.sidebar.header('Perspectiva de Semanas')
start_week = st.sidebar.number_input('Semana de inicio (1-53)', min_value=1, max_value=53, value=20)
num_weeks = st.sidebar.number_input('Número de semanas a visualizar', min_value=1, max_value=12, value=6)
weeks = [start_week + i for i in range(num_weeks)]

# --- Cálculo de Minutos de Contacto Ajustados ---
min_calls = vol_calls * aht_calls
min_chats = vol_chats * (aht_chats / conc_chats)
min_emails = vol_emails * (aht_emails / conc_emails)

total_contact_mins = min_calls + min_chats + min_emails
required_work_hours = total_contact_mins / 60.0  # horas de trabajo efectivas necesarias

# --- Entrada de HC Actual ---
st.sidebar.header('HC Real: Full-Time y Part-Time')
ft_count = st.sidebar.number_input('Número de Agentes Full-Time', value=10, min_value=0)
pt_count = st.sidebar.number_input('Número de Agentes Part-Time', value=5, min_value=0)
ft_hours = st.sidebar.number_input('Horas semanales FT (horario programado)', value=40.0, step=0.5, min_value=0.0)
pt_hours = st.sidebar.number_input('Horas semanales PT (horario programado)', value=20.0, step=0.5, min_value=0.0)

# --- Cálculos de Horas por Agente ---
# Horas de schedule = horario programado
# Horas de attendance = schedule * (1 - shrinkage)
attendance_ft = ft_hours * (1 - shrinkage)
attendance_pt = pt_hours * (1 - shrinkage)

# Horas productivas = attendance * productividad
productive_ft = attendance_ft * productive_rate
productive_pt = attendance_pt * productive_rate

# Horas in-office = attendance - horas productivas
in_office_ft = attendance_ft - productive_ft
in_office_pt = attendance_pt - productive_pt

# Horas out-office = schedule - attendance
out_office_ft = ft_hours - attendance_ft
out_office_pt = pt_hours - attendance_pt

# Capacidad productiva total (horas efectivas de atención)
capacity_hours = ft_count * productive_ft + pt_count * productive_pt

# Ocupación calculada
occupancy = required_work_hours / capacity_hours if capacity_hours > 0 else np.nan

# --- Resultados Semanales ---
st.header('Requerimiento Semanal de HC')
agents_equiv_ft = required_work_hours / productive_ft if productive_ft>0 else np.nan
weekly_req = {f'Sem {w}': agents_equiv_ft for w in weeks}
df_req = pd.DataFrame([weekly_req], index=['Agentes equivalentes FT'])
st.table(df_req.style.format('{:.2f}'))

# --- Comparativo: HC Calculado vs HC Real ---
st.header('Comparativo de HC y Horas')
col1, col2 = st.columns(2)
with col1:
    st.subheader('HC Calculado (en FT equivalentes)')
    st.metric('Agentes FT equivalentes', f"{agents_equiv_ft:.2f}")
    st.metric('Horas requeridas', f"{required_work_hours:.2f} h")
    st.metric('Ocupación', f"{occupancy:.2%}")
with col2:
    st.subheader('HC Real y Distribución de Horas')
    st.metric('FT Count', ft_count)
    st.metric('PT Count', pt_count)
    st.metric('Capacity Productiva (h)', f"{capacity_hours:.2f} h")

# --- Desglose de Horas por Agente ---
st.header('Desglose Horas por Agente')
df_hours = pd.DataFrame({
    'Tipo': ['Schedule FT', 'Attendance FT', 'Productiva FT', 'In-Office FT', 'Out-Office FT',
             'Schedule PT', 'Attendance PT', 'Productiva PT', 'In-Office PT', 'Out-Office PT'],
    'Horas': [ft_hours, attendance_ft, productive_ft, in_office_ft, out_office_ft,
              pt_hours, attendance_pt, productive_pt, in_office_pt, out_office_pt]
})
fig = px.bar(df_hours, x='Tipo', y='Horas', title='Desglose de Horas por Agente')
st.plotly_chart(fig, use_container_width=True)

st.markdown('---')
st.write('Desarrollado por tu equipo de Workforce con Streamlit.')
