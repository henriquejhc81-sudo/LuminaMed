import pandas as pd
import streamlit as st
import os

@st.cache_data(ttl=3600)
def carregar_banco_medicamentos():
    caminho_arquivo = 'banco_medicamentos_limpo.xlsx'
    
    if not os.path.exists(caminho_arquivo):
        return {"ERRO": f"Arquivo '{caminho_arquivo}' não encontrado."}, None
        
    try:
        # Lê as duas abas do banco de dados relacional
        df_meds = pd.read_excel(caminho_arquivo, sheet_name='Medicamentos')
        df_atc = pd.read_excel(caminho_arquivo, sheet_name='Categorias_ATC')
        
        # Junta (Merge) as informações usando o ID_ATC (Chave Estrangeira)
        df_completo = pd.merge(df_meds, df_atc, on='ID_ATC', how='left')
        
        # Cria um dicionário estruturado para buscas super rápidas no cache
        banco = {}
        for _, row in df_completo.iterrows():
            substancia = str(row['Nome_Principio_Ativo']).strip().upper()
            classe = str(row['Nome_Classe']).strip().upper()
            atc = str(row['ID_ATC']).strip().upper()
            
            banco[substancia] = {
                "ATC": atc,
                "Classe": classe,
                "Risco": str(row.get('Risco_Alerta', 'Baixo'))
            }
            
        return banco, df_completo
        
    except Exception as e:
        return {"ERRO": f"Falha ao ler o Excel estruturado: {str(e)}"}, None

def buscar_apresentacoes(principio_alvo, banco):
    if "ERRO" in banco: 
        return []
        
    principio_alvo = str(principio_alvo).strip().upper()
    resultados = set()
    
    # Busca por correspondência exata ou parcial do princípio ativo
    for substancia, dados in banco.items():
        if principio_alvo in substancia or substancia in principio_alvo:
            resultados.add(substancia)
            
    return list(resultados)

def auditar_alergia_cruzada(principio_sugerido, alergia_paciente, banco):
    """
    Aplica a Regra de Negócio: Cruza o código ATC do medicamento sugerido 
    com o ATC da alergia declarada pelo paciente.
    """
    if not alergia_paciente or "ERRO" in banco:
        return True, "Nenhum histórico de alergia cruzada detectado."
        
    alergia_upper = alergia_paciente.strip().upper()
    principio_upper = principio_sugerido.strip().upper()
    
    # 1. Encontra o código ATC da droga que o paciente tem alergia
    atc_alergia = None
    for sub, dados in banco.items():
        if alergia_upper in sub:
            atc_alergia = dados['ATC']
            break
            
    if not atc_alergia:
        return True, "Alergia declarada não mapeada na base ATC do sistema."
        
    # 2. Compara com a droga sugerida pela IA
    dados_sugerido = banco.get(principio_upper)
    if dados_sugerido:
        # Se as 3 primeiras letras/números do ATC baterem, eles são da mesma família (Ex: 'J01' - Antibacterianos)
        if dados_sugerido['ATC'][:3] == atc_alergia[:3]:
            return False, f"🚨 ALERTA VERMELHO: O medicamento sugerido pertence à mesma classe ATC ({dados_sugerido['ATC'][:3]} - {dados_sugerido['Classe']}) da alergia informada!"
            
    return True, "Seguro: Nenhuma alergia de mesma classe detectada."
