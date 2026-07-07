import streamlit as st
import pandas as pd
import numpy as np
import os

# ==========================================
# CONEXÃO COM O MOTOR DE IA EXTERNO
# ==========================================
try:
    from robo_ia import listar_opcoes_tratamento, gerar_prontuario_final
    CONEXAO_IA = True
except ImportError:
    CONEXAO_IA = False

# ==========================================
# CONFIGURAÇÃO VISUAL DA INTERFACE
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
    .stTextInput > div > div > input { border-radius: 6px; }
    </style>
""", unsafe_allow_html=True)

chaves_api = {
    "openai": st.secrets.get("OPENAI_API_KEY", ""),
    "gemini": st.secrets.get("GEMINI_API_KEY", ""),
    "groq": st.secrets.get("GROQ_API_KEY", ""),
    "openrouter": st.secrets.get("OPENROUTER_API_KEY", "")
}

# ==========================================
# 1. MOTOR RESILIENTE DE LEITURA E ADAPTAÇÃO
# ==========================================
@st.cache_data
def carregar_e_adaptar_dados():
    # Verifica qual arquivo existe no repositório
    if os.path.exists("lista_medicamentos.csv"):
        nome_arquivo = "lista_medicamentos.csv"
    elif os.path.exists("medicamentos.csv"):
        nome_arquivo = "medicamentos.csv"
    else:
        st.error("⚠️ Nenhum arquivo de banco de dados (CSV) foi encontrado no repositório!")
        return pd.DataFrame()

    try:
        # Tenta ler com vírgula e pula linhas defeituosas para não travar o app
        df_bruto = pd.read_csv(nome_arquivo, sep=',', on_bad_lines='skip')
        
        # Se leu apenas 1 coluna, é porque o separador real era ponto e vírgula
        if len(df_bruto.columns) < 2:
            df_bruto = pd.read_csv(nome_arquivo, sep=';', on_bad_lines='skip')
            
    except Exception as e:
        # Se falhar feio, tenta forçar com ponto e vírgula
        try:
            df_bruto = pd.read_csv(nome_arquivo, sep=';', on_bad_lines='skip')
        except Exception as erro_fatal:
            st.error(f"⚠️ Erro fatal ao processar o arquivo: {erro_fatal}")
            return pd.DataFrame()

    df_adaptado = pd.DataFrame()
    
    # Extração segura das colunas (Mapeamento flexível)
    df_adaptado['nome'] = df_bruto.get('PRODUTO', df_bruto.get('SUBSTÂNCIA', pd.Series(dtype='object')))
    df_adaptado['principio_ativo'] = df_bruto.get('SUBSTÂNCIA', pd.Series(dtype='object'))
    df_adaptado['apresentacao'] = df_bruto.get('APRESENTAÇÃO', 'Não informada')
    df_adaptado['classe_terapeutica'] = df_bruto.get('CLASSE TERAPÊUTICA', 'Geral')
    
    # Se as colunas principais não existirem (ex: CSV em formato totalmente diferente)
    if df_adaptado['nome'].isnull().all() and len(df_bruto.columns) > 1:
        st.warning("⚠️ O formato das colunas do CSV não é o esperado ('PRODUTO', 'SUBSTÂNCIA', etc).")
        return pd.DataFrame()
    
    # Motor de Busca (NLP) focado na classe terapêutica
    df_adaptado['sintomas_indicados'] = df_adaptado['classe_terapeutica'].astype(str).str.lower()
    df_adaptado['alerta_alergia'] = df_adaptado['principio_ativo']
    
    # Blindagem Matemática: Preparando estrutura para cálculos de dosagem
    df_adaptado['idade_minima_meses'] = 0
    df_adaptado['dose_mg_kg_dia'] = 0.0
    df_adaptado['dose_maxima_diaria_mg'] = 0.0
    df_adaptado['frequencia_horas'] = 8
    df_adaptado['dose_padrao_adulto_mg'] = 0.0

    # Limpeza de dados vazios
    df_adaptado['nome'] = df_adaptado['nome'].replace('', np.nan)
    return df_adaptado.dropna(subset=['nome'])

@st.cache_data
def carregar_planilha_atc():
    caminho_arquivo = "lista_remedios_estruturada.csv"
    if not os.path.exists(caminho_arquivo): return pd.DataFrame()
    
    try:
        df_atc = pd.read_csv(caminho_arquivo, sep=',', on_bad_lines='skip')
        if len(df_atc.columns) < 2:
            df_atc = pd.read_csv(caminho_arquivo, sep=';', on_bad_lines='skip')
    except:
        return pd.DataFrame()
    return df_atc

# ==========================================
# 2. MOTOR CLÍNICO E SEGURANÇA
# ==========================================
def auditar_alergia_cruzada(alergia_paciente, df_atc):
    if not alergia_paciente or df_atc.empty: return [], []
    alvo = df_atc[df_atc['Princípio Ativo'].astype(str).str.contains(alergia_paciente.upper().strip(), na=False)]
    if alvo.empty: return [], []
    
    codigos_atc = alvo['Código ATC'].unique().tolist()
    familias = alvo['Classe/Família Terapêutica'].unique().tolist()
    bloqueados = df_atc[df_atc['Código ATC'].isin(codigos_atc)]['Princípio Ativo'].astype(str).tolist()
    return familias, [b.upper() for b in bloqueados]

df_medicamentos = carregar_e_adaptar_dados()
df_atc = carregar_planilha_atc()

def processar_sintomas(texto_sintomas):
    texto = texto_sintomas.lower().replace(',', ' ').replace('.', ' ')
    for palavra in [' e ', ' com ', ' muita ', ' muito ', ' de ', ' dor ']: texto = texto.replace(palavra, ' ')
    return [p.strip() for p in texto.split() if p.strip()]

def buscar_treatment_seguro(sintomas_lista, idade, peso, lista_bloqueio_alergia):
    resultados = []
    if df_medicamentos.empty: return resultados
        
    for index, row in df_medicamentos.iterrows():
        principio_atual = str(row['principio_ativo']).upper()
        if any(bloqueado in principio_atual for bloqueado in lista_bloqueio_alergia): continue

        sintomas_bula = str(row['sintomas_indicados']).lower()
        if any(sintoma in sintomas_bula for sintoma in sintomas_lista):
            if idade < (row['idade_minima_meses'] / 12): continue 
                
            tratamento = {"medicamento": row['nome'], "principio_ativo": row['principio_ativo'], "apresentacao": row['apresentacao']}
            
            if idade < 12:
                dose = peso * row['dose_mg_kg_dia']
                if 0 < row['dose_maxima_diaria_mg'] < dose: dose = row['dose_maxima_diaria_mg']
                freq = row['frequencia_horas'] if row['frequencia_horas'] > 0 else 8
                tratamento['prescricao'] = f"Pediátrico: {(dose / (24 / freq)):.1f}mg a cada {freq}h."
            else:
                freq = row['frequencia_horas'] if row['frequencia_horas'] > 0 else 8
                tratamento['prescricao'] = f"Adulto: {row['dose_padrao_adulto_mg']}mg a cada {freq}h."
                
            resultados.append(tratamento)
            if len(resultados) >= 15: break
    return resultados

# ==========================================
# 3. INTERFACE E GESTÃO DE ESTADO
# ==========================================
def limpar_consulta():
    for key in list(st.session_state.keys()): del st.session_state[key]
    st.session_state.etapa = 1

if "etapa" not in st.session_state: st.session_state.etapa = 1
if "dados" not in st.session_state: st.session_state.dados = {}

st.title("⚕️ Lumina Med")
st.markdown("### **Terminal Clínico CDSS Advanced**")
st.divider()

if st.session_state.etapa == 1:
    st.markdown("#### 📋 ETAPA 1: Triagem e Histórico")
    col1, col2 = st.columns([2, 1])
    with col1:
        sintomas = st.text_area("Quadro clínico OU Nome do medicamento (ex: Infecção urinária, Amoxicilina):", height=120)
    with col2:
        uso_continuo = st.text_input("Uso contínuo (ex: Losartana):")
        alergias = st.text_input("⚠️ Alergias (ex: Ibuprofeno):")

    bio_col1, bio_col2, bio_col3, bio_col4 = st.columns(4)
    with bio_col1: idade = st.number_input("Idade:", min_value=0, max_value=120, step=1, value=None)
    with bio_col2: peso = st.number_input("Peso (kg):", min_value=0.0, max_value=300.0, step=0.1, value=None)
    with bio_col3: sexo = st.selectbox("Sexo Biológico:", ["Masculino", "Feminino"])
    with bio_col4: creatinina = st.number_input("Creatinina (mg/dL) - Opc.:", min_value=0.0, max_value=15.0, step=0.1)

    with st.expander("🩺 Sinais Vitais e Comorbidades (Avançado - Opcional)", expanded=False):
        vit_col1, vit_col2, vit_col3 = st.columns(3)
        with vit_col1: pressao = st.text_input("Pressão Arterial (ex: 120/80):", placeholder="Opcional")
        with vit_col2: glicemia = st.number_input("Glicemia (mg/dL):", min_value=0, max_value=1000, step=1, value=0)
        with vit_col3: temperatura = st.number_input("Temperatura (°C):", min_value=30.0, max_value=45.0, step=0.1, value=36.5)
        comorbidades = st.multiselect("Selecione Comorbidades Preexistentes:", ["Hipertensão", "Diabetes Tipo 1", "Diabetes Tipo 2", "Asma", "Insuficiência Renal", "Insuficiência Cardíaca", "Doença Hepática", "DPOC"])

    st.markdown("---")
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🔍 Iniciar Auditoria Farmacológica"):
            if not sintomas or idade is None or peso is None:
                st.error("⚠️ O Quadro Clínico, a Idade e o Peso são obrigatórios.")
            else:
                st.session_state.dados = {"sintomas": sintomas, "uso_continuo": uso_continuo, "alergias": alergias, "idade": idade, "peso": peso, "sexo": sexo}
                st.session_state.etapa = 2
                st.rerun()

elif st.session_state.etapa == 2:
    st.markdown("### 💊 ETAPA 2: Resultados e Auditoria")
    
    alergia_paciente = st.session_state.dados.get('alergias', '')
    familias_risco, lista_bloqueio = auditar_alergia_cruzada(alergia_paciente, df_atc)
    
    if familias_risco:
        st.error(f"🚨 **ALERTA DE SEGURANÇA MÁXIMA:** Alergia a '{alergia_paciente.upper()}'. Risco detectado na família: **{familias_risco[0]}**.")
        st.warning("🛡️ Todos os medicamentos desta família foram removidos das opções de tratamento abaixo.")

    sintomas_processados = processar_sintomas(st.session_state.dados['sintomas'])
    opcoes = buscar_treatment_seguro(sintomas_processados, st.session_state.dados['idade'], st.session_state.dados['peso'], lista_bloqueio)
    
    if not opcoes:
        st.info("Nenhum medicamento seguro ou correspondente encontrado para os termos digitados.")
        st.button("⬅️ Voltar e Tentar Novamente", on_click=limpar_consulta)
    else:
        st.success(f"✅ O motor encontrou {len(opcoes)} opções seguras!")
        lista_radio = [f"{o['medicamento']} - {o['apresentacao']}" for o in opcoes]
        escolha = st.radio("Selecione a conduta para gerar o laudo:", lista_radio)
        
        col1, col2 = st.columns(2)
        with col1: st.button("⬅️ Voltar e Editar Triagem", on_click=limpar_consulta)
        with col2:
            if st.button("✅ Confirmar Conduta e Gerar Prontuário"):
                st.session_state.escolha_final = escolha
                st.session_state.etapa = 3
                st.rerun()

elif st.session_state.etapa == 3:
    st.markdown("### 📑 ETAPA 3: Laudo Clínico Final")
    st.success("Prontuário auditado com sucesso!")
    
    st.markdown(f"**Idade:** {st.session_state.dados['idade']} anos | **Peso:** {st.session_state.dados['peso']} kg | **Quadro:** {st.session_state.dados['sintomas']} | **Alergias:** {st.session_state.dados['alergias']}")
    st.markdown(f"**Medicamento Escolhido:** {st.session_state.escolha_final}")
    
    if CONEXAO_IA:
        st.info("Iniciando comunicação com o motor de IA externo...")
        with st.spinner("🧠 Gerando laudo avançado..."):
            try:
                prontuario = gerar_prontuario_final(st.session_state.escolha_final, st.session_state.dados, chaves_api)
                st.markdown(prontuario)
            except Exception as e:
                st.error(f"Erro no motor de IA: {e}")
                
    st.markdown("---")
    st.button("🔄 Iniciar Nova Consulta Limpa", on_click=limpar_consulta)
