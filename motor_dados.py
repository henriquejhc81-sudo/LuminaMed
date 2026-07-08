import pandas as pd
import streamlit as st
import os

@st.cache_data
def carregar_banco_medicamentos():
    """
    Data Warehouse do Lumina Med:
    Leitor Resiliente. Tenta múltiplos encodings para evitar o erro 'utf-8'.
    """
    caminho_arquivo = 'medicamentos.csv'
    
    if not os.path.exists(caminho_arquivo):
        return {"ERRO": {"FALHA_LEITURA": [f"Arquivo {caminho_arquivo} não encontrado."]}}

    # Tenta ler o arquivo forçando diferentes codificações para ignorar erros do Excel
    encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
    df = None
    
    for enc in encodings:
        try:
            df = pd.read_csv(caminho_arquivo, sep=None, engine='python', encoding=enc)
            break # Se leu com sucesso, interrompe o loop
        except Exception:
            continue
            
    if df is None or df.empty:
        return {"ERRO": {"FALHA_LEITURA": ["Falha fatal: Não foi possível decodificar o arquivo CSV."]}}

    try:
        # Padroniza os nomes das colunas para maiúsculas e remove espaços ocultos
        df.columns = df.columns.str.strip().str.upper()
        
        # Mapeia as colunas exatas da sua planilha
        col_classe = 'CLASSE TERAPÊUTICA' if 'CLASSE TERAPÊUTICA' in df.columns else df.columns[2]
        col_principio = 'SUBSTÂNCIA' if 'SUBSTÂNCIA' in df.columns else df.columns[0]
        col_apres = 'APRESENTAÇÃO' if 'APRESENTAÇÃO' in df.columns else df.columns[1]

        # Estrutura relacional do dicionário
        banco_completo = {}
        
        for _, row in df.iterrows():
            classe = str(row.get(col_classe, 'OUTROS')).strip().upper()
            principio = str(row.get(col_principio, 'DESCONHECIDO')).strip().upper()
            apresentacao = str(row.get(col_apres, 'PADRÃO')).strip()
            
            if classe == 'NAN' or principio == 'NAN':
                continue
                
            if classe not in banco_completo:
                banco_completo[classe] = {}
            
            if principio not in banco_completo[classe]:
                banco_completo[classe][principio] = []
                
            if apresentacao not in banco_completo[classe][principio]:
                banco_completo[classe][principio].append(apresentacao)
                
        return banco_completo
    except Exception as e:
        return {"ERRO": {"FALHA_LEITURA": [str(e)]}}

def buscar_apresentacoes(principio_alvo, banco):
    """Busca as miligramagens exatas de um remédio no banco de dados"""
    if "ERRO" in banco:
        return []
        
    principio_alvo = str(principio_alvo).strip().upper()
    for classe, principios in banco.items():
        for principio, apresentacoes in principios.items():
            if principio_alvo in principio:
                return apresentacoes
    return []
