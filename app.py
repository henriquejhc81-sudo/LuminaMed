import streamlit as st
from robo_ia import listar_opcoes_tratamento, gerar_prontuario_final

st.set_page_config(page_title="Lumina Med", page_icon="⚕️", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #050b14; }
    h1, h2, h3 { color: #00d2ff; }
    div.stButton > button { background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); color: #fff; width: 100%; border-radius: 8px;}
    .status-box { padding: 15px; border-radius: 8px; background-color: #0b1423; border-left: 5px solid #00d2ff; margin-bottom: 20px;}
</style>
""", unsafe_allow_html=True)

chaves_api = {
    "openrouter": st.secrets.get("OPENROUTER_API_KEY", ""),
    "groq": st.secrets.get("GROQ_API_KEY", "")
}

if 'etapa' not in st.session_state: st.session_state.etapa = 1
if 'opcoes' not in st.session_state: st.session_state.opcoes = []
if 'dados' not in st.session_state: st.session_state.dados = {}

def resetar():
    st.session_state.etapa = 1
    st.session_state.opcoes = []

st.title("⚕️ Lumina Med")
st.markdown("### Terminal Clínico CDSS")
st.markdown("---")

if st.session_state.etapa == 1:
    st.markdown("<div class='status-box'><b>ETAPA 1:</b> Triagem do Paciente</div>", unsafe_allow_html=True)
    sintomas = st.text_area("Quadro clínico do paciente:")
    alergias = st.text_input("Alergias (Opcional):")
    col1, col2 = st.columns(2)
    idade = col1.number_input("Idade:", min_value=0, step=1, value=None)
    peso = col2.number_input("Peso (kg):", min_value=0.0, step=0.5, value=None)
    
    if st.button("🔍 Buscar Tratamentos"):
        if sintomas and idade is not None and peso is not None:
            with st.spinner("Analisando quadro e cruzando com CSV..."):
                opcoes = listar_opcoes_tratamento(sintomas, alergias, chaves_api)
                if opcoes:
                    st.session_state.dados = {'sintomas': sintomas, 'idade': idade, 'peso': peso, 'alergias': alergias}
                    st.session_state.opcoes = opcoes
                    st.session_state.etapa = 2
                    st.rerun()

elif st.session_state.etapa == 2:
    st.markdown("<div class='status-box'><b>ETAPA 2:</b> Escolha o Princípio Ativo</div>", unsafe_allow_html=True)
    escolha = st.radio("Selecione para calcular dosagem:", st.session_state.opcoes)
    
    colA, colB = st.columns(2)
    with colA:
        if st.button("✅ Gerar Prontuário Exato"):
            st.session_state.escolha_final = escolha
            st.session_state.etapa = 3
            st.rerun()
    with colB:
        if st.button("🔄 Voltar"): resetar(); st.rerun()

elif st.session_state.etapa == 3:
    st.markdown("<div class='status-box'><b>ETAPA 3:</b> Prontuário Finalizado</div>", unsafe_allow_html=True)
    with st.spinner("Aplicando regras matemáticas e gerando bula..."):
        prontuario = gerar_prontuario_final(
            st.session_state.escolha_final, st.session_state.dados['sintomas'], 
            st.session_state.dados['idade'], st.session_state.dados['peso'], 
            st.session_state.dados['alergias'], chaves_api
        )
        st.success("✅ Veredito Validado!")
        st.info(prontuario)
        
    if st.button("🔄 Nova Consulta"): resetar(); st.rerun()
