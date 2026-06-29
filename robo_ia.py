import json
import requests
from motor_dados import carregar_banco_medicamentos, buscar_apresentacoes

def consultar_llm_com_healer(prompt, chaves_api):
    if chaves_api.get('openrouter'):
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            payload = {"model": "meta-llama/llama-3.1-8b-instruct", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['openrouter']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            if res.status_code == 200: return res.json()['choices'][0]['message']['content'], "OpenRouter"
        except: pass

    if chaves_api.get('groq'):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['groq']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            if res.status_code == 200: return res.json()['choices'][0]['message']['content'], "Groq"
        except: pass

    return None, "⚠️ FALHA NAS APIs"

def listar_opcoes_tratamento(sintomas, alergias, chaves_api):
    prompt = f"""
    Atue como Farmacêutico Clínico rigoroso.
    Paciente: Sintomas "{sintomas}". Alergias: "{alergias}".
    Liste 4 Princípios Ativos genéricos altamente indicados para o quadro.
    Responda ESTRITAMENTE em formato JSON:
    {{"opcoes": ["Principio1", "Principio2", "Principio3", "Principio4"]}}
    """
    
    resposta, _ = consultar_llm_com_healer(prompt, chaves_api)
    
    try:
        if "
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

*Pronto!* Salve todos eles e abra o seu Streamlit. Ele vai ler a sua planilha `medicamentos.csv` e usar as 3 etapas de atendimento que desenvolvemos. Me dê o sinal verde se deu tudo certo!
