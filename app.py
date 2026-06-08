import streamlit as st
import pandas as pd
from motor_clinico import carregar_dados, processar_sintomas, buscar_tratamento
from robo_ia import analisar_consenso

# 1. CONFIGURAÇÃO VISUAL DA INTERFACE
st.set_page_config(page_title="Lumina Med - Nexus", page_icon="⚕️", layout="centered")

st.title("⚕️ Lumina Med - V6 DoctorBot")
st.subheader("Sistema Inteligente de Suporte à Prescrição")
st.markdown("---")

# 2. CARREGAMENTO DO BANCO DE DADOS LÓGICO
df_medicamentos = carregar_dados()

# 3. RECUPERAÇÃO DAS CHAVES DE API DO COFRE DE SEGURANÇA (SECRETS)
chaves_api = {
    "openai": st.secrets.get("OPENAI_KEY", ""),
    "gemini": st.secrets.get("GEMINI_KEY", ""),
    "groq": st.secrets.get("GROQ_KEY", ""),
    "openrouter": st.secrets.get("OPENROUTER_KEY", "")
}

# 4. GERENCIAMENTO DE ESTADO (PREVINE A RETENÇÃO DE DADOS ANTIGOS)
if 'idade' not in st.session_state:
    st.session_state.idade = 0
if 'peso' not in st.session_state:
    st.session_state.peso = 0.0
if 'sintomas' not in st.session_state:
    st.session_state.sintomas = ""

def limpar_consulta():
    st.session_state.idade = 0
    st.session_state.peso = 0.0
    st.session_state.sintomas = ""

# 5. FORMULÁRIO CENTRALIZADO DO PACIENTE
with st.form("form_paciente"):
    st.write("📋 **Dados do Paciente**")
    
    sintomas_input = st.text_area(
        "Descreva o quadro do paciente de forma natural:", 
        value=st.session_state.sintomas, 
        placeholder="Ex: Criança com dor de garganta muito forte, febre alta e alergia a dipirona..."
    )
    
    col1, col2 = st.columns(2)
    with col1:
        idade_input = st.number_input("Idade (anos):", min_value=0, max_value=120, value=st.session_state.idade, step=1)
    with col2:
        peso_input = st.number_input("Peso (kg):", min_value=0.0, max_value=200.0, value=st.session_state.peso, step=0.5)
        
    submit_button = st.form_submit_button("Consultar DoctorBot")

# 6. PROCESSAMENTO E EXIBIÇÃO DOS RESULTADOS
if submit_button:
    # Sincroniza as entradas com o estado da sessão
    st.session_state.sintomas = sintomas_input
    st.session_state.idade = idade_input
    st.session_state.peso = peso_input

    if not sintomas_input:
        st.warning("Por favor, descreva os sintomas do paciente para iniciar.")
    elif idade_input == 0 or peso_input == 0.0:
        st.warning("⚠️ Atenção: A idade e o peso devem ser maiores que zero para o cálculo posológico correto.")
    else:
        # QUADRO A: Painel Cognitivo (Consenso das Inteligências Artificiais)
        with st.spinner("🧠 Junta médica analisando o relato (OpenAI, Gemini, Groq)..."):
            analise_das_ias = analisar_consenso(sintomas_input, chaves_api)
            
            st.info("💡 **Parecer Técnico da Junta de IAs:**")
            for i, resposta in enumerate(analise_das_ias):
                if resposta:
                    st.markdown(f"**Agente de Diagnóstico {i+1}:**")
                    st.write(resposta)
                    st.markdown("---")
            
        # QUADRO B: Validação Lógica Estrita (Cálculos Determinísticos do CSV)
        sintomas_processados = processar_sintomas(sintomas_input)
        opcoes = buscar_tratamento(sintomas_processados, idade_input, peso_input, df_medicamentos)
        
        if not opcoes:
            st.info("Nenhum protocolo clínico rígido correspondente foi localizado no banco de dados para este quadro.")
        else:
            st.success(f"✅ {len(opcoes)} protocolo(s) de tratamento seguro(s) encontrado(s) na base!")
            for opcao in opcoes:
                with st.expander(f"💊 {opcao['principio_ativo']} (Classe: {opcao['classe']})"):
                    st.write(f"**Posologia Base (mg):** {opcao['prescricao']}")
                    st.success(f"**{opcao['apresentacao_final']}**")
                    
                    if pd.notna(opcao['alerta_alergia']) and opcao['alerta_alergia']:
                        st.error(f"⚠️ **Alergias:** {opcao['alerta_alergia']}")
                    if pd.notna(opcao['similares']) and opcao['similares']:
                        st.warning(f"🔄 **Evitar Similares:** {opcao['similares']}")

# 7. MECANISMO DE RESET (LIMPEZA TOTAL DO ESTADO)
st.markdown("---")
if st.button("🔄 Nova Consulta", on_click=limpar_consulta):
    st.rerun()
