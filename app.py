import streamlit as st
from robo_ia import listar_opcoes_tratamento, gerar_prontuario_final

st.set_page_config(page_title="Lumina Med", page_icon="⚕️", layout="centered")

st.markdown("""
<style>
    .stApp { background-color: #050b14; }
    h1, h2, h3 { color: #00d2ff; }
    div.stButton > button { background: linear-gradient(90deg, #00d2ff 0%, #3a7bd5 100%); color: #fff; width: 100%; border-radius: 8px;}
    .status-box { padding: 15px; border-radius: 8px; background-color: #0b1423; border-left: 5px solid #00d2ff; margin-bottom: 20px;}
    .alert-box { padding: 10px; border-radius: 5px; background-color: #4a0000; border-left: 5px solid #ff0000; color: #fff; margin-bottom: 15px;}
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
    st.session_state.dados = {}

st.title("⚕️ Lumina Med")
st.markdown("### Terminal Clínico CDSS Advanced")
st.markdown("---")

if st.session_state.etapa == 1:
    st.markdown("<div class='status-box'><b>ETAPA 1:</b> Triagem e Biometria</div>", unsafe_allow_html=True)
    
    sintomas = st.text_area("Quadro clínico OU Nome do medicamento (ex: Infecção urinária, Amoxicilina):")
    
    col_med, col_alergia = st.columns(2)
    uso_continuo = col_med.text_input("Uso contínuo (ex: Losartana, Atenolol):")
    alergias = col_alergia.text_input("Alergias (ex: Penicilina):")
    
    col1, col2, col3, col4 = st.columns(4)
    idade = col1.number_input("Idade:", min_value=0, step=1, value=None)
    peso = col2.number_input("Peso (kg):", min_value=0.0, step=0.5, value=None)
    sexo = col3.selectbox("Sexo Biológico:", ["Masculino", "Feminino"])
    creatinina = col4.number_input("Creatinina (mg/dL - opcional):", min_value=0.0, step=0.1, value=None)
    
    clearance = None
    if st.button("🔍 Analisar e Buscar"):
        if sintomas and idade is not None and peso is not None:
            # Cálculo automático de Clearance de Creatinina (Cockcroft-Gault)
            if creatinina and creatinina > 0:
                clearance = ((140 - idade) * peso) / (72 * creatinina)
                if sexo == "Feminino": clearance *= 0.85
                st.session_state.clearance = round(clearance, 2)
            else:
                st.session_state.clearance = "Não informado"

            with st.spinner("Analisando interações e buscando no Estoque (CSV)..."):
                opcoes = listar_opcoes_tratamento(sintomas, alergias, uso_continuo, chaves_api)
                if opcoes:
                    st.session_state.dados = {
                        'sintomas': sintomas, 'idade': idade, 'peso': peso, 
                        'alergias': alergias, 'uso_continuo': uso_continuo,
                        'clearance': st.session_state.clearance
                    }
                    st.session_state.opcoes = opcoes
                    st.session_state.etapa = 2
                    st.rerun()

elif st.session_state.etapa == 2:
    st.markdown("<div class='status-box'><b>ETAPA 2:</b> Escolha a Apresentação</div>", unsafe_allow_html=True)
    
    if st.session_state.dados.get('clearance') != "Não informado":
        st.markdown(f"<div class='alert-box'>⚙️ <b>Clearance de Creatinina Estimado:</b> {st.session_state.dados['clearance']} mL/min (Atenção ao ajuste renal)</div>", unsafe_allow_html=True)
    
    escolha = st.radio("Selecione para calcular dosagem:", st.session_state.opcoes)
    
    colA, colB = st.columns(2)
    with colA:
        if st.button("✅ Gerar Prontuário Seguro"):
            st.session_state.escolha_final = escolha
            st.session_state.etapa = 3
            st.rerun()
    with colB:
        if st.button("🔄 Voltar"): resetar(); st.rerun()

elif st.session_state.etapa == 3:
    st.markdown("<div class='status-box'><b>ETAPA 3:</b> Auditoria Final e Veredito</div>", unsafe_allow_html=True)
    with st.spinner("Consenso Multi-IA: Auditando interações medicamentosas e limites de dose..."):
        prontuario = gerar_prontuario_final(
            st.session_state.escolha_final, 
            st.session_state.dados, 
            chaves_api
        )
        if prontuario:
            st.success("✅ Prontuário Validado com Sucesso pelo Algoritmo Juiz!")
            st.info(prontuario)
        else:
            st.error("Falha de comunicação com os motores de IA. Tente novamente.")
        
    if st.button("🔄 Nova Consulta"): resetar(); st.rerun()
