import pandas as pd
import streamlit as st
import os

def traduzir_nomes(texto):
    if not texto: return ""
    sinonimos = {
        "BENZETACIL": "BENZILPENICILINA",
        "BENZETACL": "BENZILPENICILINA",
        "NOVALGINA": "DIPIRONA",
        "NEOSALDINA": "DIPIRONA",
        "TYLENOL": "PARACETAMOL",
        "ROCEFIN": "CEFTRIAXONA",
        "AMOXIL": "AMOXICILINA",
        "BUSCOPAN": "ESCOPOLAMINA",
        "PLASIL": "METOCLOPRAMIDA",
        "VOLTAREN": "DICLOFENACO",
        "CATAFLAM": "DICLOFENACO",
        "ADVIL": "IBUPROFENO",
        "SPIDUFEM": "IBUPROFENO",
        "ALIVIUM": "IBUPROFENO",
        "MOTRIN": "IBUPROFENO",
        "ASPIRINA": "ACETILSALICÍLICO",
        "AAS": "ACETILSALICÍLICO",
        "RIVOTRIL": "CLONAZEPAM",
        "LEXOTAN": "BROMAZEPAM",
        "VALIUM": "DIAZEPAM",
        "ROACUTAN": "ISOTRETINOÍNA",
        "GLIFAGE": "METFORMINA",
        "PONSTAN": "ÁCIDO MEFENÂMICO",
        "TORSILAX": "CARISOPRODOL",
        "DORFLEX": "CARISOPRODOL",
        "ALLEGRA": "FEXOFENADINA",
        "POLARAMINE": "DEXCLORFENIRAMINA"
    }
    texto_upper = texto.upper()
    for marca, princ in sinonimos.items():
        if marca in texto_upper:
            texto_upper = texto_upper.replace(marca, princ)
    return texto_upper

