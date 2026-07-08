import pandas as pd
import streamlit as st
import os

@st.cache_data
def carregar_banco_medicamentos():
    """
    Motor de Força Bruta: Imune a erros do Excel (latin-1, utf-8) e separadores.
    """
    caminho_arquivo = 'medicamentos.csv'
    
    if not os.path.exists(caminho_arquivo):
        return {"ERRO": {"FALHA_LEITURA": [f"Arquivo {caminho_arquivo} não encontrado na raiz."]}}

    df = None
    for enc in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
        for sep in [';', ',', '\t']:
            try:
                temp_df = pd.read_csv(caminho_arquivo, sep=sep, encoding=enc, on_bad_lines='skip', encoding_errors='ignore')
                if len(temp_df.columns) > 1:
                    df = temp_df
                    break
            except Exception:
                continue
        if df is not None: break
            
    if df is None or df.empty:
        return {"ERRO": {"FALHA_LEITURA": ["Falha absoluta ao decodificar a planilha CSV."]}}

    try:
        colunas = [str(c).strip().upper() for c in df.columns]
        df.columns = colunas
        
        # Mapeamento Flexível (Procura por palavras-chave em vez de nomes exatos)
        col_principio = next((c for c in colunas if 'SUBST' in c or 'PRINC' in c), colunas[0])
        col_classe = next((c for c in colunas if 'CLASS' in c or 'TERAP' in c), colunas[1] if len(colunas) > 1 else None)
        col_apres = next((c for c in colunas if 'APRES' in c or 'DOSAG' in c), None)

        banco_completo = {}
        for _, row in df.iterrows():
            principio = str(row.get(col_principio, 'DESCONHECIDO')).strip().upper()
            classe = str(row.get(col_classe, 'OUTROS')).strip().upper() if col_classe else 'OUTROS'
            apresentacao = str(row.get(col_apres, 'PADRÃO')).strip() if col_apres else 'PADRÃO'
            
            if pd.isna(row.get(col_principio)) or principio == 'NAN' or principio == '': continue
                
            if classe not in banco_completo: banco_completo[classe] = {}
            if principio not in banco_completo[classe]: banco_completo[classe][principio] = []
            if apresentacao not in banco_completo[classe][principio]: banco_completo[classe][principio].append(apresentacao)
                
        return banco_completo
    except Exception as e:
        return {"ERRO": {"FALHA_LEITURA": [f"Erro interno de colunas: {str(e)}"]}}

def buscar_apresentacoes(principio_alvo, banco):
    """Cruza as recomendações da IA com o seu estoque físico real"""
    if "ERRO" in banco: return []
    principio_alvo = str(principio_alvo).strip().upper()
    resultados = []
    
    for classe, principios in banco.items():
        for principio, apresentacoes in principios.items():
            if principio_alvo in principio or principio in principio_alvo:
                for ap in apresentacoes:
                    nome_completo = f"{principio} ({ap})"
                    if nome_completo not in resultados: resultados.append(nome_completo)
    return resultados
