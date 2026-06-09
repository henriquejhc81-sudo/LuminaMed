import streamlit as st
from robo_ia import listar_opcoes_tratamento, gerar_prontuario_final

# CONFIGURAÇÃO VISUAL - TEMA TERMINAL CLÍNICO
st.set_page_config(page_title="Lumina Med", page_icon="⚕️", layout="centered")

st.markdown("""
<style>
    /* Design Cyber-Medical de Alta Precisão */
    .stApp { background-color: #050b14; }
    h1, h2, h3 { color: #00d2ff; font-weight: 300; letter-spacing: 1px; }
    div.stButton > button {
        background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%);
        color: #fff; border: none; border-radius: 8px; font-weight: 600;
        transition: transform 0.2s, box-shadow 0.2s;
        width: 100%; padding: 0.6rem;
    }
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0, 210, 255, 0.4);
    }
    .stTextInput textarea, .stTextInput input, .stNumberInput input {
        background-color: #0b1423 !important; color: #fff !important;
        border: 1px solid #1f3a5e !important; border-radius: 8px !important;
    }
    .status-box { padding: 15px; border-radius: 8px; background-color: #0b1423; border-left: 5px solid #00d2ff; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

chaves_api = {
    "openai": st.secrets.get("OPENAI_API_KEY", ""),
    "gemini": st.secrets.get("GEMINI_API_KEY", ""),
    "groq": st.secrets.get("GROQ_API_KEY", ""),
    "openrouter": st.secrets.get("OPENROUTER_API_KEY", "")
}

# CONTROLE DE ESTADO (ETAPAS)
if 'etapa' not in st.session_state: st.session_state.etapa = 1
if 'opcoes' not in st.session_state: st.session_state.opcoes = []
if 'dados' not in st.session_state: st.session_state.dados = {}

def resetar():
    st.session_state.etapa = 1
    st.session_state.opcoes = []
    st.session_state.dados = {}

st.title("⚕️ Lumina Med")
st.markdown("### Assistente de Decisão Clínica Avançada")
st.markdown("---")

# ================= ETAPA 1: COLETA DE SINTOMAS =================
if st.session_state.etapa == 1:
    st.markdown("<div class='status-box'><b>PASSO 1:</b> Triagem do Paciente</div>", unsafe_allow_html=True)
    
    sintomas = st.text_area("Descreva o quadro clínico do paciente (Ex: dor, inflamação, febre):")
    alergias = st.text_input("Alergias conhecidas (Opcional):", placeholder="Ex: Penicilina, Dipirona...")
    
    col1, col2 = st.columns(2)
    idade = col1.number_input("Idade (anos):", min_value=0, max_value=120, step=1, value=None)
    peso = col2.number_input("Peso (kg):", min_value=0.0, max_value=200.0, step=0.5, value=None)
    
    if st.button("🔍 Buscar Opções de Tratamento"):
        if not sintomas or idade is None or peso is None:
            st.warning("⚠️ Preencha Sintomas, Idade e Peso obrigatórios.")
        else:
            with st.spinner("Analisando quadro clínico e cruzando dados..."):
                opcoes_geradas = listar_opcoes_tratamento(sintomas, alergias, chaves_api)
                if opcoes_geradas:
                    st.session_state.dados = {'sintomas': sintomas, 'idade': idade, 'peso': peso, 'alergias': alergias}
                    st.session_state.opcoes = opcoes_geradas
                    st.session_state.etapa = 2
                    st.rerun()
                else:
                    st.error("Falha ao gerar opções. Verifique a conexão das IAs.")

# ================= ETAPA 2: ESCOLHA DO PROFISSIONAL =================
elif st.session_state.etapa == 2:
    st.markdown("<div class='status-box'><b>PASSO 2:</b> Seleção do Princípio Ativo</div>", unsafe_allow_html=True)
    st.write(f"Paciente: **{st.session_state.dados['idade']} anos, {st.session_state.dados['peso']}kg** | Sintomas: *{st.session_state.dados['sintomas']}*")
    
    escolha = st.radio("Selecione o tratamento indicado para prosseguir com a matemática:", st.session_state.opcoes)
    
    colA, colB = st.columns(2)
    with colA:
        if st.button("✅ Gerar Prontuário Seguro"):
            st.session_state.escolha_final = escolha
            st.session_state.etapa = 3
            st.rerun()
    with colB:
        if st.button("🔄 Voltar / Corrigir Sintomas"):
            resetar()
            st.rerun()

# ================= ETAPA 3: VEREDITO E AUDITORIA =================
elif st.session_state.etapa == 3:
    st.markdown("<div class='status-box'><b>PASSO 3:</b> Emissão de Prontuário Auditado</div>", unsafe_allow_html=True)
    
    with st.spinner("Calculando posologia exata e acionando Auditoria de Segurança..."):
        telemetria, prontuario = gerar_prontuario_final(
            st.session_state.escolha_final, 
            st.session_state.dados['sintomas'], 
            st.session_state.dados['idade'], 
            st.session_state.dados['peso'], 
            st.session_state.dados['alergias'],
            chaves_api
        )
        
        if telemetria:
            st.success("✅ Veredito Clínico finalizado, auditado e validado!")
            st.info(prontuario)
        else:
            st.error(prontuario)

    st.markdown("---")
    if st.button("🔄 Novo Atendimento"):
        resetar()
        st.rerun()
