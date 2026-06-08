import streamlit as st
from supabase import create_client, Client
from robo_ia import diagnostico_autonomo_completo

# 1. CONFIGURAÇÃO VISUAL (Agora em layout 'wide' para caber a barra lateral)
st.set_page_config(page_title="Lumina Med", page_icon="⚕️", layout="wide")

st.markdown("""
<style>
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
    .stTextInput textarea, .stNumberInput input {
        border-radius: 4px !important;
    }
</style>
""", unsafe_allow_html=True)

# 2. CHAVES DE SEGURANÇA E CONEXÃO SUPABASE
chaves_api = {
    "openai": st.secrets.get("OPENAI_API_KEY", ""),
    "gemini": st.secrets.get("GEMINI_API_KEY", ""),
    "groq": st.secrets.get("GROQ_API_KEY", ""),
    "openrouter": st.secrets.get("OPENROUTER_API_KEY", "")
}

SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")

@st.cache_resource
def iniciar_banco() -> Client:
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Só tenta conectar se as chaves existirem
supabase = iniciar_banco() if SUPABASE_URL and SUPABASE_KEY else None

# 3. PAINEL LATERAL DE HISTÓRICO
with st.sidebar:
    st.header("🕰️ Histórico de Atendimentos")
    st.markdown("---")
    
    if supabase:
        try:
            # Busca as 5 consultas mais recentes
            resposta = supabase.table("historico_consultas").select("*").order("created_at", desc=True).limit(5).execute()
            registros = resposta.data
            
            if not registros:
                st.info("Nenhuma consulta registrada.")
            else:
                for reg in registros:
                    with st.expander(f"👤 {reg['idade']} anos | {reg['peso']}kg"):
                        st.write(f"**Sintomas:** {reg['sintomas']}")
                        st.write(f"**Motor IA:** `{reg.get('provedor', 'Desconhecido')}`")
        except Exception as e:
            st.error("Aguardando criação da tabela no Supabase...")
    else:
        st.warning("Banco de dados não conectado.")

# 4. ENGENHARIA DE LIMPEZA DE MEMÓRIA
def limpar_consulta():
    st.session_state['sintomas_chave'] = ""
    st.session_state['idade_chave'] = None
    st.session_state['peso_chave'] = None

if 'sintomas_chave' not in st.session_state:
    st.session_state['sintomas_chave'] = ""
if 'idade_chave' not in st.session_state:
    st.session_state['idade_chave'] = None
if 'peso_chave' not in st.session_state:
    st.session_state['peso_chave'] = None

# 5. TELA PRINCIPAL
st.title("⚕️ Lumina Med")
st.markdown("---")

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
                
                # 6. SALVAMENTO AUTOMÁTICO NO BANCO DE DADOS
                if supabase:
                    try:
                        novo_registro = {
                            "sintomas": st.session_state['sintomas_chave'],
                            "idade": st.session_state['idade_chave'],
                            "peso": st.session_state['peso_chave'],
                            "prontuario": veredito,
                            "provedor": telemetria.get("Provedor Usado", "Desconhecido")
                        }
                        supabase.table("historico_consultas").insert(novo_registro).execute()
                    except Exception as e:
                        st.toast("Não foi possível salvar o histórico. Verifique a tabela no Supabase.")

st.markdown("---")
st.button("Nova Consulta", on_click=limpar_consulta)
