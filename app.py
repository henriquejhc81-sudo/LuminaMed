import streamlit as st
import pandas as pd
from motor_clinico import carregar_dados, processar_sintomas, buscar_tratamento

st.set_page_config(page_title="Lumina Med - Nexus", page_icon="⚕️", layout="centered")
st.title("⚕️ Lumina Med")
st.subheader("Sistema Inteligente de Suporte à Prescrição")
st.markdown("---")

df_medicamentos = carregar_dados()

with st.form("form_paciente"):
    st.write("📋 **Dados do Paciente**")
    sintomas_input = st.text_input("Sintomas (ex: febre e dor de cabeça):")
    col1, col2 = st.columns(2)
    with col1:
        idade_input = st.number_input("Idade (anos):", min_value=0, max_value=120, value=8)
    with col2:
        peso_input = st.number_input("Peso (kg):", min_value=1.0, max_value=200.0, value=25.0)
    submit_button = st.form_submit_button("Gerar Opções de Tratamento")

if submit_button:
    if not sintomas_input:
        st.warning("Por favor, informe os sintomas do paciente.")
    else:
        sintomas_processados = processar_sintomas(sintomas_input)
        opcoes = buscar_tratamento(sintomas_processados, idade_input, peso_input, df_medicamentos)
        
        if not opcoes:
            st.info("Nenhum tratamento encontrado para estes sintomas na nossa base atual.")
        else:
            st.success(f"✅ {len(opcoes)} opção(ões) encontrada(s)!")
            for opcao in opcoes:
                with st.expander(f"💊 {opcao['principio_ativo']} (Classe: {opcao['classe']})"):
                    st.write(f"**Posologia:** {opcao['prescricao']}")
                    st.markdown("---")
                    if pd.notna(opcao['alerta_alergia']) and opcao['alerta_alergia']:
                        st.error(f"⚠️ **Alergias:** {opcao['alerta_alergia']}")
                    if pd.notna(opcao['similares']) and opcao['similares']:
                        st.warning(f"🔄 **Evitar Similares:** {opcao['similares']}")
