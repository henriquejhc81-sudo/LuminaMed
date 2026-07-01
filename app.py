import streamlit as st
import pandas as pd
import os

# Tenta conectar com o seu arquivo robo_ia.py se ele existir
try:
    from robo_ia import listar_opcoes_tratamento, gerar_prontuario_final
    CONEXAO_IA = True
except ImportError:
    CONEXAO_IA = False

# ==========================================
# 1. CONFIGURAÇÃO DA INTERFACE PREMIUM E CHAVES
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

# Chaves para a IA
chaves_api = {
    "openai": st.secrets.get("OPENAI_API_KEY", ""),
    "gemini": st.secrets.get("GEMINI_API_KEY", ""),
    "groq": st.secrets.get("GROQ_API_KEY", ""),
    "openrouter": st.secrets.get("OPENROUTER_API_KEY", "")
}

# ==========================================
# 2. MOTORES DE DADOS (Cérebro Matemático + Trava de Alergia)
# ==========================================
@st.cache_data
def carregar_banco_principal():
    # Esse é o seu banco original com as doses
    nome_arquivo = "medicamentos.csv" 
    if not os.path.exists(nome_arquivo):
        return pd.DataFrame()

    try:
        df_bruto = pd.read_csv(nome_arquivo, on_bad_lines='skip', delimiter=';')
    except Exception:
        try:
            df_bruto = pd.read_csv(nome_arquivo, on_bad_lines='skip')
        except Exception:
            return pd.DataFrame()

    df_adaptado = pd.DataFrame()
    col_subst = next((c for c in df_bruto.columns if 'SUBST' in c.upper()), None)
    col_prod = next((c for c in df_bruto.columns if 'PROD' in c.upper()), None)
    col_apres = next((c for c in df_bruto.columns if 'APRES' in c.upper()), None)
    col_class = next((c for c in df_bruto.columns if 'CLASS' in c.upper()), None)

    if not col_subst:
        return pd.DataFrame()

    df_adaptado['nome'] = df_bruto[col_prod] if col_prod else df_bruto[col_subst]
    df_adaptado['principio_ativo'] = df_bruto[col_subst]
    df_adaptado['apresentacao'] = df_bruto[col_apres] if col_apres else "Não informada"
    df_adaptado['classe_terapeutica'] = df_bruto[col_class] if col_class else "Geral"
    df_adaptado['sintomas_indicados'] = df_adaptado['classe_terapeutica'].astype(str).str.lower()
    
    # Valores numéricos padrão de segurança
    df_adaptado['idade_minima_meses'] = 0
    df_adaptado['dose_mg_kg_dia'] = 0.0
    df_adaptado['dose_maxima_diaria_mg'] = 0.0
    df_adaptado['frequencia_horas'] = 8
    df_adaptado['dose_padrao_adulto_mg'] = 0.0

    return df_adaptado.dropna(subset=['nome'])

@st.cache_data
def carregar_planilha_atc():
    # A MÁGICA: Agora ele procura a sua planilha no formato CSV que nunca dá erro!
    caminho_arquivo = "lista_remedios_estruturada.csv" 
    if os.path.exists(caminho_arquivo):
        try:
            return pd.read_csv(caminho_arquivo)
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

def auditar_alergia_cruzada(alergia_paciente, df_atc):
    if not alergia_paciente or df_atc.empty:
        return [], []
    alergia_limpa = alergia_paciente.upper().strip()
    alvo = df_atc[df_atc['Princípio Ativo'].str.contains(alergia_limpa, na=False)]
    if alvo.empty:
        return [], []
    codigos_atc = alvo['Código ATC'].unique().tolist()
    familias = alvo['Classe/Família Terapêutica'].unique().tolist()
    bloqueados = df_atc[df_atc['Código ATC'].isin(codigos_atc)]['Princípio Ativo'].tolist()
    return familias, [b.upper() for b in bloqueados]

df_medicamentos = carregar_banco_principal()
df_atc = carregar_planilha_atc()

# ==========================================
# 3. MOTOR CLÍNICO E DE BUSCA
# ==========================================
def processar_sintomas(texto_sintomas):
    texto = texto_sintomas.lower()
    palavras_ignoradas = [' e ', ' com ', ' muita ', ' muito ', ' de ', ' dor ', ',', '.']
    for palavra in palavras_ignoradas:
        texto = texto.replace(palavra, ' ')
    return [p.strip() for p in texto.split() if p.strip()]

