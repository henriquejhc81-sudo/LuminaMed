import json
import requests
from motor_dados import carregar_banco_medicamentos, buscar_apresentacoes

def consultar_llm_direto(provedor, prompt, chave):
    try:
        if provedor == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
            payload = {"model": "meta-llama/llama-3.1-8b-instruct", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
        elif provedor == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
        else:
            return None
            
        res = requests.post(url, json=payload, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
    except:
        pass
    return None

def listar_opcoes_tratamento(sintomas, alergias, chaves_api):
    prompt = f"""
    Atue como Farmacêutico. Usuário digitou: "{sintomas}". Alergias: "{alergias}".
    1. Se for nome de remédio (ex: Amoxicilina), liste ele e 2 da mesma classe.
    2. Se for sintoma, liste de 5 a 8 princípios ativos indicados.
    Responda ESTRITAMENTE em JSON: {{"opcoes": ["Remedio1", "Remedio2"]}}
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
    
    try:
        if "
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

Se o botão de copiar não aparecer e precisar de selecionar com o rato, desça até à **última linha de cada código** e confirme que apanhou até à última palavra! Pode salvar no GitHub e o ecrã vermelho desaparecerá na hora.