@st.cache_data(ttl=3600)
def carregar_banco_medicamentos():
    caminho1 = 'banco_medicamentos_limpo.xlsx.xlsx'
    caminho2 = 'banco_medicamentos_limpo.xlsx'
    
    arquivo_alvo = caminho1 if os.path.exists(caminho1) else (caminho2 if os.path.exists(caminho2) else None)
    
    if not arquivo_alvo:
        return {"ERRO": "Arquivo Excel não encontrado na raiz. Verifique o nome."}, None
        
    try:
        df = pd.read_excel(arquivo_alvo)
        df = df.fillna("")
        
        banco = {}
        for _, row in df.iterrows():
            substancia = str(row.get('SUBSTÂNCIA', row.get('Nome_Principio_Ativo', row.get('Princípio Ativo', '')))).strip().upper()
            if not substancia or substancia == 'NAN': continue
                
            produto = str(row.get('PRODUTO', '')).strip().upper()
            laboratorio = str(row.get('LABORATÓRIO', '')).strip().upper()
            classe_full = str(row.get('CLASSE TERAPÊUTICA', row.get('Nome_Classe', row.get('Classe/Família Terapêutica', '')))).strip().upper()
            apresentacao = str(row.get('APRESENTAÇÃO', 'Apresentação genérica')).strip()
            tarja_bruta = str(row.get('TARJA', '')).strip()
            
            if tarja_bruta == "- (*)" or "SEM TARJA" in tarja_bruta.upper() or tarja_bruta == "":
                tarja = "🟢 MIP (Isento de Prescrição)"
            elif "VERMELHA SOB RESTRIÇÃO" in tarja_bruta.upper():
                tarja = "🔴 Tarja Vermelha (Sob Restrição)"
            elif "VERMELHA" in tarja_bruta.upper():
                tarja = "🔴 Tarja Vermelha"
            elif "PRETA" in tarja_bruta.upper():
                tarja = "⚫ Tarja Preta"
            else:
                tarja = "⚪ Tarja Sob Avaliação"
                
            atc = "N/A"
            classe = classe_full
            
            atc_direto = str(row.get('ID_ATC', row.get('Código ATC', ''))).strip().upper()
            if atc_direto and atc_direto != "NAN" and atc_direto != "":
                atc = atc_direto
            elif " - " in classe_full:
                partes = classe_full.split(" - ", 1)
                atc = partes[0].strip()
                classe = partes[1].strip()
                
            atc = atc.strip()
            classe = classe.strip()
            
            sintomas = "geral"
            if 'EXPECTORANTE' in classe or 'R5C' in atc: sintomas = "tosse com secreção, catarro, peito cheio, expectorante, mucolítico"
            elif 'ANTITUSSÍGENO' in classe or 'R5D' in atc: sintomas = "tosse seca, tosse alérgica, tosse irritativa"
            elif 'ANALGÉSICO' in classe or 'N2B' in atc or 'ANTIPIRÉTICO' in classe: sintomas = "dor, febre, dor de cabeça, dor no corpo, dipirona, paracetamol"
            elif 'ANTI-INFLAMATÓRIO' in classe or 'M1A' in atc or 'M2A' in atc: sintomas = "dor, inflamação, inchaço, dor muscular, dor articular, garganta inflamada"
            elif 'ANTI-HISTAMÍNICO' in classe or 'R6A' in atc or 'ANTIALÉRGICO' in classe: sintomas = "alergia, rinite, coriza, espirros, coceira, urticária"
            elif 'ANTIBIÓTICO' in classe or 'PENICILINA' in classe or 'J1' in atc: sintomas = "infecção bacteriana, pus, febre alta persistente, bactéria, infecção grave"
            elif 'ANTIESPASMÓDICO' in classe or 'A3' in atc: sintomas = "cólica, dor abdominal, dor na barriga, espasmos"
            elif 'ANTIÁCIDO' in classe or 'A2A' in atc or 'BOMBA DE PRÓTONS' in classe or 'A2B' in atc: sintomas = "azia, queimação, refluxo, dor de estômago, gastrite"
            elif 'BRONCODILATADOR' in classe or 'R3A' in atc or 'ASMA' in classe: sintomas = "falta de ar, asma, bronquite, chiado no peito"
            elif 'CORTICOSTER' in classe or 'H2A' in atc or 'D7A' in atc: sintomas = "inflamação grave, alergia grave, asma, dermatite"
            elif 'ANTIFÚNGICO' in classe or 'ANTIMICÓTICO' in classe or 'D1A' in atc or 'J2A' in atc: sintomas = "fungo, micose, coceira, frieira, cândida, pano branco"
            elif 'ANTIVIRAL' in classe or 'J5' in atc: sintomas = "vírus, herpes, gripe viral, infecção viral"
            elif 'DIURÉTICO' in classe or 'C3A' in atc: sintomas = "pressão alta, retenção de líquido, inchaço, edema"
            elif 'ANTI-HIPERTENSIVO' in classe or 'C2' in atc or 'C9' in atc or 'BETABLOQUEADOR' in classe: sintomas = "pressão alta, hipertensão, pressão arterial"
            elif 'ANTIDIABÉTICO' in classe or 'A10' in atc or 'INSULINA' in classe: sintomas = "diabetes, glicose alta, açúcar no sangue, hiperglicemia"
            elif 'RELAXANTE MUSCULAR' in classe or 'M3' in atc: sintomas = "tensão muscular, dor nas costas, torcicolo, espasmo muscular"
            elif 'ANTIDEPRESSIVO' in classe or 'N6A' in atc: sintomas = "depressão, ansiedade, pânico, tristeza, insônia"
            elif 'ANTIVERTIGINOSO' in classe or 'N7C' in atc: sintomas = "tontura, vertigem, labirintite, enjoo"
            elif 'ANTIEMÉTICO' in classe or 'A4A' in atc or 'A4' in atc: sintomas = "enjoo, náusea, vômito"
            
            if substancia not in banco:
                banco[substancia] = {
                    "ATC": atc,
                    "Classe": classe,
                    "Sintomas_Chave": sintomas,
                    "Marcas": set(),
                    "Opcoes_Fisicas": set(),
                    "Tarja": tarja
                }
            
            if produto and produto != "NAN":
                banco[substancia]["Marcas"].add(produto)
                
            nome_comercial = produto if produto and produto != "NAN" else "Genérico"
            lab_str = f" ({laboratorio})" if laboratorio and laboratorio != "NAN" else ""
            linha_fisica = f"{tarja} | {nome_comercial}{lab_str} - {apresentacao}"
            
            banco[substancia]["Opcoes_Fisicas"].add(linha_fisica)
            
        for sub in banco:
            banco[sub]["Marcas"] = sorted(list(banco[sub]["Marcas"]))
            banco[sub]["Opcoes_Fisicas"] = sorted(list(banco[sub]["Opcoes_Fisicas"]))
            
        return banco, df
        
    except Exception as e:
        return {"ERRO": f"Falha ao ler o Excel estruturado: {str(e)}"}, None