def buscar_treatment_seguro(sintomas_lista, idade, peso, lista_bloqueio_alergia):
    resultados = []
    if df_medicamentos.empty:
        return resultados
        
    for index, row in df_medicamentos.iterrows():
        # A TRAVA MATADORA: Bloqueia a família ATC inteira
        principio_atual = str(row['principio_ativo']).upper()
        if any(bloqueado in principio_atual for bloqueado in lista_bloqueio_alergia):
            continue

        sintomas_bula = str(row['sintomas_indicados']).lower()
        match = any(sintoma in sintomas_bula for sintoma in sintomas_lista)
        
        if match:
            if idade < (row['idade_minima_meses'] / 12):
                continue 
                
            tratamento = {
                "medicamento": row['nome'],
                "principio_ativo": row['principio_ativo'],
                "apresentacao": row['apresentacao']
            }
            
            if idade < 12:
                dose_calculada = peso * row['dose_mg_kg_dia']
                if dose_calculada > row['dose_maxima_diaria_mg'] > 0:
                    dose_calculada = row['dose_maxima_diaria_mg']
                freq = row['frequencia_horas'] if row['frequencia_horas'] > 0 else 8
                dose_por_tomada = dose_calculada / (24 / freq) if (24/freq) > 0 else 0
                tratamento['prescricao'] = f"Pediátrico: {dose_por_tomada:.1f}mg a cada {freq}h."
            else:
                freq = row['frequencia_horas'] if row['frequencia_horas'] > 0 else 8
                tratamento['prescricao'] = f"Adulto: {row['dose_padrao_adulto_mg']}mg a cada {freq}h."
                
            resultados.append(tratamento)
            if len(resultados) >= 15: 
                break
    return resultados

# ==========================================
# 4. GESTÃO DE TELAS E MEMÓRIA
# ==========================================
def limpar_consulta():
    # Essa função limpa o paciente anterior da memória!
    for key in list(st.session_state.keys()):
        del st.session_state[key]
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
        sintomas = st.text_area("Classe Terapêutica ou Sintoma (ex: Analgésicos, Tosse, Inflamação):", height=120)
    with col2:
        uso_continuo = st.text_input("Uso contínuo (ex: Losartana):")
        alergias = st.text_input("⚠️ Alergias (ex: Ibuprofeno):")

    bio_col1, bio_col2, bio_col3 = st.columns(3)
    # Deixei value=None para vir vazio e não carregar o paciente antigo!
    with bio_col1: idade = st.number_input("Idade (anos):", min_value=0, max_value=120, step=1, value=None)
    with bio_col2: peso = st.number_input("Peso (kg):", min_value=1.0, max_value=300.0, step=0.1, value=None)
    with bio_col3: sexo = st.selectbox("Sexo Biológico:", ["Masculino", "Feminino"])

    st.markdown("---")
    _, btn_col, _ = st.columns([1, 2, 1])
    with btn_col:
        if st.button("🔍 Iniciar Varredura de Tratamentos"):
            if not sintomas or idade is None or peso is None:
                st.error("⚠️ Preencha o Quadro Clínico, Idade e Peso obrigatoriamente.")
            else:
                st.session_state.dados = {
                    "sintomas": sintomas, "uso_continuo": uso_continuo, "alergias": alergias,
                    "idade": idade, "peso": peso, "sexo": sexo
                }
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
    opcoes = buscar_treatment_seguro(
        sintomas_processados, 
        st.session_state.dados['idade'], 
        st.session_state.dados['peso'], 
        lista_bloqueio
    )
    
    if not opcoes:
        st.info("Nenhum medicamento seguro ou correspondente encontrado para os termos digitados.")
        st.button("⬅️ Voltar e Tentar Novamente", on_click=limpar_consulta)
    else:
        st.success(f"✅ O motor encontrou {len(opcoes)} opções seguras!")
        lista_radio = [f"{o['medicamento']} - {o['apresentacao']}" for o in opcoes]
        escolha = st.radio("Selecione a conduta para gerar o laudo:", lista_radio)
        
        col1, col2 = st.columns(2)
        with col1:
            st.button("⬅️ Voltar e Editar Triagem", on_click=limpar_consulta)
        with col2:
            if st.button("✅ Confirmar Conduta e Gerar Prontuário"):
                st.session_state.escolha_final = escolha
                st.session_state.etapa = 3
                st.rerun()

elif st.session_state.etapa == 3:
    st.markdown("### 📑 ETAPA 3: Laudo Clínico Final")
    st.success("Prontuário auditado!")
    
    st.markdown(f"""
    **Paciente:** {st.session_state.dados['idade']} anos, {st.session_state.dados['peso']} kg  
    **Quadro:** {st.session_state.dados['sintomas']}  
    **Alergias:** {st.session_state.dados['alergias'] if st.session_state.dados['alergias'] else 'Não informadas'}  
    **Medicamento Escolhido:** {st.session_state.escolha_final}
    """)
    
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
