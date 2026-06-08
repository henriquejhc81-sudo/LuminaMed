import requests
import json

def consultar_llm(provedor, api_key, prompt):
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    try:
        if provedor == "openai":
            url = "https://api.openai.com/v1/chat/completions"
            payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            return res.json()['choices'][0]['message']['content']
            
        elif provedor == "gemini":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=10)
            return res.json()['candidates'][0]['content']['parts'][0]['text']
            
        elif provedor == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            res = requests.post(url, json=payload, headers=headers, timeout=10)
            return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return ""
    return ""

def diagnosticar_principio_ativo(sintomas_usuario, chaves_api):
    """Usa a IA apenas para descobrir qual o princípio ativo indicado para o sintoma"""
    prompt = f"""
    O paciente relata o seguinte quadro: "{sintomas_usuario}".
    Responda APENAS com um objeto JSON contendo os nomes genéricos dos princípios ativos mais indicados para aliviar esses sintomas.
    Exemplo de formato: {{"principios_ativos": ["ondansetrona", "paracetamol", "ibuprofeno"]}}
    Não escreva nenhuma outra palavra além do JSON.
    """
    
    # Tenta usar a OpenAI primeiro, se não tiver, tenta Gemini, depois Groq
    resposta_ia = ""
    if chaves_api.get('openai'):
        resposta_ia = consultar_llm("openai", chaves_api['openai'], prompt)
    elif chaves_api.get('gemini'):
        resposta_ia = consultar_llm("gemini", chaves_api['gemini'], prompt)
    elif chaves_api.get('groq'):
        resposta_ia = consultar_llm("groq", chaves_api['groq'], prompt)
        
    if not resposta_ia:
        return []
        
    # Limpa a resposta para garantir que o Python leia o JSON perfeitamente
    try:
        if "```json" in resposta_ia:
            resposta_ia = resposta_ia.split("```json")[1].split("```")[0]
        elif "```" in resposta_ia:
            resposta_ia = resposta_ia.split("```")[1].split("```")[0]
            
        dados = json.loads(resposta_ia.strip())
        return [p.lower() for p in dados.get("principios_ativos", [])]
    except:
        return []
