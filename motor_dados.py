import pandas as pd
import streamlit as st
import os

@st.cache_data(ttl=3600)
def carregar_banco_medicamentos():
    caminho_arquivo = 'planilha_teste_sem_repeticoes.xlsx'
    
    if not os.path.exists(caminho_arquivo):
        return {"ERRO": f"Arquivo '{caminho_arquivo}' não encontrado na raiz."}, None
        
    try:
        df = pd.read_excel(caminho_arquivo)
        banco = {}
        
        for _, row in df.iterrows():
            substancia = str(row.get('SUBSTÂNCIA', '')).strip().upper()
            if substancia == 'NAN' or not substancia: continue
                
            classe_full = str(row.get('CLASSE TERAPÊUTICA', '')).strip().upper()
            apresentacao = str(row.get('APRESENTAÇÃO', '')).strip()
            tarja = str(row.get('TARJA', '')).strip()
            
            if tarja == "- (*)" or "SEM TARJA" in tarja.upper():
                tarja = "🟢 MIP (Isento de Prescrição)"
            elif "VERMELHA SOB RESTRIÇÃO" in tarja.upper():
                tarja = "🔴 Tarja Vermelha (Sob Restrição)"
            elif "VERMELHA" in tarja.upper():
                tarja = "🔴 Tarja Vermelha"
            elif "PRETA" in tarja.upper():
                tarja = "⚫ Tarja Preta"
                
            if " - " in classe_full:
                atc, classe = classe_full.split(" - ", 1)
            else:
                atc, classe = "N/A", classe_full
                
            atc = atc.strip()
            classe = classe.strip()
            
            # --- INJEÇÃO DINÂMICA DE SINTOMAS ---
            sintomas = "geral"
            if 'EXPECTORANTE' in classe or 'R5C' in atc:
                sintomas = "tosse com secreção, catarro, peito cheio, expectorante"
            elif 'ANTITUSSÍGENO' in classe or 'R5D' in atc:
                sintomas = "tosse seca, tosse alérgica, tosse irritativa"
            elif 'ANALGÉSICO' in classe or 'N2B' in atc:
                sintomas = "dor, febre, dor de cabeça, dor no corpo, dipirona, paracetamol"
            elif 'ANTI-INFLAMATÓRIO' in classe or 'M1A' in atc:
                sintomas = "dor, inflamação, inchaço, dor muscular, dor articular, garganta inflamada"
            elif 'ANTI-HISTAMÍNICO' in classe or 'R6A' in atc:
                sintomas = "alergia, rinite, coriza, espirros, coceira, urticária"
            elif 'ANTIBIÓTICO' in classe or 'PENICILINA' in classe or 'J1' in atc:
                sintomas = "infecção bacteriana, pus, febre alta persistente, bactéria"
            elif 'ANTIESPASMÓDICO' in classe or 'A3' in atc:
                sintomas = "cólica, dor abdominal, dor na barriga, espasmos"
            elif 'ANTIÁCIDO' in classe or 'A2A' in atc or 'BOMBA DE PRÓTONS' in classe:
                sintomas = "azia, queimação, refluxo, dor de estômago, gastrite"
            elif 'BRONCODILATADOR' in classe or 'R3A' in atc:
                sintomas = "falta de ar, asma, bronquite, chiado no peito"
            elif 'CORTICOSTER' in classe or 'H2A' in atc or 'D7A' in atc:
                sintomas = "inflamação grave, alergia grave, asma, dermatite"
                
            if substancia not in banco:
                banco[substancia] = {
                    "ATC": atc,
                    "Classe": classe,
                    "Sintomas_Chave": sintomas,
                    "Tarja": tarja,
                    "Apresentacoes": []
                }
                
            if apresentacao not in banco[substancia]["Apresentacoes"]:
                banco[substancia]["Apresentacoes"].append(apresentacao)
                
        return banco, df
        
    except Exception as e:
        return {"ERRO": f"Falha ao ler o Excel: {str(e)}"}, None

def buscar_apresentacoes(principio_alvo, banco):
    if "ERRO" in banco: return []
    principio_alvo = str(principio_alvo).strip().upper()
    resultados = set()
    for substancia, dados in banco.items():
        if principio_alvo in substancia or substancia in principio_alvo:
            resultados.add(f"{substancia} | {dados['Tarja']}")
    return list(resultados)

def auditar_alergia_cruzada(principio_sugerido, alergia_paciente, banco):
    """Retorna: is_seguro, msg_alerta, prefixo_atc, classe, sintomas_chave"""
    if not alergia_paciente or "ERRO" in banco:
        return True, "", None, None, None
        
    alergias_lista = [a.strip().upper() for a in alergia_paciente.split(',')]
    principio_upper = str(principio_sugerido).strip().upper()
    
    dados_sugerido = None
    for sub, d in banco.items():
        if principio_upper in sub or sub in principio_upper:
            dados_sugerido = d
            break
            
    if not dados_sugerido:
        return True, "", None, None, None
        
    for alergia in alergias_lista:
        # 1. Bloqueio Direto
        if alergia in principio_upper:
            return False, f"🚨 BLOQUEIO DIRETO: '{principio_sugerido}' contém o agente alérgico '{alergia}'!", dados_sugerido['ATC'][:3], dados_sugerido['Classe'], dados_sugerido['Sintomas_Chave']
            
        # 2. Bloqueio por Família ATC
        atc_alergia = None
        for sub, dados in banco.items():
            if alergia in sub:
                atc_alergia = dados['ATC']
                break
                
        if atc_alergia and len(dados_sugerido['ATC']) >= 3 and len(atc_alergia) >= 3:
            if dados_sugerido['ATC'][:3] == atc_alergia[:3]:
                return False, f"🚨 BLOQUEIO ATC CRUZADO: '{principio_sugerido}' pertence à mesma família farmacológica ({dados_sugerido['Classe']}) da alergia informada '{alergia}'!", dados_sugerido['ATC'][:3], dados_sugerido['Classe'], dados_sugerido['Sintomas_Chave']
            
    return True, "", None, None, None

def listar_proibidos_por_familia(prefixo_atc, banco):
    """Retorna todos os medicamentos que compartilham o mesmo código ATC proibido."""
    if not prefixo_atc or "ERRO" in banco: return []
    proibidos = set()
    for sub, dados in banco.items():
        if dados['ATC'].startswith(prefixo_atc):
            proibidos.add(sub.title())
    return sorted(list(proibidos))

def buscar_alternativas_seguras(sintomas_chave, prefixo_atc_proibido, banco):
    """Busca medicamentos que tratam os mesmos sintomas, mas de famílias ATC DIFERENTES."""
    if not sintomas_chave or sintomas_chave == 'geral' or not prefixo_atc_proibido or "ERRO" in banco:
        return []
        
    alternativas = set()
    sintomas_lista = [s.strip() for s in sintomas_chave.split(',')]
    
    for sub, dados in banco.items():
        # Pula imediatamente se for da mesma família proibida
        if dados['ATC'].startswith(prefixo_atc_proibido):
            continue
            
        # Verifica se algum sintoma da classe bate com os sintomas do remédio bloqueado
        for s in sintomas_lista:
            if s in dados['Sintomas_Chave']:
                alternativas.add(f"{sub} | {dados['Tarja']}")
                break
                
    return sorted(list(alternativas))[:15] # Limita a 15 opções para não poluir
