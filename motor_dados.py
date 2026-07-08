import pandas as pd
import streamlit as st
import os

@st.cache_data
def carregar_banco_medicamentos():
    """
    Data Warehouse do Lumina Med:
    Leitor cravado no padrão Excel Brasil (Latin-1) com cabeçalhos exatos.
    """
    caminho_arquivo = 'medicamentos.csv'
    
    if not os.path.exists(caminho_arquivo):
        return {"ERRO": {"FALHA_LEITURA": [f"Arquivo {caminho_arquivo} não encontrado na raiz do GitHub."]}}

    try:
        # Força o padrão Windows (Latin-1) e ignora o UTF-8 que estava causando o erro 0xdd
        df = pd.read_csv(caminho_arquivo, sep=None, engine='python', encoding='latin-1')
        
        # Padroniza os nomes das colunas para maiúsculas e remove espaços ocultos
        df.columns = df.columns.str.strip().str.upper()
        
        banco_completo = {}
        
        for _, row in df.iterrows():
            # Mapeamento EXATO das colunas que você confirmou no cabeçalho
            principio = str(row.get('SUBSTÂNCIA', 'DESCONHECIDO')).strip().upper()
            classe = str(row.get('CLASSE TERAPÊUTICA', 'OUTROS')).strip().upper()
            
            # Se a coluna de apresentação tiver outro nome, ele usa 'PADRÃO'
            apresentacao = str(row.get('APRESENTAÇÃO', 'PADRÃO')).strip()
            
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
        return {"ERRO": {"FALHA_LEITURA": [f"Erro interno de leitura: {str(e)}"]}}

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
