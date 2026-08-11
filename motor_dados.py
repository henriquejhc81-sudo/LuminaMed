import pandas as pd
import streamlit as st
import os

@st.cache_data(ttl=3600) # Cache otimizado para a versão >=1.30.0
def carregar_banco_medicamentos():
    caminho_arquivo = 'medicamentos.csv'
    
    if not os.path.exists(caminho_arquivo):
        return {"ERRO": f"Arquivo '{caminho_arquivo}' não encontrado."}
        
    try:
        # Forçando a leitura correta do CSV brasileiro (separador ; e latin-1 ou utf-8)
        df = pd.read_csv(caminho_arquivo, sep=';', encoding='latin-1', on_bad_lines='skip')
        
        # Limpeza e Padronização Vectorizada (muito mais rápido no pandas 2.0+)
        df.columns = df.columns.str.strip().str.upper()
        
        # Captura as colunas com base em partes dos nomes
        col_subst = next((c for c in df.columns if 'SUBST' in c), None)
        col_classe = next((c for c in df.columns if 'CLASSE' in c or 'TERAP' in c), None)
        
        if not col_subst or not col_classe:
            return {"ERRO": "Colunas de Substância ou Classe Terapêutica ausentes."}
            
        # Agrupamento sofisticado de dados
        banco = {}
        df_valido = df.dropna(subset=[col_subst]).copy()
        
        for _, row in df_valido.iterrows():
            substancia = str(row[col_subst]).strip().upper()
            classe = str(row[col_classe]).strip().upper() if pd.notna(row[col_classe]) else 'OUTROS'
            
            if classe not in banco:
                banco[classe] = {}
            if substancia not in banco[classe]:
                banco[classe][substancia] = []
            
            # Adiciona apenas se não houver repetição de princípio exato na classe
            if substancia not in banco[classe][substancia]:
                banco[classe][substancia].append(substancia)
                
        return banco
        
    except Exception as e:
        return {"ERRO": f"Falha crítica na matriz de dados: {str(e)}"}

def buscar_apresentacoes(principio_alvo, banco):
    if "ERRO" in banco: 
        return []
    
    principio_alvo = str(principio_alvo).strip().upper()
    resultados = set() # Usando Set para evitar O(N^2) no processamento
    
    for _, principios in banco.items():
        for principio in principios.keys():
            # Match parcial seguro
            if principio_alvo in principio or principio in principio_alvo:
                resultados.add(principio)
                
    return list(resultados)
