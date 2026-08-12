import pandas as pd
import streamlit as st
import os

@st.cache_data(ttl=3600)
def carregar_banco_medicamentos():
    caminho_arquivo = 'banco_medicamentos_limpo.xlsx'
    
    if not os.path.exists(caminho_arquivo):
        return {"ERRO": f"Arquivo '{caminho_arquivo}' não encontrado."}, None
        
    try:
        df_meds = pd.read_excel(caminho_arquivo, sheet_name='Medicamentos')
        df_atc = pd.read_excel(caminho_arquivo, sheet_name='Categorias_ATC')
        
        df_completo = pd.merge(df_meds, df_atc, on='ID_ATC', how='left')
        
        banco = {}
        for _, row in df_completo.iterrows():
            substancia = str(row['Nome_Principio_Ativo']).strip().upper()
            classe = str(row['Nome_Classe']).strip().upper()
            atc = str(row['ID_ATC']).strip().upper()
            
            # --- INJEÇÃO DINÂMICA DE SINTOMAS (Mapeamento Inteligente) ---
            sintomas = "geral"
            if 'EXPECTORANTE' in classe or 'R5C' in atc:
                sintomas = "tosse com secreção, catarro, peito cheio, expectorante, mucolítico"
            elif 'ANTITUSSÍGENO' in classe or 'R5D' in atc:
                sintomas = "tosse seca, tosse alérgica, tosse irritativa"
            elif 'ANALGÉSICO' in classe or 'N2B' in atc:
                sintomas = "dor, febre, dor de cabeça, dor no corpo, dipirona, paracetamol"
            elif 'ANTI-INFLAMATÓRIO' in classe or 'M1A' in atc:
                sintomas = "dor, inflamação, inchaço, dor muscular, dor articular, garganta inflamada"
            elif 'ANTI-HISTAMÍNICO' in classe or 'R6A' in atc:
                sintomas = "alergia, rinite, coriza, espirros, coceira, urticária"
            elif 'ANTIBIÓTICO' in classe or 'PENICILINA' in classe or 'J1' in atc:
                sintomas = "infecção bacteriana, pus, febre alta persistente, bactéria, infecção grave"
            elif 'ANTIESPASMÓDICO' in classe or 'A3' in atc:
                sintomas = "cólica, dor abdominal, dor na barriga, espasmos"
            elif 'ANTIÁCIDO' in classe or 'A2A' in atc or 'BOMBA DE PRÓTONS' in classe:
                sintomas = "azia, queimação, refluxo, dor de estômago, gastrite"
            elif 'BRONCODILATADOR' in classe or 'R3A' in atc:
                sintomas = "falta de ar, asma, bronquite, chiado no peito"
            elif 'CORTICOSTER' in classe or 'H2A' in atc or 'D7A' in atc:
                sintomas = "inflamação grave, alergia grave, asma, dermatite"
            
            banco[substancia] = {
                "ATC": atc,
                "Classe": classe,
                "Sintomas_Chave": sintomas,
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
    
    for substancia in banco.keys():
        if principio_alvo in substancia or substancia in principio_alvo:
            resultados.add(substancia)
            
    return list(resultados)

def auditar_alergia_cruzada(principio_sugerido, alergia_paciente, banco):
    if not alergia_paciente or "ERRO" in banco:
        return True, ""
        
    alergias_lista = [a.strip().upper() for a in alergia_paciente.split(',')]
    principio_upper = str(principio_sugerido).strip().upper()
    dados_sugerido = banco.get(principio_upper)
    
    if not dados_sugerido:
        return True, ""
        
    for alergia in alergias_lista:
        # 1. Checagem por Nome (Se contém a palavra exata)
        if alergia in principio_upper:
            return False, f"🚨 BLOQUEIO DIRETO: {principio_sugerido} contém o agente alérgico '{alergia}'!"
            
        # 2. Checagem Cruzada por Família ATC
        atc_alergia = None
        for sub, dados in banco.items():
            if alergia in sub:
                atc_alergia = dados['ATC']
                break
                
        # Compara as 3 primeiras letras (Subgrupo Farmacológico. Ex: J1C = Penicilinas)
        if atc_alergia and len(dados_sugerido['ATC']) >= 3 and len(atc_alergia) >= 3:
            if dados_sugerido['ATC'][:3] == atc_alergia[:3]:
                return False, f"🚨 BLOQUEIO CRUZADO: {principio_sugerido} pertence à mesma família ATC ({dados_sugerido['Classe']}) do item alérgico '{alergia}'!"
            
    return True, ""
