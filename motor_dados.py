import pandas as pd
import streamlit as st
import os

@st.cache_data
def carregar_banco_medicamentos():
    arquivo = 'medicamentos.csv'
    
    if not os.path.exists(arquivo):
        st.error(f"🚨 ARQUIVO NÃO ENCONTRADO: '{arquivo}'. Certifique-se de fazer o upload do CSV.")
        return {}

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
            temp_df = pd.read_csv(arquivo, sep=config['sep'], encoding=config['enc'], on_bad_lines='skip')
            if not temp_df.empty and len(temp_df.columns) > 1:
                df = temp_df
                break 
        except Exception:
            continue
            
    if df is None or df.empty:
        st.error("🚨 ERRO DE LEITURA: O arquivo está vazio ou o formato está errado.")
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
        st.error(f"🚨 ERRO NAS COLUNAS: Não consegui achar as colunas corretas. Erro: {str(e)}")
        return {}

def buscar_apresentacoes(principio_alvo, banco):
    if not banco:
        return []
    termo_busca = str(principio_alvo).upper().strip().split()[0] 
    encontrados = []
    for classe, principios in banco.items():
        for substancia, apresentacoes in principios.items():
            if termo_busca in substancia:
                encontrados.extend(apresentacoes)
    return list(dict.fromkeys(encontrados))[:5]
