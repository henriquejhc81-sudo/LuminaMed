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
        return f"Erro de comunicação com {provedor}: {str(e)}"
    return None

def analisar_consenso_autonomo(sintomas_usuario, idade, peso, chaves_api):
    """O DoctorBot atua de forma autônoma sem depender de banco de dados local"""
    
    prompt = f"""
    Você atua como o 'DoctorBot', um sistema especialista de suporte clínico avançado.
    
    DADOS DO PACIENTE:
    - Idade: {idade} anos
    - Peso: {peso} kg
    - Quadro relatado: "{sintomas_usuario}"
    
    Com base na medicina baseada em evidências e na farmacologia, forneça um prontuário rigoroso e estruturado contendo:
    1. 🩺 **Hipóteses Clínicas Preliminares:** Possíveis causas dos sintomas.
    2. 💊 **Princípios Ativos Indicados:** Sugestões de tratamento para alívio.
    3. ⚖️ **Posologia Calculada:** Faça o cálculo matemático rigoroso da dose (em mg, ml ou gotas) baseado EXATAMENTE no peso ({peso}kg) e idade ({idade} anos) do paciente para cada medicação.
    4. ⚠️ **Contraindicações:** Alertas e alergias cruzadas a serem evitadas.
    
    Use a formatação Markdown. Seja didático, objetivo e separe as seções claramente.
    No final, adicione o seguinte aviso em negrito: "AVISO: Esta é uma análise gerada por Inteligência Artificial autônoma. Não substitui a consulta médica. Sempre valide a posologia com um profissional de saúde."
    """
    
    respostas = []
    
    # Executa a chamada para as IAs disponíveis no cofre
    if chaves_api.get('openai'):
        res = consultar_llm("openai", chaves_api['openai'], prompt)
        if res: respostas.append(("OpenAI", res))
        
    if chaves_api.get('gemini'):
        res = consultar_llm("gemini", chaves_api['gemini'], prompt)
        if res: respostas.append(("Gemini", res))
        
    if chaves_api.get('groq'):
        res = consultar_llm("groq", chaves_api['groq'], prompt)
        if res: respostas.append(("Groq", res))
        
    return respostas
