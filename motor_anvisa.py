import pandas as pd
import streamlit as st
import os

@st.cache_data
def carregar_banco_medicamentos():
    """
    Data Warehouse do Lumina Med (Versão Blindada):
    Busca o novo arquivo medicamentos.csv e tenta diversos separadores e codificações.
    """
    # O nome do novo arquivo que você colocou no GitHub!
    arquivo = 'medicamentos.csv'
    
    # 1. Verifica se o arquivo físico está lá
    if not os.path.exists(arquivo):
        st.error(f"🚨 ARQUIVO NÃO ENCONTRADO: O sistema não achou '{arquivo}'. Verifique se você fez o upload no GitHub.")
        return {}

    banco_completo = {}
    df = None
    
    # 2. Motor de Leitura Robusto: Testa vírgula e ponto e vírgula, em várias codificações
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
            # Se leu o arquivo e ele tem mais de 1 coluna, a leitura foi um sucesso!
            if not temp_df.empty and len(temp_df.columns) > 1:
                df = temp_df
                break # Para a busca, achamos o formato certo
        except Exception:
            continue
            
    if df is None or df.empty:
        st.error("🚨 ERRO DE LEITURA: O arquivo está vazio, corrompido ou o formato está errado. Abra o seu Excel e salve o arquivo novamente indo em 'Salvar como' -> 'CSV UTF-8 (Delimitado por vírgulas)'.")
        return {}

    # 3. Monta o cérebro de dados
    try:
        # Limpa os nomes das colunas invisíveis
        df.columns = [str(c).strip().upper() for c in df.columns]
        
        # Mapeia as colunas dinamicamente (aceita variações do nome)
        col_substancia = 'SUBSTÂNCIA' if 'SUBSTÂNCIA' in df.columns else 'PRINCIPIO ATIVO' if 'PRINCIPIO ATIVO' in df.columns else df.columns[0]
        col_apresentacao = 'APRESENTAÇÃO' if 'APRESENTAÇÃO' in df.columns else 'APRESENTACAO' if 'APRESENTACAO' in df.columns else df.columns[2]
        col_classe = 'CLASSE TERAPÊUTICA' if 'CLASSE TERAPÊUTICA' in df.columns else 'CLASSE' if 'CLASSE' in df.columns else df.columns[3]

        for _, row in df.iterrows():
            classe = str(row.get(col_classe, 'OUTROS')).strip().upper()
            principio = str(row.get(col_substancia, '')).strip().upper()
            apresentacao = str(row.get(col_apresentacao, '')).strip()
            
            # Ignora linhas em branco
            if pd.isna(row.get(col_substancia)) or principio == 'NAN' or not principio:
                continue
                
            if classe not in banco_completo:
                banco_completo[classe] = {}
            
            if principio not in banco_completo[classe]:
                banco_completo[classe][principio] = []
                
            if apresentacao and apresentacao not in banco_completo[classe][principio]:
                banco_completo[classe][principio].append(apresentacao)
                
        return banco_completo
    except Exception as e:
        st.error(f"🚨 ERRO NAS COLUNAS: Não consegui achar as colunas SUBSTÂNCIA e APRESENTAÇÃO. Erro: {str(e)}")
        return {}

def buscar_apresentacoes(principio_alvo, banco):
    """Procura as dosagens exatas de um medicamento na sua base de dados"""
    if not banco:
        return []
        
    # Pega apenas o primeiro nome para cruzar (Ex: "DIPIRONA")
    termo_busca = str(principio_alvo).upper().strip().split()[0] 
    
    encontrados = []
    for classe, principios in banco.items():
        for substancia, apresentacoes in principios.items():
            if termo_busca in substancia:
                encontrados.extend(apresentacoes)
                
    # Remove duplicados e retorna as primeiras 5 opções reais do estoque
    return list(dict.fromkeys(encontrados))[:5]
