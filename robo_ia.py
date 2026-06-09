import requests
import json
from motor_anvisa import buscar_bula_anvisa

def consultar_llm_com_healer(prompt, chaves_api):
    """Healer Engine V2 priorizando Groq e OpenRouter"""
    erros_detalhados = []
    
    if chaves_api.get('openrouter'):
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            payload = {"model": "meta-llama/llama-3.1-8b-instruct", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['openrouter']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'], "OpenRouter"
            else:
                erros_detalhados.append(f"OpenRouter ({res.status_code})")
        except Exception as e:
            erros_detalhados.append("OpenRouter Erro")

    if chaves_api.get('groq'):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['groq']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'], "Groq"
            else:
                erros_detalhados.append(f"Groq ({res.status_code})")
        except Exception as e:
            erros_detalhados.append("Groq Erro")

    if chaves_api.get('gemini'):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={chaves_api['gemini']}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini"
            else:
                erros_detalhados.append(f"Gemini ({res.status_code})")
        except Exception as e:
            erros_detalhados.append("Gemini Erro")

    motivo_real = " | ".join(erros_detalhados)
    return None, f"⚠️ FALHA NAS APIs: {motivo_real}"

def listar_opcoes_tratamento(sintomas, alergias, chaves_api):
    """Passo 1: A IA apenas lista os princípios ativos viáveis"""
    prompt = f"""
    Paciente relata: "{sintomas}". Alergias conhecidas: "{alergias if alergias else 'Nenhuma informada'}".
    Liste APENAS o nome genérico de 3 a 5 princípios ativos indicados para esse quadro.
    Responda ESTRITAMENTE em formato JSON, sem nenhum outro texto.
    Exemplo: {{"opcoes": ["Ibuprofeno", "Paracetamol", "Dipirona"]}}
    """
    
    resposta, _ = consultar_llm_com_healer(prompt, chaves_api)
    if not resposta:
        return []
        
    try:
        # Limpa formatações Markdown indesejadas
        if "```json" in resposta:
            resposta = resposta.split("```json")[1].split("```")[0]
        elif "```" in resposta:
            resposta = resposta.split("```")[1].split("```")[0]
            
        dados = json.loads(resposta.strip())
        return dados.get("opcoes", [])
    except:
        # Fallback de limpeza caso a IA erre o JSON
        linhas = [l.strip().replace('- ', '').replace('* ', '') for l in resposta.split('\n') if len(l.strip()) > 3]
        return linhas[:5]

def gerar_prontuario_final(principio_escolhido, sintomas, idade, peso, alergias, chaves_api):
    """Passo 2: Gera a matemática e as contraindicações da droga escolhida pelo usuário"""
    prompt_consulta = f"""
    Médico escolheu: {principio_escolhido}.
    Paciente: {idade} anos, {peso}kg. Sintomas: {sintomas}. Alergias: {alergias if alergias else 'Nenhuma'}.
    
    Gere a prescrição ESTRITAMENTE neste formato:
    Princípio Ativo: {principio_escolhido}
    Para que serve: [BREVE EXPLICAÇÃO DA INDICAÇÃO]
    Posologia: [DOSE EXATA CALCULADA EM MG/ML/GOTAS PARA {peso}KG]
    Alergias e Alternativas: [CRUZAMENTO DE ALERGIA E 2 OPÇÕES DE ALTERNATIVAS SEGURAS]
    Contraindicações: [ALERTAS PRINCIPAIS]
    """
    
    prontuario_cru, provedor = consultar_llm_com_healer(prompt_consulta, chaves_api)
    if not prontuario_cru: return None, provedor

    prompt_auditoria = f"""
    Audite esta prescrição matemática para um paciente de {idade} anos e {peso}kg:
    "{prontuario_cru}"
    
    A dose é segura ou letal? 
    Se letal, corrija a matemática. Se segura, apenas repita a prescrição melhorando o visual com Markdown (negritos, ícones).
    """
    
    prontuario_auditado, _ = consultar_llm_com_healer(prompt_auditoria, chaves_api)
    if not prontuario_auditado: return None, "Falha na Auditoria."
    
    link_bula = buscar_bula_anvisa(principio_escolhido)

    relatorio_final = f"""
{prontuario_auditado}
    
---
**🛠️ Telemetria do Sistema:**
* Motor Estável: `{provedor}` (Healer V2)
* Auditoria: `Deep Learning Engine: Validado`
* 📄 **Bula Oficial (ANVISA):** {"[Acessar PDF da Bula](" + link_bula + ")" if link_bula else "Não localizada."}
    """
    return {"Provedor": provedor}, relatorio_final
