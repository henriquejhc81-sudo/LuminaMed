import streamlit as st
import pandas as pd
import os

# ---------------------------------------------------------
# 1. CONFIGURAÇÃO DA INTERFACE
# ---------------------------------------------------------
st.set_page_config(page_title="Lumina Med - Nexus", page_icon="⚕️", layout="centered")

st.title("⚕️ Lumina Med")
st.subheader("Sistema Inteligente de Suporte à Prescrição")
st.markdown("---")

# ---------------------------------------------------------
# 2. MOTOR DE DETECÇÃO E CARREGAMENTO RESILIENTE
# ---------------------------------------------------------
@st.cache_data
def carregar_e_adaptar_dados():
    # Agora buscamos pelo padrão limpo
    nome_arquivo = "lista_medicamentos.csv"
    
    # Se o arquivo não existir, o sistema avisa de forma elegante
    if not os.path.exists(nome_arquivo):
        st.error(f"⚠️ Arquivo '{nome_arquivo}' não encontrado. Verifique se o nome está em letras minúsculas!")
        return pd.DataFrame()

    try:
        # Lê o arquivo. Usamos header=0 pois agora ele está limpo
        df_bruto = pd.read_csv(nome_arquivo)
        st.info("📦 Banco de dados carregado com sucesso.")
    except Exception as e:
        st.error(f"⚠️ Erro ao processar o arquivo: {e}")
        return pd.DataFrame()

    # Mapeamento fixo, já que o arquivo está padronizado
    df_adaptado = pd.DataFrame()
    df_adaptado['nome'] = df_bruto['PRODUTO']
    df_adaptado['principio_ativo'] = df_bruto['SUBSTÂNCIA']
    df_adaptado['apresentacao'] = df_bruto['APRESENTAÇÃO']
    df_adaptado['classe_terapeutica'] = df_bruto['CLASSE TERAPÊUTICA']
    
    # Restante da lógica...
    df_adaptado['sintomas_indicados'] = df_adaptado['classe_terapeutica'].astype(str).str.lower()
    df_adaptado['alerta_alergia'] = df_adaptado['principio_ativo']
    # ... (restante do código)
    return df_adaptado
    
    # Padronização de Colunas (Garantindo nomes corretos independente do padrão)
    colunas_reais = df_bruto.columns
    substancia_col = [c for c in colunas_reais if 'SUBST' in c.upper()]
    apresentacao_col = [c for c in colunas_reais if 'APRES' in c.upper()]
    classe_col = [c for c in colunas_reais if 'CLASS' in c.upper()]
    produto_col = [c for c in colunas_reais if 'PROD' in c.upper()]

    if not substancia_col:
        st.error("⚠️ A coluna 'SUBSTÂNCIA' não foi detectada no arquivo enviado.")
        return pd.DataFrame()

    # Mapeamento dinâmico
    df_adaptado['nome'] = df_bruto[produto_col[0]] if produto_col else df_bruto[substancia_col[0]]
    df_adaptado['principio_ativo'] = df_bruto[substancia_col[0]]
    df_adaptado['apresentacao'] = df_bruto[apresentacao_col[0]] if apresentacao_col else "Não informada"
    df_adaptado['classe_terapeutica'] = df_bruto[classe_col[0]] if classe_col else "Geral"
    
    # Motor de Busca (NLP) focado na classe terapêutica
    df_adaptado['sintomas_indicados'] = df_adaptado['classe_terapeutica'].astype(str).str.lower()
    
    # Alertas e Travas Clínicas baseadas no princípio ativo
    df_adaptado['alerta_alergia'] = df_adaptado['principio_ativo']
    df_adaptado['tipo_receita'] = "Branca (Comum)"
    
    # Estrutura Matemática Preparada (V1 a V4)
    df_adaptado['idade_minima_meses'] = 0
    df_adaptado['dose_mg_kg_dia'] = 0.0
    df_adaptado['dose_maxima_diaria_mg'] = 0.0
    df_adaptado['frequencia_horas'] = 8
    df_adaptado['dose_padrao_adulto_mg'] = 0.0

    return df_adaptado.dropna(subset=['nome'])

