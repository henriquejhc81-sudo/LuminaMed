import json
import requests

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
        else: return None
            
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        if res.status_code == 200: return res.json()['choices'][0]['message']['content']
    except Exception: pass
    return None

def listar_opcoes_tratamento(sintomas, alergias, uso_continuo, chaves_api):
    prompt = f"""
    Atue como Farmacêutico Clínico Sênior. 
    Quadro do Paciente: "{sintomas}". Alergias: "{alergias}". Uso Contínuo: "{uso_continuo}".
    
    DIRETRIZES DE SEGURANÇA MÁXIMA (GUARDRAILS):
    1. ALERGIAS CRUZADAS: Se o paciente tem alergia a um princípio ativo, VOCÊ É PROIBIDO de sugerir medicamentos da mesma classe farmacológica.
    2. USO CONTÍNUO: NÃO sugira medicamentos que tenham interação com os de uso contínuo relatados.
    
    Liste até 8 princípios ativos altamente indicados.
    Responda ESTRITAMENTE em formato JSON: {{"opcoes": ["Principio1", "Principio2", "Principio3"]}}
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
    
    if not resposta: return ["Falha na conexão com a IA."]
        
    try:
        if "
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1

### 🚀 O Passo a Passo de Retomada:
1. Cole esses três arquivos no seu GitHub e não se esqueça de colocar as suas **Chaves de API** originais no topo do `app.py`.
2. Faça o **Commit**.
3. No painel do Streamlit, vá em "Manage app" (ou nos três pontinhos) e faça o **Clear Cache** pela última vez. 

Esse é o código de ponta a ponta limpo, integrado e indestrutível. Pode testar!
