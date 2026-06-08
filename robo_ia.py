import requests

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
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=15)
            return res.json()['candidates'][0]['content']['parts'][0]['text']
            
        elif provedor == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            return res.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"Erro: {str(e)}"
    return ""

def diagnostico_autonomo_completo(sintomas, idade, peso, chaves_api):
    """Consulta todas as IAs e depois passa pelo Algoritmo Juiz"""
    
    prompt_consulta = f"""
    Atue como um médico especialista. Paciente: {idade} anos, {peso}kg.
    Quadro clínico: "{sintomas}".
    Indique rapidamente:
    1. Princípio ativo sugerido.
    2. Posologia matemática exata (mg, ml ou gotas) calculada estritamente para os {peso}kg.
    3. Contraindicações principais.
    """
    
    opinioes = {}
    
    # 1. Coleta a opinião individual de cada IA
    if chaves_api.get('openai'):
        res = consultar_llm("openai", chaves_api['openai'], prompt_consulta)
        if res and "Erro" not in res: opinioes['OpenAI'] = res
            
    if chaves_api.get('gemini'):
        res = consultar_llm("gemini", chaves_api['gemini'], prompt_consulta)
        if res and "Erro" not in res: opinioes['Gemini'] = res
            
    if chaves_api.get('groq'):
        res = consultar_llm("groq", chaves_api['groq'], prompt_consulta)
        if res and "Erro" not in res: opinioes['Groq'] = res

    if not opinioes:
        return None, "Falha geral de comunicação com as APIs."

    # 2. O Algoritmo Juiz entra em ação
    prompt_juiz = f"""
    Você é o Algoritmo Juiz Clínico. Analise os seguintes pareceres gerados por diferentes IAs para um paciente de {idade} anos e {peso}kg com o quadro: "{sintomas}".
    
    Pareceres coletados:
    {opinioes}
    
    Sua missão:
    Crie um VEREDITO CLÍNICO FINAL unificado. 
    Resolva qualquer divergência matemática na dosagem entre as IAs, escolhendo a mais segura. 
    Gere um prontuário limpo, em formato Markdown, contendo o Princípio Ativo, Posologia Exata e Alertas.
    """
    
    # Elege a OpenAI ou Gemini para ser o Juiz (os modelos mais robustos)
    chave_juiz = chaves_api.get('openai') or chaves_api.get('gemini')
    provedor_juiz = "openai" if chaves_api.get('openai') else "gemini"
    
    veredito_final = consultar_llm(provedor_juiz, chave_juiz, prompt_juiz)
    
    return opinioes, veredito_final
