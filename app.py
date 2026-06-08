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
    sintomas_input = st.text_input("Sintomas (ex: febre e dor de cabeça):", value="")
    
    col1, col2 = st.columns(2)
    with col1:
        # Valores zerados por padrão para evitar erros de distração
        idade_input = st.number_input("Idade (anos):", min_value=0, max_value=120, value=0, step=1)
    with col2:
        peso_input = st.number_input("Peso (kg):", min_value=0.0, max_value=200.0, value=0.0, step=0.5)
        
    submit_button = st.form_submit_button("Gerar Opções de Tratamento")

if submit_button:
    if not sintomas_input:
        st.warning("Por favor, informe os sintomas do paciente.")
    elif idade_input == 0 or peso_input == 0.0:
        st.warning("⚠️ Atenção: A idade e o peso devem ser maiores que zero para o cálculo.")
    else:
        sintomas_processados = processar_sintomas(sintomas_input)
        opcoes = buscar_tratamento(sintomas_processados, idade_input, peso_input, df_medicamentos)
        
        if not opcoes:
            st.info("Nenhum tratamento encontrado para estes sintomas na nossa base atual.")
        else:
            st.success(f"✅ {len(opcoes)} opção(ões) encontrada(s)!")
            for opcao in opcoes:
                with st.expander(f"💊 {opcao['principio_ativo']} (Classe: {opcao['classe']})"):
                    st.write(f"**Posologia Base (mg):** {opcao['prescricao']}")
                    st.success(f"**{opcao['apresentacao_final']}**")
                    st.markdown("---")
                    if pd.notna(opcao['alerta_alergia']) and opcao['alerta_alergia']:
                        st.error(f"⚠️ **Alergias:** {opcao['alerta_alergia']}")
                    if pd.notna(opcao['similares']) and opcao['similares']:
                        st.warning(f"🔄 **Evitar Similares:** {opcao['similares']}")

# Botão fora do formulário para resetar a tela rapidamente
st.markdown("---")
if st.button("🔄 Nova Consulta"):
    st.rerun()
