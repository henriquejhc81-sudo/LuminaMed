import streamlit as st
import pandas as pd
import os

# ==========================================
# 1. CONFIGURAÇÃO DA INTERFACE PREMIUM
# ==========================================
st.set_page_config(
    page_title="Lumina Med - CDSS Advanced",
    page_icon="⚕️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
    <style>
    div.stButton > button:first-child {
        background-color: #0056b3; color: white; border-radius: 8px;
        height: 3em; font-weight: 600; transition: all 0.3s ease;
        width: 100%; border: none;
    }
    div.stButton > button:first-child:hover {
        background-color: #003d82; border: 1px solid #00bfff;
        box-shadow: 0px 0px 15px rgba(0, 191, 255, 0.4);
    }
    .stTextInput > div > div > input, .stTextArea > div > textarea, .stNumberInput > div > div > input {
        border-radius: 6px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. ALGORITMO JUIZ: TRAVA DE ALERGIA ATC
# ==========================================
@st.cache_data
def carregar_banco_medicamentos():
    caminho_arquivo = "lista_remedios_estruturada.xlsx - Medicamentos_Estruturados.csv"
    if os.path.exists(caminho_arquivo):
        try:
            return pd.read_csv(caminho_arquivo)
        except Exception as e:
            st.error(f"Erro na leitura do arquivo de dados: {e}")
            return pd.DataFrame()
    else:
        st.warning("⚠️ Arquivo de medicamentos não encontrado. A trava operará em modo reduzido.")
        return pd.DataFrame()

def auditar_alergias(input_alergia, df_medicamentos):
    if not input_alergia or df_medicamentos.empty:
        return [], []
    alergia_limpa = input_alergia.upper().strip()
    
    alergias_encontradas = df_medicamentos[df_medicamentos['Princípio Ativo'].str.contains(alergia_limpa, na=False)]
    if alergias_encontradas.empty:
        return [], []
        
    codigos_atc_risco = alergias_encontradas['Código ATC'].unique().tolist()
    nomes_familias = alergias_encontradas['Classe/Família Terapêutica'].unique().tolist()
    
    medicamentos_bloqueados = df_medicamentos[df_medicamentos['Código ATC'].isin(codigos_atc_risco)]['Princípio Ativo'].unique().tolist()
    return nomes_familias, medicamentos_bloqueados

df_meds = carregar_banco_medicamentos()

# ==========================================
# 3. CABEÇALHO DO SISTEMA
# ==========================================
st.title("⚕️ Lumina Med")
st.markdown("### **Terminal Clínico CDSS Advanced** | Auditoria e Triagem Inteligente")
st.divider()

# ==========================================
# 4. ETAPA 1: TRIAGEM E BIOMETRIA
# ==========================================
st.markdown("#### 📋 ETAPA 1: Triagem e Histórico")

col1, col2 = st.columns([2, 1])
with col1:
    sintomas = st.text_area("Quadro clínico OU Nome do medicamento:", height=120)
with col2:
    uso_continuo = st.text_input("Uso contínuo (ex: Losartana):")
    alergias = st.text_input("⚠️ Alergias (ex: Ibuprofeno):")

st.markdown("#### 🧬 Perfil Biométrico")
bio_col1, bio_col2, bio_col3, bio_col4 = st.columns(4)
with bio_col1:
    idade = st.number_input("Idade:", min_value=0, max_value=120, step=1, value=30)
with bio_col2:
    peso = st.number_input("Peso (kg):", min_value=0.0, max_value=300.0, step=0.1, value=60.0)
with bio_col3:
    sexo = st.selectbox("Sexo Biológico:", ["Masculino", "Feminino"])
with bio_col4:
    creatinina = st.number_input("Creatinina (mg/dL) - Opcional:", min_value=0.0, max_value=15.0, step=0.1, value=0.0)

with st.expander("🩺 Sinais Vitais e Comorbidades (Avançado - Opcional)", expanded=False):
    vit_col1, vit_col2, vit_col3 = st.columns(3)
    with vit_col1:
        pressao = st.text_input("Pressão Arterial (ex: 120/80):")
    with vit_col2:
        glicemia = st.number_input("Glicemia (mg/dL):", min_value=0, max_value=1000, step=1, value=0)
    with vit_col3:
        temperatura = st.number_input("Temperatura (°C):", min_value=30.0, max_value=45.0, step=0.1, value=36.5)
    comorbidades = st.multiselect(
        "Selecione Comorbidades Preexistentes:",
        ["Hipertensão", "Diabetes Tipo 1", "Diabetes Tipo 2", "Asma", "Insuficiência Renal", "Insuficiência Cardíaca", "Doença Hepática", "DPOC"]
    )

st.markdown("---")

# ==========================================
# 5. ETAPA 2: ANÁLISE E TRAVA DE RISCO
# ==========================================
_, btn_col, _ = st.columns([1, 2, 1])
with btn_col:
    analisar = st.button("🔍 Analisar e Buscar")

if "analise_concluida" not in st.session_state:
    st.session_state.analise_concluida = False

if analisar:
    if not sintomas:
        st.warning("⚠️ O campo de Quadro Clínico é obrigatório.")
    else:
        st.session_state.analise_concluida = True

if st.session_state.analise_concluida:
    st.markdown("### 💊 ETAPA 2: Escolha a Apresentação")
    
    familias_risco, lista_bloqueio = auditar_alergias(alergias, df_meds)
    
    if familias_risco:
        st.error(f"🚨 **ALERTA DE SEGURANÇA MÁXIMA:** O paciente declarou alergia a '{alergias.upper()}'. O Algoritmo Juiz detectou risco de reação cruzada na família: **{familias_risco[0]}**.")
        st.warning("🛡️ **Ação do Sistema:** Todos os medicamentos da mesma família foram suprimidos do painel por segurança (Padrão Ouro de Auditoria).")

    opcoes_disponiveis = [
        "PARACETAMOL", "ASPIRINA", "NAPROXENO", "DICLOFENACO", "CETOPROFENO",
        "FLURBIPROFENO", "BENZILMETILINDOL", "FENILBUTAZONA", "PIROXICAM", "TENOXICAM", "LORNOCICAM"
    ]
    
    opcoes_seguras = [med for med in opcoes_disponiveis if med not in lista_bloqueio]
    
    if not opcoes_seguras:
        st.error("Nenhuma opção segura disponível com as restrições atuais.")
    else:
        medicamento_selecionado = st.radio("Selecione para calcular dosagem:", opcoes_seguras)
        
        _, btn_pront_col, _ = st.columns([1, 2, 1])
        with btn_pront_col:
            gerar_prontuario = st.button("✅ Gerar Prontuário Seguro")
            
        if gerar_prontuario:
            st.success("Prontuário validado com Sucesso pelo Algoritmo Juiz!")
            st.markdown(f"""
            ### Prontuário Rápido (Auditoria Final)
            * **Idade:** {idade} anos
            * **Peso:** {peso} kg
            * **Sintomas:** {sintomas}
            * **Alergias:** {alergias if alergias else 'Não informadas'}
            * **Uso contínuo:** {uso_continuo if uso_continuo else 'Não informado'}
            * **Medicamento Selecionado:** {medicamento_selecionado}
            """)
            st.info("💡 A IA gerará o Laudo detalhado (Posologia, Interação Renal e Bula).")
            st.markdown("""
            ---
            > ⚠️ **Aviso Legal:** *Este documento é um relatório de inteligência artificial. Não constitui diagnóstico.*
            """)