# Executa o processamento em tempo de execução
df_medicamentos = carregar_e_adaptar_dados()

# ---------------------------------------------------------
# 3. MOTOR MATEMÁTICO (Inteligência Clínica)
# ---------------------------------------------------------
def processar_sintomas(texto_sintomas):
    texto = texto_sintomas.lower()
    palavras_ignoradas = [' e ', ' com ', ' muita ', ' muito ', ' de ', ' dor ', ',', '.']
    for palavra in palavras_ignoradas:
        texto = texto.replace(palavra, ' ')
    return [p.strip() for p in texto.split() if p.strip()]

def buscar_treatment(sintomas_lista, idade, peso):
    resultados = []
    if df_medicamentos.empty:
        return resultados
        
    for index, row in df_medicamentos.iterrows():
        sintomas_bula = str(row['sintomas_indicados']).lower()
        match = any(sintoma in sintomas_bula for sintoma in sintomas_lista)
        
        if match:
            if idade < row['idade_minima_meses'] / 12:
                continue 
                
            tratamento = {
                "medicamento": row['nome'],
                "principio_ativo": row['principio_ativo'],
                "alerta_alergia": row['alerta_alergia'],
                "tipo_receita": row['tipo_receita'],
                "apresentacao": row['apresentacao']
            }
            
            if idade < 12:
                dose_calculada = peso * row['dose_mg_kg_dia']
                if dose_calculada > row['dose_maxima_diaria_mg']:
                    dose_calculada = row['dose_maxima_diaria_mg']
                
                freq = row['frequencia_horas'] if row['frequencia_horas'] > 0 else 8
                dose_por_tomada = dose_calculada / (24 / freq)
                
                tratamento['prescricao'] = f"Uso Pediátrico: Administrar {dose_por_tomada:.1f}mg a cada {freq} horas."
            else:
                freq = row['frequencia_horas'] if row['frequencia_horas'] > 0 else 8
                tratamento['prescricao'] = f"Uso Adulto: Administrar {row['dose_padrao_adulto_mg']}mg a cada {freq} horas."
                
            resultados.append(tratamento)
            
            # Limite preventivo para o painel não travar com milhares de resultados
            if len(resultados) >= 20:
                break
                
    return resultados

# ---------------------------------------------------------
# 4. INTERFACE DO UTILIZADOR
# ---------------------------------------------------------
with st.form("form_paciente"):
    st.write("📋 **Dados do Paciente**")
    
    sintomas_input = st.text_input("Classe Terapêutica ou Termo da Bula (ex: expectorantes, analgésicos, corticosteróides):")
    
    col1, col2 = st.columns(2)
    with col1:
        idade_input = st.number_input("Idade (anos):", min_value=0, max_value=120, value=8)
    with col2:
        peso_input = st.number_input("Peso (kg):", min_value=1.0, max_value=200.0, value=25.0)
        
    submit_button = st.form_submit_button("Gerar Opções de Tratamento")

# ---------------------------------------------------------
# 5. APRESENTAÇÃO DOS RESULTADOS
# ---------------------------------------------------------
if submit_button:
    if not sintomas_input:
        st.warning("Por favor, introduza um termo de busca.")
    else:
        sintomas_processados = processar_sintomas(sintomas_input)
        opcoes = buscar_treatment(sintomas_processados, idade_input, peso_input)
        
        if opcoes:
            st.success(f"✅ Foram encontradas correspondências para os critérios informados!")
            for opcao in opcoes:
                with st.expander(f"💊 {opcao['medicamento']} - {opcao['apresentacao']}"):
                    st.write(f"**Princípio Ativo:** {opcao['principio_ativo']}")
                    st.write(f"**Instrução Base:** {opcao['prescricao']}")
                    st.write(f"**Classe de Receita:** {opcao['tipo_receita']}")
                    if pd.notna(opcao['alerta_alergia']):
                        st.error(f"⚠️ **Aviso de Segurança:** Validar histórico de alergia a: {opcao['alerta_alergia']}.")
        else:
            st.info("Nenhum medicamento correspondente encontrado para os termos digitados.")
