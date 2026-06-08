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
    /* Limpeza das bordas das caixas de texto */
    .stTextInput textarea, .stNumberInput input {
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚕️ Lumina Med")
st.markdown("---")

# 2. CHAVES DE SEGURANÇA (O COFRE COMPLETO)
chaves_api = {
    "openai": st.secrets.get("OPENAI_API_KEY", ""),
    "gemini": st.secrets.get("GEMINI_API_KEY", ""),
    "groq": st.secrets.get("GROQ_API_KEY", ""),
    "openrouter": st.secrets.get("OPENROUTER_API_KEY", ""),
    "supabase_url": st.secrets.get("SUPABASE_URL", ""),
    "supabase_key": st.secrets.get("SUPABASE_KEY", "")
}

# 3. NOVA ENGENHARIA DE LIMPEZA DE MEMÓRIA
def limpar_consulta():
    st.session_state['sintomas_chave'] = ""
    st.session_state['idade_chave'] = None
    st.session_state['peso_chave'] = None

# Inicializa as variáveis na memória se for a primeira vez
if 'sintomas_chave' not in st.session_state:
    st.session_state['sintomas_chave'] = ""
if 'idade_chave' not in st.session_state:
    st.session_state['idade_chave'] = None
if 'peso_chave' not in st.session_state:
    st.session_state['peso_chave'] = None

# 4. INTERFACE DO USUÁRIO
with st.form("form_paciente"):
    sintomas_input = st.text_area("Descreva o quadro clínico do paciente:", key="sintomas_chave")
    
    col1, col2 = st.columns(2)
    with col1:
        idade_input = st.number_input("Idade (anos):", min_value=0, max_value=120, step=1, key="idade_chave")
    with col2:
        peso_input = st.number_input("Peso (kg):", min_value=0.0, max_value=200.0, step=0.5, key="peso_chave")
        
    submit_button = st.form_submit_button("Gerar Prescrição Autônoma")

if submit_button:
    if not st.session_state['sintomas_chave'] or st.session_state['idade_chave'] is None or st.session_state['peso_chave'] is None:
        st.error("⚠️ Preencha o quadro clínico, a idade e o peso do paciente para prosseguir.")
    else:
        with st.spinner("🧠 A orquestrar a junta médica (Healer Engine, Auditoria e ANVISA)..."):
            
            telemetria, veredito = diagnostico_autonomo_completo(
                st.session_state['sintomas_chave'], 
                st.session_state['idade_chave'], 
                st.session_state['peso_chave'], 
                chaves_api
            )
            
            if not telemetria:
                st.error(veredito)
            else:
                st.success("✅ Veredito Clínico finalizado, auditado e validado!")
                st.markdown("### 📋 Prontuário Unificado e Seguro")
                st.info(veredito)

st.markdown("---")
# O botão agora chama a nossa função de limpeza forçada
st.button("Nova Consulta", on_click=limpar_consulta)
