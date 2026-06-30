import streamlit as st
import pandas as pd
import os

# 1. CONFIGURAÇÃO DA INTERFACE (O Padrão Premium)
st.set_page_config(
    page_title="Lumina Med - CDSS Advanced",
    page_icon="⚕️",
    layout="wide", # Expandindo para tela cheia (dashboard hospitalar)
    initial_sidebar_state="collapsed"
)

# Injeção de CSS para um acabamento moderno e botões responsivos
st.markdown("""
    <style>
    /* Estilizando o botão principal para um azul médico vibrante */
    div.stButton > button:first-child {
        background-color: #0056b3;
        color: white;
        border-radius: 8px;
        height: 3em;
        font-weight: 600;
        transition: all 0.3s ease;
        width: 100%;
        border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #003d82;
        border: 1px solid #00bfff;
        box-shadow: 0px 0px 15px rgba(0, 191, 255, 0.4);
    }
    /* Ajustes finos nos inputs */
    .stTextInput > div > div > input, .stTextArea > div > textarea, .stNumberInput > div > div > input {
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CABEÇALHO
st.title("⚕️ Lumina Med")
st.markdown("### **Terminal Clínico CDSS Advanced** | Auditoria e Triagem Inteligente")
st.divider()

# 3. MÓDULO DE TRIAGEM PRINCIPAL (Organizado em Colunas)
st.markdown("#### 📋 ETAPA 1: Triagem e Histórico")

col1, col2 = st.columns([2, 1])

with col1:
    motivo = st.text_area("Quadro clínico OU Nome do medicamento (ex: Infecção urinária, Amoxicilina):", height=120)

with col2:
    uso_continuo = st.text_input("Uso contínuo (ex: Losartana):")
    alergias = st.text_input("⚠️ Alergias (ex: Ibuprofeno):", help="O motor cruzará a família ATC automaticamente para bloquear riscos.")

st.markdown("#### 🧬 Perfil Biométrico")
bio_col1, bio_col2, bio_col3, bio_col4 = st.columns(4)

with bio_col1:
    idade = st.number_input("Idade:", min_value=0, max_value=120, step=1)
with bio_col2:
    peso = st.number_input("Peso (kg):", min_value=0.0, max_value=300.0, step=0.1)
with bio_col3:
    sexo = st.selectbox("Sexo Biológico:", ["Masculino", "Feminino"])
with bio_col4:
    creatinina = st.number_input("Creatinina (mg/dL) - Opc.:", min_value=0.0, max_value=15.0, step=0.1, help="Para ajuste automático de Clearance Renal.")

# 4. SINAIS VITAIS E COMORBIDADES (A Evolução Oculta/Opcional)
st.markdown("---")
with st.expander("🩺 Sinais Vitais e Comorbidades (Avançado - Opcional)", expanded=False):
    st.info("Preencha apenas o que estiver disponível na triagem. O Algoritmo Juiz usará estes dados para refinar o cruzamento de riscos.")
    
    vit_col1, vit_col2, vit_col3 = st.columns(3)
    with vit_col1:
        pressao = st.text_input("Pressão Arterial (ex: 120/80):", placeholder="Opcional")
    with vit_col2:
        glicemia = st.number_input("Glicemia (mg/dL):", min_value=0, max_value=1000, step=1, value=0, help="Deixe 0 se não medido.")
    with vit_col3:
        temperatura = st.number_input("Temperatura (°C):", min_value=30.0, max_value=45.0, step=0.1, value=36.5)
        
    comorbidades = st.multiselect(
        "Selecione Comorbidades Preexistentes:",
        ["Hipertensão", "Diabetes Tipo 1", "Diabetes Tipo 2", "Asma", "Insuficiência Renal", "Insuficiência Cardíaca", "Doença Hepática", "DPOC"]
    )

st.markdown("---")

# Botão de Ação Centralizado
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    iniciar_analise = st.button("🔍 Iniciar Auditoria Farmacológica")

if iniciar_analise:
    st.success("Motor de dados ativado. Aguardando integração do backend...")
    # A lógica do backend de cruzamento ATC e LLM entrará aqui
