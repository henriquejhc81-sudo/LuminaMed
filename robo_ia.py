import requests

def consultar_llm(provedor, api_key, prompt):
    """Faz chamadas diretas via API simulando requisições estruturadas limpas"""
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    
    try:
        if provedor == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            return res.json()['choices'][0]['message']['content']
            
        elif provedor == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            return res.json()['choices'][0]['message']['content']
            
        elif provedor == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
            return res.json()['candidates'][0]['content']['parts'][0]['text']
            
        elif provedor == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
            payload = {
                "model": "openchat/openchat-7b",
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1
            }
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            return res.json()['choices'][0]['message']['content']
            
    except Exception as e:
        return f"Erro no provedor {provedor}: {str(e)}"
    return None

def analisar_consenso(sintomas_usuario, chaves_api):
    """O Agente Juiz que une as forças das IAs e extrai as palavras-chave clínicas"""
    
    prompt_analise = f"""
    Você é um extrator clínico de alta precisão. Analise os seguintes sintomas/frase do paciente: "{sintomas_usuario}"
    
    Responda EXATAMENTE no formato JSON abaixo, sem textos antes ou depois:
    {{
        "sintomas_chave": "palavras_chave_separadas_por_espaco",
        "analise_clinica_resumida": "Breve explicação humana do que os sintomas podem indicar"
    }}
    """
    
    respostas = []
    
    if chaves_api.get('openai'):
        respostas.append(consultar_llm("openai", chaves_api['openai'], prompt_analise))
    if chaves_api.get('gemini'):
        respostas.append(consultar_llm("gemini", chaves_api['gemini'], prompt_analise))
    if chaves_api.get('groq'):
        respostas.append(consultar_llm("groq", chaves_api['groq'], prompt_analise))
        
    return respostas