def buscar_apresentacoes(principio_alvo, banco):
    if "ERRO" in banco: return []
    principio_alvo = traduzir_nomes(str(principio_alvo)).strip()
    resultados = set()
    
    for substancia, dados in banco.items():
        if principio_alvo in substancia:
            resultados.add(f"{substancia} | {dados['Tarja']}")
        else:
            for marca in dados["Marcas"]:
                if principio_alvo in marca:
                    resultados.add(f"{substancia} | {dados['Tarja']}")
                    break
    return sorted(list(resultados))

def auditar_alergia_cruzada(principio_sugerido, alergia_paciente, banco):
    if not alergia_paciente or "ERRO" in banco:
        return True, "", None, None, None
        
    alergia_paciente = traduzir_nomes(alergia_paciente)
    alergias_lista = [a.strip().upper() for a in alergia_paciente.split(',')]
    principio_upper = traduzir_nomes(str(principio_sugerido)).strip()
    
    dados_sugerido = banco.get(principio_upper)
    if not dados_sugerido:
        for sub, d in banco.items():
            if principio_upper in sub or sub in principio_upper:
                dados_sugerido = d
                principio_upper = sub
                break
                
    if not dados_sugerido:
        return True, "", None, None, None
        
    for alergia in alergias_lista:
        if alergia in principio_upper:
            return False, f"🚨 BLOQUEIO DIRETO: '{principio_sugerido}' contém o agente '{alergia}'!", dados_sugerido['ATC'][:3], dados_sugerido['Classe'], dados_sugerido['Sintomas_Chave']
        
        for marca in dados_sugerido['Marcas']:
            if alergia in marca:
                return False, f"🚨 BLOQUEIO DIRETO: '{principio_sugerido}' é a base química da marca alérgica '{alergia}'!", dados_sugerido['ATC'][:3], dados_sugerido['Classe'], dados_sugerido['Sintomas_Chave']
            
        atc_alergia = None
        for sub, dados in banco.items():
            if alergia in sub:
                atc_alergia = dados['ATC']
                break
            for marca in dados['Marcas']:
                if alergia in marca:
                    atc_alergia = dados['ATC']
                    break
            if atc_alergia: break
                
        if atc_alergia and len(dados_sugerido['ATC']) >= 3 and len(atc_alergia) >= 3:
            if dados_sugerido['ATC'][:3] == atc_alergia[:3]:
                return False, f"🚨 BLOQUEIO ATC CRUZADO: '{principio_sugerido}' pertence à mesma família farmacológica ({dados_sugerido['Classe']}) da alergia informada ('{alergia}')!", dados_sugerido['ATC'][:3], dados_sugerido['Classe'], dados_sugerido['Sintomas_Chave']
            
    return True, "", None, None, None

def listar_proibidos_por_familia(prefixo_atc, banco):
    if not prefixo_atc or "ERRO" in banco: return []
    proibidos = set()
    for sub, dados in banco.items():
        if dados['ATC'].startswith(prefixo_atc):
            proibidos.add(sub.title())
    return sorted(list(proibidos))

def buscar_alternativas_seguras(sintomas_chave, prefixo_atc_proibido, banco):
    if not sintomas_chave or sintomas_chave == 'geral' or not prefixo_atc_proibido or "ERRO" in banco:
        return []
        
    alternativas = set()
    sintomas_lista = [s.strip() for s in sintomas_chave.split(',')]
    
    for sub, dados in banco.items():
        if dados['ATC'].startswith(prefixo_atc_proibido):
            continue
        for s in sintomas_lista:
            if s in dados['Sintomas_Chave']:
                alternativas.add(f"{sub} | {dados['Tarja']}")
                break
                
    return sorted(list(alternativas))[:15]
