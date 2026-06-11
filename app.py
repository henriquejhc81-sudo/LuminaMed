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
    nome_padrao = "LISTA MEDICAMENTOS.xlsx - Planilha1.csv"
    nome_arquivo = nome_padrao
    
    # Se o arquivo com o nome exato não for achado, o Nexus caça o arquivo correto
    if not os.path.exists(nome_arquivo):
        arquivos_no_github = os.listdir('.')
        # Procura qualquer arquivo .csv que mencione "MEDICAMENTOS" ou "LISTA"
        csv_encontrados = [f for f in arquivos_no_github if ('MEDICAMENTOS' in f.upper() or 'LISTA' in f.upper()) and f.endswith('.csv')]
        
        if csv_encontrados:
            nome_arquivo = csv_encontrados[0]
        else:
            # Se não achar nada com o nome, pega o primeiro .csv que estiver na pasta
            csv_gerais = [f for f in arquivos_no_github if f.endswith('.csv')]
            if csv_gerais:
                nome_arquivo = csv_gerais[0]
            else:
                st.error("⚠️ Nenhum arquivo CSV de medicamentos foi encontrado no seu repositório GitHub!")
                return pd.DataFrame()

    try:
        # Lê o arquivo detectado. Tenta identificar se o cabeçalho está na linha 1 ou 2
        df_bruto = pd.read_csv(nome_arquivo)
        if 'SUBSTÂNCIA' not in df_bruto.columns and len(df_bruto) > 0:
            # Tenta reler pulando a primeira linha caso haja lixo de exportação do Excel
            df_bruto = pd.read_csv(nome_arquivo, skiprows=1)
            
        st.info(f"📦 Banco de dados carregado com sucesso a partir de: `{nome_arquivo}`")
    except Exception as e:
        st.error(f"⚠️ Erro crítico ao ler a planilha: {e}")
        return pd.DataFrame()

    df_adaptado = pd.DataFrame()
    
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
