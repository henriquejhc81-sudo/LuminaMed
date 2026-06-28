import pandas as pd
import streamlit as st
import os
import glob

@st.cache_data
def carregar_banco_medicamentos():
    """
    Data Warehouse (Auto-Detect):
    Procura automaticamente qualquer arquivo CSV na pasta e extrai os dados!
    """
    # Procura todos os arquivos que terminam com .csv
    arquivos_csv = glob.glob("*.csv")
    
    if not arquivos_csv:
        st.error("🚨 NENHUM ARQUIVO CSV ENCONTRADO. Faça o upload da sua planilha no GitHub.")
        return {}

    arquivo_alvo = arquivos_csv[0] # Pega o arquivo que ele achar (ex: medicamentos_2.csv)
    banco_completo = {}
    df = None
    
    configuracoes = [
        {'enc': 'utf-8', 'sep': ','},
        {'enc': 'utf-8', 'sep': ';'},
        {'enc': 'latin1', 'sep': ','},
        {'enc': 'latin1', 'sep': ';'},
        {'enc': 'iso-8859-1', 'sep': ';'}
    ]
    
    for config in configuracoes:
        try:
            temp_df = pd.read_csv(arquivo_alvo, sep=config['sep'], encoding=config['enc'], on_bad_lines='skip')
            if not temp_df.empty and len(temp_df.columns) > 1:
                df = temp_df
                break 
        except Exception:
            continue
            
    if df is None or df.empty:
        st.error(f"🚨 Não foi possível ler o arquivo {arquivo_alvo}. Salve como CSV UTF-8 no Excel.")
        return {}

    try:
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        col_substancia = 'SUBSTÂNCIA' if 'SUBSTÂNCIA' in df.columns else 'PRINCIPIO ATIVO' if 'PRINCIPIO ATIVO' in df.columns else df.columns[0]
        col_apresentacao = 'APRESENTAÇÃO' if 'APRESENTAÇÃO' in df.columns else 'APRESENTACAO' if 'APRESENTACAO' in df.columns else df.columns[2]
        col_classe = 'CLASSE TERAPÊUTICA' if 'CLASSE TERAPÊUTICA' in df.columns else 'CLASSE' if 'CLASSE' in df.columns else df.columns[3]

        for _, row in df.iterrows():
            classe = str(row.get(col_classe, 'OUTROS')).strip().upper()
            principio = str(row.get(col_substancia, '')).strip().upper()
            apresentacao = str(row.get(col_apresentacao, '')).strip()
            
            if pd.isna(row.get(col_substancia)) or principio == 'NAN' or not principio:
                continue
                
            if classe not in banco_completo: banco_completo[classe] = {}
            if principio not in banco_completo[classe]: banco_completo[classe][principio] = []
            if apresentacao and apresentacao not in banco_completo[classe][principio]:
                banco_completo[classe][principio].append(apresentacao)
                
        return banco_completo
    except Exception as e:
        return {}

def buscar_apresentacoes(principio_alvo, banco):
    if not banco: return []
    termo_busca = str(principio_alvo).upper().strip().split()[0] 
    encontrados = []
    for classe, principios in banco.items():
        for substancia, apresentacoes in principios.items():
            if termo_busca in substancia:
                encontrados.extend(apresentacoes)
    return list(dict.fromkeys(encontrados))[:5]
