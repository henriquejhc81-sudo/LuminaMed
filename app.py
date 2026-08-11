import os
import streamlit as st
from dotenv import load_dotenv
from motor_dados import carregar_banco_medicamentos, buscar_apresentacoes
from robo_ia import listar_opcoes_tratamento, gerar_prontuario_final

# Inicializa variáveis de ambiente locais (para desenvolvimento)
load_dotenv()

st.set_page_config(page_title="Lumina Med | CDSS", page_icon="⚕️", layout="centered")

# Injeção de CSS Cyberpunk Minimalista
st.markdown("""
<style>
    div.stButton > button {
        background-color: transparent;
        color: #00ff99;
        border: 1px solid #00ff99;
        border-radius: 4px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #00ff99;
        color: #0e1117;
        box-shadow: 0 0 15px #00ff99;
    }
</style>
""", unsafe_allow_html=True)

# Gerenciador Híbrido de Segredos (Lê do Streamlit Cloud ou do .env local)
def get_secret(key):
    return st.secrets.get(key, os.getenv(key, ""))

CHAVES_API = {
    'groq': get_secret("GROQ_API_KEY"),
    'openrouter': get_secret("OPENROUTER_API_KEY"),
    'openai': get_secret("OPENAI_API_KEY"),
    'gemini': get_secret("GEMINI_API_KEY")
}

st.title("⚕️ Lumina Med")
st.subheader("Terminal Clínico CDSS Advanced")

# Carregamento da Matriz de Dados
banco_csv = carregar_banco_medicamentos()
if "ERRO" in banco_csv:
    st.error(f"⚠️ {banco_csv['ERRO']}")
    st.stop()

# Controle de Estado da Sessão
if 'etapa' not in st.session_state: st.session_state.etapa = 1
if 'opcoes_estoque' not in st.session_state: st.session_state.opcoes_estoque = []
if 'dados_paciente' not in st.session_state: st.session_state.dados_paciente = {}
if 'escolha_final' not in st.session_state: st.session_state.escolha_final = ""

def resetar_consulta():
    st.session_state.etapa = 1
    st.session_state.opcoes_estoque = []
    st.session_state.dados_paciente = {}

# --- ETAPA 1 ---
if st.session_state.etapa == 1:
    st.markdown("### ETAPA 1: Triagem e Biometria")
    with st.form("form_triagem"):
        sintomas = st.text_area("Quadro Clínico (Sintomas detalhados):", placeholder="Ex: Febre alta, tosse seca...")
        
        col1, col2 = st.columns(2)
        uso_continuo = col1.text_input("Uso contínuo:", placeholder="Ex: Losartana")
        alergias = col2.text_input("Alergias:", placeholder="Ex: Penicilina")
        
        c1, c2, c3 = st.columns(3)
        idade = c1.number_input("Idade:", min_value=0, max_value=120, value=30)
        peso = c2.number_input("Peso (kg):", min_value=1.0, max_value=250.0, value=70.0)
        sexo = c3.selectbox("Sexo:", ["Masculino", "Feminino", "Outro"])
        
        if st.form_submit_button("Processar Triagem"):
            if not sintomas:
                st.warning("⚠️ Descreva o quadro clínico para prosseguir.")
            else:
                st.session_state.dados_paciente = {
                    "Sintomas": sintomas, "Alergias": alergias, "Uso": uso_continuo,
                    "Idade": idade, "Peso": peso, "Sexo": sexo
                }
                
                with st.status("🧠 Cruzando biometria com Inteligência Artificial...", expanded=True) as status:
                    st.write("Analisando sintomas e interações...")
                    sugestoes_ia = listar_opcoes_tratamento(sintomas, alergias, uso_continuo, CHAVES_API)
                    
                    st.write("Mapeando disponibilidade no estoque base...")
                    opcoes_encontradas = []
                    for principio in sugestoes_ia:
                        encontrados = buscar_apresentacoes(principio, banco_csv)
                        opcoes_encontradas.extend(encontrados)
                    
                    if opcoes_encontradas:
                        st.session_state.opcoes_estoque = list(set(opcoes_encontradas))
                        st.session_state.etapa = 2
                        status.update(label="Análise Concluída!", state="complete", expanded=False)
                        st.rerun()
                    else:
                        status.update(label="Falha no Cruzamento", state="error", expanded=False)
                        st.warning("A IA sugeriu princípios ativos que não estão mapeados no seu arquivo CSV de medicamentos.")

# --- ETAPA 2 ---
elif st.session_state.etapa == 2:
    st.markdown("### ETAPA 2: Validação Farmacêutica")
    st.info("Bases ativas encontradas compatíveis com o quadro:")
    
    escolha = st.radio("Selecione o Princípio Ativo para prescrição:", st.session_state.opcoes_estoque)
    
    col_a, col_b = st.columns(2)
    if col_a.button("Gerar Prontuário"):
        st.session_state.escolha_final = escolha
        st.session_state.etapa = 3
        st.rerun()
    if col_b.button("Voltar / Editar"):
        st.session_state.etapa = 1
        st.rerun()

# --- ETAPA 3 ---
elif st.session_state.etapa == 3:
    st.markdown("### ETAPA 3: Laudo CDSS Final")
    with st.spinner("Compilando dados matemáticos e interações..."):
        prontuario = gerar_prontuario_final(
            st.session_state.escolha_final, 
            st.session_state.dados_paciente, 
            CHAVES_API
        )
        st.success("✅ Protocolo Clínico Gerado.")
        st.markdown(prontuario)
        
    st.markdown("---")
    st.button("🔄 Iniciar Nova Triagem", on_click=resetar_consulta)
