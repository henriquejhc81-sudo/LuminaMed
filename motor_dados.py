import pandas as pd
import streamlit as st
import os

@st.cache_data
def carregar_banco_medicamentos():
    """
    Data Warehouse do Lumina Med:
    Motor de Força Bruta. Testa múltiplos separadores e codificações 
    para garantir a leitura de qualquer planilha exportada pelo Excel.
    """
    caminho_arquivo = 'medicamentos.csv'
    
    if not os.path.exists(caminho_arquivo):
        return {"ERRO": {"FALHA_LEITURA": [f"Arquivo {caminho_arquivo} não encontrado na raiz do GitHub."]}}

    # 1. Estratégia de Força Bruta para abrir a planilha
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    separadores = [';', ',', '\t']
    
    df = None
    for enc in encodings:
        for sep in separadores:
            try:
                # O comando encoding_errors='ignore' pula qualquer letra corrompida sem travar o app
                temp_df = pd.read_csv(caminho_arquivo, sep=sep, encoding=enc, on_bad_lines='skip', encoding_errors='ignore')
                
                # Se o Pandas encontrou pelo menos 2 colunas, significa que o separador está correto!
                if len(temp_df.columns) > 1:
                    df = temp_df
                    break
            except Exception:
                continue
        if df is not None:
            break
            
    if df is None or df.empty:
        return {"ERRO": {"FALHA_LEITURA": ["Falha absoluta ao decodificar a planilha. Verifique o arquivo CSV."]}}

    try:
        # 2. Mapeamento Inteligente de Colunas (Imune a acentuação e espaços)
        colunas = [str(c).strip().upper() for c in df.columns]
        df.columns = colunas
        
        # Encontra as colunas rastreando fragmentos de palavras
        col_principio = next((c for c in colunas if 'SUBST' in c or 'PRINC' in c), colunas[0])
        col_classe = next((c for c in colunas if 'CLASS' in c or 'TERAP' in c), colunas[1] if len(colunas) > 1 else None)
        col_apres = next((c for c in colunas if 'APRES' in c or 'DOSAG' in c), None)

        # 3. Montagem do Dicionário Rápido na Memória RAM
        banco_completo = {}
        
        for _, row in df.iterrows():
            principio = str(row.get(col_principio, 'DESCONHECIDO')).strip().upper()
            classe = str(row.get(col_classe, 'OUTROS')).strip().upper() if col_classe else 'OUTROS'
            apresentacao = str(row.get(col_apres, 'PADRÃO')).strip() if col_apres else 'PADRÃO'
            
            # Se a linha estiver vazia, pula
            if pd.isna(row.get(col_principio)) or principio == 'NAN' or principio == '':
                continue
                
            if classe not in banco_completo:
                banco_completo[classe] = {}
            
            if principio not in banco_completo[classe]:
                banco_completo[classe][principio] = []
                
            if apresentacao not in banco_completo[classe][principio]:
                banco_completo[classe][principio].append(apresentacao)
                
        return banco_completo
        
    except Exception as e:
        return {"ERRO": {"FALHA_LEITURA": [f"Erro ao processar as colunas: {str(e)}"]}}

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
