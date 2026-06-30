import streamlit as st
import pandas as pd
import os

# Tenta importar as inteligências do seu arquivo robo_ia.py (Sua IA original preservada)
try:
    from robo_ia import listar_opcoes_tratamento, gerar_prontuario_final
    CONEXAO_IA = True
except ImportError:
    CONEXAO_IA = False

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
    /* Estilo do Botão Principal Azul Neon */
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
def carregar_planilha_atc():
    caminho_arquivo = "lista_remedios_estruturada.xlsx"
    if os.path.exists(caminho_arquivo):
        try:
            return pd.read_excel(caminho_arquivo, sheet_name="Medicamentos_Estruturados")
        except Exception as e:
            st.error(f"Erro na leitura da planilha Excel: {e}")
            return pd.DataFrame()
    else:
        st.warning("⚠️ Planilha Excel não encontrada no sistema. A trava de alergia operará em modo reduzido.")
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

# Carrega o banco de dados silenciamente na memória
df_atc = carregar_planilha_atc()

# ==========================================
# 3. VARIÁVEIS DE ESTADO (Para o sistema não se perder nas telas)
# ==========================================
if "etapa" not in st.session_state: 
    st.session_state.etapa = 1
if "dados" not in st.session_state: 
    st.session_state.dados = {}
if "escolha_final" not in st.session_state: 
    st.session_state.escolha_final = ""

# ==========================================
# CABEÇALHO DO SISTEMA
# ==========================================
st.title("⚕️ Lumina Med")
st.markdown("### **Terminal Clínico CDSS Advanced** | Auditoria e Triagem Inteligente")
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

    # Gaveta Oculta
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
    
    # Botão de Ação
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🔍 Analisar e Buscar"):
            if not sintomas:
                st.warning("⚠️ O campo de Quadro Clínico é obrigatório para iniciar a busca.")
            else:
                # Salva todos os dados na memória e passa para a Etapa 2
                st.session_state.dados = {
                    "sintomas": sintomas, "uso_continuo": uso_continuo, "alergias": alergias,
                    "idade": idade, "peso": peso, "sexo": sexo, "creatinina": creatinina,
                    "pressao": pressao, "glicemia": glicemia, "temperatura": temperatura,
                    "comorbidades": comorbidades
                }
                st.session_state.etapa = 2
                st.rerun()

# ==========================================
# ETAPA 2: ANÁLISE DE ALERGIA E ESCOLHA
# ==========================================
elif st.session_state.etapa == 2:
    st.markdown("### 💊 ETAPA 2: Auditoria e Escolha da Apresentação")
    
    alergia_paciente = st.session_state.dados.get('alergias', '')
    familias_risco, lista_bloqueio = auditar_alergia_cruzada(alergia_paciente, df_atc)
    
    if familias_risco:
        st.error(f"🚨 **ALERTA DE SEGURANÇA MÁXIMA:** O paciente declarou alergia a '{alergia_paciente.upper()}'. O Algoritmo Juiz detectou risco de reação cruzada na família: **{familias_risco[0]}**.")
        st.warning("🛡️ **Ação do Sistema:** Todos os medicamentos da mesma família foram suprimidos do painel por segurança (Padrão Ouro de Auditoria).")

    # Opções do seu sistema original
    opcoes_disponiveis = [
        "PARACETAMOL", "ASPIRINA", "NAPROXENO", "DICLOFENACO", "CETOPROFENO",
        "FLURBIPROFENO", "BENZILMETILINDOL", "FENILBUTAZONA", "PIROXICAM", "TENOXICAM", "LORNOCICAM", "AMOXICILINA", "AZITROMICINA"
    ]
    
    # O FILTRO: Exclui da lista os remédios que batem com o código ATC de alergia
    opcoes_seguras = [med for med in opcoes_disponiveis if med not in lista_bloqueio]
    
    if not opcoes_seguras:
        st.error("Nenhuma opção segura disponível com as restrições atuais.")
        if st.button("⬅️ Voltar"):
            st.session_state.etapa = 1
            st.rerun()
    else:
        escolha = st.radio("Selecione para gerar o Prontuário:", opcoes_seguras)
        
        col_voltar, col_avancar = st.columns(2)
        with col_voltar:
            if st.button("⬅️ Voltar e Editar Dados"):
                st.session_state.etapa = 1
                st.rerun()
        with col_avancar:
            if st.button("✅ Gerar Prontuário Seguro"):
                st.session_state.escolha_final = escolha
                st.session_state.etapa = 3
                st.rerun()

# ==========================================
# ETAPA 3: LAUDO FINAL (COM O ROBO DA IA)
# ==========================================
elif st.session_state.etapa == 3:
    st.markdown("### 📑 ETAPA 3: Auditoria Final e Veredito")
    st.success("Prontuário validado com Sucesso pelo Algoritmo Juiz!")
    
    if CONEXAO_IA:
        with st.spinner("🧠 Consenso Multi-IA: Auditando interações e gerando laudo com o robo_ia..."):
            try:
                # O CÓDIGO CORRIGIDO: Agora enviamos apenas os 2 argumentos que a IA exige!
                prontuario = gerar_prontuario_final(st.session_state.escolha_final, st.session_state.dados)
                st.markdown(prontuario)
            except Exception as e:
                st.error(f"⚠️ Erro ao conectar com o motor de IA: {e}")
                st.info("O sistema travou as alergias perfeitamente, mas houve uma falha de comunicação com as chaves da API.")
    else:
        st.warning("Motor de IA não detectado na pasta (arquivo robo_ia.py ausente). Mostrando dados de contingência:")
        st.json(st.session_state.dados)
        st.write(f"**Medicamento Selecionado:** {st.session_state.escolha_final}")
        
    st.markdown("---")
    if st.button("🔄 Nova Consulta"):
        st.session_state.etapa = 1
        st.rerun()
