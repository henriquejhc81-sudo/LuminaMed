import streamlit as st
from robo_ia import diagnostico_autonomo_completo

# 1. CONFIGURAÇÃO VISUAL E INJEÇÃO DE CSS MODERNO
st.set_page_config(page_title="Lumina Med", page_icon="⚕️", layout="centered")

st.markdown("""
<style>
    /* Estilo Cyberpunk Minimalista para os botões */
    div.stButton > button {
        background-color: transparent;
        color: #00ff99;
        border: 1px solid #00ff99;
        border-radius: 4px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
    }
    div.stButton > button:hover {
        background-color: #00ff99;
        color: #0e1117;
        box-shadow: 0 0 15px #00ff99;
    }
    /* Limpeza das bordas dos inputs */
    .stTextInput textarea, .stNumberInput input {
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚕️ Lumina Med")
st.markdown("---")

chaves_api = {
    "openai": st.secrets.get("OPENAI_KEY", ""),
    "gemini": st.secrets.get("GEMINI_KEY", ""),
    "groq": st.secrets.get("GROQ_KEY", "")
}

def limpar_consulta():
    st.session_state.clear()

with st.form("form_paciente"):
    # Label direto, sem placeholder e sem títulos poluindo a tela
    sintomas_input = st.text_area("Descreva o quadro do paciente:", value="", placeholder="", key="sintomas_chave")
    
    col1, col2 = st.columns(2)
    with col1:
        idade_input = st.number_input("Idade (anos):", min_value=0, max_value=120, value=None, step=1, key="idade_chave")
    with col2:
        peso_input = st.number_input("Peso (kg):", min_value=0.0, max_value=200.0, value=None, step=0.5, key="peso_chave")
        
    submit_button = st.form_submit_button("Gerar Prescrição Autônoma")

if submit_button:
    if not sintomas_input or idade_input is None or peso_input is None:
        st.error("⚠️ Preencha o quadro clínico, a idade e o peso do paciente.")
    else:
        with st.spinner("🧠 Orquestrando junta médica (OpenAI, Gemini, Groq)..."):
            
            opinioes_individuais, veredito = diagnostico_autonomo_completo(sintomas_input, idade_input, peso_input, chaves_api)
            
            if not opinioes_individuais:
                st.error("Falha de comunicação com as IAs. Verifique suas chaves no painel Secrets.")
            else:
                st.success("✅ Veredito Clínico finalizado.")
                
                # Exibe o resultado do Juiz em destaque
                st.markdown("### 📋 Prontuário Unificado (Veredito do Juiz)")
                st.info(veredito)
                
                st.markdown("---")
                st.markdown("#### 🔍 Pareceres Individuais (Bastidores)")
                for provedor, texto in opinioes_individuais.items():
                    with st.expander(f"Parecer Base: {provedor}"):
                        st.write(texto)

st.markdown("---")
st.button("Nova Consulta", on_click=limpar_consulta)
