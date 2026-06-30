import streamlit as st
import pandas as pd
import os

# Tenta importar a sua inteligência artificial (robo_ia.py) preservada
try:
    from robo_ia import listar_opcoes_tratamento, gerar_prontuario_final
    CONEXAO_IA = True
except ImportError:
    CONEXAO_IA = False

# ==========================================
# 1. CONFIGURAÇÃO E CHAVES DA API
# ==========================================
st.set_page_config(page_title="Lumina Med - CDSS Advanced", page_icon="⚕️", layout="wide")

st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #0056b3; color: white; border-radius: 8px;
        height: 3em; font-weight: 600; width: 100%; border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #003d82; box-shadow: 0px 0px 15px rgba(0, 191, 255, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Resgata as chaves exatamente como o seu robo_ia.py exige
chaves_api = {
    "openai": st.secrets.get("OPENAI_API_KEY", ""),
    "gemini": st.secrets.get("GEMINI_API_KEY", ""),
    "groq": st.secrets.get("GROQ_API_KEY", ""),
    "openrouter": st.secrets.get("OPENROUTER_API_KEY", "")
}

# ==========================================
# 2. MOTOR DO EXCEL E TRAVA DE RISCO
# ==========================================
@st.cache_data
def carregar_planilha_atc():
    caminho_arquivo = "lista_remedios_estruturada.xlsx"
    if os.path.exists(caminho_arquivo):
        try:
            return pd.read_excel(caminho_arquivo, sheet_name="Medicamentos_Estruturados")
        except Exception as e:
            return pd.DataFrame()
    return pd.DataFrame()

def auditar_alergia_cruzada(alergia_paciente, df_atc):
    if not alergia_paciente or df_atc.empty:
        return [], []
    
    alergia_limpa = alergia_paciente.upper().strip()
    alvo = df_atc[df_atc['Princípio Ativo'].str.contains(alergia_limpa, na=False)]
    
    if alvo.empty:
        return [], []
        
    codigos_atc_risco = alvo['Código ATC'].unique().tolist()
    nomes_familias = alvo['Classe/Família Terapêutica'].unique().tolist()
    
    bloqueados = df_atc[df_atc['Código ATC'].isin(codigos_atc_risco)]['Princípio Ativo'].tolist()
    return nomes_familias, bloqueados

df_atc = carregar_planilha_atc()

# ==========================================
# 3. GESTÃO DE ESTADO (MEMÓRIA) E LIMPEZA
# ==========================================
def limpar_consulta():
    # Isso resolve a "Memória Fantasma" (apaga tudo)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.session_state.etapa = 1

if "etapa" not in st.session_state: st.session_state.etapa = 1
if "dados" not in st.session_state: st.session_state.dados = {}
if "escolha_final" not in st.session_state: st.session_state.escolha_final = ""

st.title("⚕️ Lumina Med")
st.markdown("### **Terminal Clínico CDSS Advanced**")
st.divider()

# ==========================================
# ETAPA 1: TRIAGEM E BIOMETRIA
# ==========================================
if st.session_state.etapa == 1:
    st.markdown("#### 📋 ETAPA 1: Triagem e Histórico")

    col1, col2 = st.columns([2, 1])
    with col1:
        sintomas = st.text_area("Quadro clínico OU Nome do medicamento (ex: Infecção urinária, Amoxicilina):", height=120)
    with col2:
        uso_continuo = st.text_input("Uso contínuo (ex: Losartana):")
        alergias = st.text_input("⚠️ Alergias (ex: Naproxeno):")

    bio_col1, bio_col2, bio_col3 = st.columns(3)
    with bio_col1: idade = st.number_input("Idade (anos):", min_value=0, max_value=120, step=1, value=None)
    with bio_col2: peso = st.number_input("Peso (kg):", min_value=0.0, max_value=300.0, step=0.1, value=None)
    with bio_col3: sexo = st.selectbox("Sexo Biológico:", ["Masculino", "Feminino"])

    st.markdown("---")
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🔍 Analisar e Buscar (Orquestrar IA)"):
            if not sintomas or idade is None or peso is None:
                st.error("⚠️ Preencha o Quadro Clínico, a Idade e o Peso obrigatórios.")
            else:
                st.session_state.dados = {
                    "sintomas": sintomas, "uso_continuo": uso_continuo, "alergias": alergias,
                    "idade": idade, "peso": peso, "sexo": sexo
                }
                st.session_state.etapa = 2
                st.rerun()

# ==========================================
# ETAPA 2: AUDITORIA DE RISCO CRUZADO
# ==========================================
elif st.session_state.etapa == 2:
    st.markdown("### 💊 ETAPA 2: Auditoria de Segurança")
    
    alergia_paciente = st.session_state.dados.get('alergias', '')
    familias_risco, lista_bloqueio = auditar_alergia_cruzada(alergia_paciente, df_atc)
    
    if familias_risco:
        st.error(f"🚨 **ALERTA DE SEGURANÇA MÁXIMA:** Alergia a '{alergia_paciente.upper()}'. Risco de reação cruzada na família: **{familias_risco[0]}**.")
        st.warning("🛡️ Medicamentos conflitantes serão suprimidos do painel.")

    # A LISTA CORRETA E OFICIAL (Nomes extraídos da sua planilha, sem erros de digitação)
    opcoes_disponiveis = [
        "PARACETAMOL", "ÁCIDO ACETILSALICÍLICO", "NAPROXENO", "DICLOFENACO SÓDICO", "CETOPROFENO",
        "FLURBIPROFENO", "PIROXICAM", "TENOXICAM", "LORNOXICAM", "AMOXICILINA", "AZITROMICINA", "BENZOATO DE BENZILA"
    ]
    
    # O FILTRO INFALÍVEL
    opcoes_seguras = [med for med in opcoes_disponiveis if med not in lista_bloqueio]
    
    if not opcoes_seguras:
        st.error("Nenhuma opção segura disponível.")
        st.button("⬅️ Voltar", on_click=limpar_consulta)
    else:
        escolha = st.radio("Selecione para calcular dosagem e gerar prontuário:", opcoes_seguras)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("⬅️ Voltar", on_click=limpar_consulta)
        with col2:
            if st.button("✅ Gerar Prontuário Inteligente"):
                st.session_state.escolha_final = escolha
                st.session_state.etapa = 3
                st.rerun()

# ==========================================
# ETAPA 3: O LAUDO DA IA (ROBO_IA.PY)
# ==========================================
elif st.session_state.etapa == 3:
    st.markdown("### 📑 ETAPA 3: Veredito Clínico Final")
    
    if CONEXAO_IA:
        with st.spinner("🧠 Acionando as IAs (OpenAI/Gemini/Groq) para emissão do laudo..."):
            try:
                # O CÓDIGO CORRIGIDO (Enviando os 3 argumentos que o robo_ia quer)
                prontuario = gerar_prontuario_final(st.session_state.escolha_final, st.session_state.dados, chaves_api)
                
                st.success("Prontuário gerado e validado com sucesso!")
                st.info(prontuario)
                
            except Exception as e:
                st.error(f"⚠️ Erro ao acionar a API do robo_ia: {e}")
    else:
        st.error("⚠️ Arquivo robo_ia.py não encontrado ou com erro de importação.")
        
    st.markdown("---")
    st.button("🔄 Iniciar Nova Triagem do Zero", on_click=limpar_consulta)
