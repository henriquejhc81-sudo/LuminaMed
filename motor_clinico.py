import pandas as pd
import streamlit as st

@st.cache_data
def carregar_dados():
    try:
        return pd.read_csv("medicamentos.csv")
    except Exception:
        return pd.DataFrame()

def processar_sintomas(texto_sintomas):
    texto = texto_sintomas.lower()
    palavras_ignoradas = [' e ', ' com ', ' muita ', ' muito ', ' de ', ' dor ', ',', '.']
    for palavra in palavras_ignoradas:
        texto = texto.replace(palavra, ' ')
    return [p.strip() for p in texto.split() if p.strip()]

def buscar_tratamento(sintomas_lista, idade, peso, df_medicamentos):
    if df_medicamentos.empty: return []
    resultados = []
    for index, row in df_medicamentos.iterrows():
        sintomas_bula = str(row.get('sintomas_chave', '')).lower()
        match = any(sintoma in sintomas_bula for sintoma in sintomas_lista)
        
        if match:
            if idade < float(row.get('idade_minima', 0)):
                continue
                
            tratamento = {
                "principio_ativo": row.get('principio_ativo', 'N/A'),
                "classe": row.get('classe_farmacologica', 'N/A'),
                "alerta_alergia": row.get('avisos_alergia', ''),
                "similares": row.get('similares', '')
            }
            
            idade_adulta = float(row.get('idade_adulta', 12))
            freq_horas = int(row.get('frequencia_horas', 8))
            limite_max = float(row.get('limite_maximo_diario_mg', 1000))
            
            if idade < idade_adulta:
                dose_mg_kg = float(row.get('dosagem_mg_kg', 0))
                dose_diaria_total = dose_mg_kg * peso
                
                if dose_diaria_total > limite_max:
                    dose_diaria_total = limite_max
                
                doses_por_dia = 24 / freq_horas
                dose_por_tomada = dose_diaria_total / doses_por_dia
                tratamento['prescricao'] = f"Uso Pediátrico: Administrar {dose_por_tomada:.1f}mg a cada {freq_horas} horas."
            else:
                dose_adulta = float(row.get('dose_adulta_mg', 0))
                tratamento['prescricao'] = f"Uso Adulto: Administrar {dose_adulta}mg a cada {freq_horas} horas."
                
            resultados.append(tratamento)
    return resultados
