import pandas as pd
import streamlit as st

@st.cache_data
def carregar_banco_medicamentos():
    """
    Data Warehouse do Lumina Med:
    Lê o CSV em milissegundos. Pandas aguenta milhões de linhas, o seu arquivo é super leve!
    """
    try:
        # Lê o arquivo forçando o motor a aceitar acentos e identificar as colunas corretamente
        df = pd.read_csv('lista_medicamentos (1).xls - Planilha1.csv', sep=',', on_bad_lines='skip')
        
        # Estrutura: { "Classe": { "Principio": ["Apresentacao1", "Apresentacao2"] } }
        banco_completo = {}
        
        for _, row in df.iterrows():
            # AGORA SIM! Pegando os nomes EXATOS das colunas da sua planilha
            classe = str(row.get('CLASSE TERAPÊUTICA', 'Outros')).strip().upper()
            principio = str(row.get('SUBSTÂNCIA', 'Desconhecido')).strip().upper()
            apresentacao = str(row.get('APRESENTAÇÃO', 'Padrão')).strip()
            
            # Se a linha estiver vazia, ignora e pula para a próxima
            if pd.isna(row.get('SUBSTÂNCIA')) or principio == 'NAN' or principio == 'DESCONHECIDO':
                continue
                
            if classe not in banco_completo:
                banco_completo[classe] = {}
            
            if principio not in banco_completo[classe]:
                banco_completo[classe][principio] = []
                
            if apresentacao not in banco_completo[classe][principio]:
                banco_completo[classe][principio].append(apresentacao)
                
        return banco_completo
    except Exception as e:
        print(f"Erro Crítico de Leitura: {e}")
        return {}

def buscar_apresentacoes(principio_alvo, banco):
    """Busca as miligramagens exatas de um remédio no banco de dados"""
    if not banco:
        return []
        
    principio_alvo = str(principio_alvo).upper().strip()
    # Pega apenas o primeiro nome (ex: se a IA sugerir "Ibuprofeno Sódico", busca por "IBUPROFENO")
    primeiro_nome = principio_alvo.split()[0] 
    
    apresentacoes_encontradas = []
    for classe, principios in banco.items():
        for principio, apresentacoes in principios.items():
            if primeiro_nome in principio:
                apresentacoes_encontradas.extend(apresentacoes)
                
    # Remove duplicatas e retorna até as 5 principais apresentações encontradas
    return list(dict.fromkeys(apresentacoes_encontradas))[:5]
