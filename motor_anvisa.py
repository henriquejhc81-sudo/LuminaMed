import json
import requests
from motor_dados import carregar_banco_medicamentos, buscar_apresentacoes

# DICIONÁRIO MATEMÁTICO BLINDADO
CORTICOIDES = {
    "Hidrocortisona": {"potencia": 1, "dose_eq": 20, "retencao": "Alta"},
    "Prednisona": {"potencia": 4, "dose_eq": 5, "retencao": "Baixa"},
    "Prednisolona": {"potencia": 4, "dose_eq": 5, "retencao": "Baixa"},
    "Dexametasona": {"potencia": 30, "dose_eq": 0.75, "retencao": "Nula"},
    "Betametasona": {"potencia": 30, "dose_eq": 0.6, "retencao": "Nula"}
}

def consultar_llm(prompt, chaves_api):
    # Rota 1: OpenRouter
    if chaves_api.get('openrouter'):
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            payload = {"model": "meta-llama/llama-3.1-8b-instruct", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['openrouter']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            if res.status_code == 200: return res.json()['choices'][0]['message']['content'], "OpenRouter"
        except: pass

    # Rota 2: Groq
    if chaves_api.get('groq'):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['groq']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            if res.status_code == 200: return res.json()['choices'][0]['message']['content'], "Groq"
        except: pass

    return None, "FALHA"

def listar_opcoes_tratamento(sintomas, alergias, chaves_api):
    prompt = f"""
    Atue como Farmacêutico Clínico. Paciente relata: "{sintomas}". Alergias: "{alergias}".
    Liste APENAS o nome genérico de 4 princípios ativos indicados para o quadro.
    Responda ESTRITAMENTE em JSON: {{"opcoes": ["Remedio1", "Remedio2", "Remedio3", "Remedio4"]}}
    """
    resposta, _ = consultar_llm(prompt, chaves_api)
    
    try:
        if "```json" in resposta: resposta = resposta.split("```json")[1].split("```")[0]
        elif "```" in resposta: resposta = resposta.split("```")[1].split("```")[0]
        dados_ia = json.loads(resposta.strip()).get("opcoes", [])
    except:
        dados_ia = ["Ibuprofeno", "Dipirona", "Amoxicilina", "Dexametasona"]
        
    banco_csv = carregar_banco_medicamentos()
    opcoes_enriquecidas = []
    
    for remedio in dados_ia:
        apresentacoes = buscar_apresentacoes(remedio, banco_csv)
        if apresentacoes:
            opcoes_enriquecidas.append(f"{remedio} (No estoque: {', '.join(apresentacoes[:2])})")
        else:
            opcoes_enriquecidas.append(f"{remedio} (Dose a calcular)")
            
    return opcoes_enriquecidas

def gerar_prontuario_final(principio, sintomas, idade, peso, alergias, chaves_api):
    primeiro_nome = principio.split()[0].title()
    alerta_matematico = ""
    
    if primeiro_nome in CORTICOIDES:
        dados = CORTICOIDES[primeiro_nome]
        alerta_matematico = f"REGRA: Este é um corticoide. Potência: {dados['potencia']}x. Dose base: {dados['dose_eq']}mg. Use isso no cálculo."

    prompt_consulta = f"""
    Prescrição: {principio}.
    Paciente: {idade} anos, {peso}kg. Sintomas: {sintomas}. Alergias: {alergias}.
    {alerta_matematico}
    
    Estrutura obrigatória do prontuário:
    - Princípio Ativo
    - Para que serve
    - Posologia Matemática (baseada em {peso}kg)
    - Alergias e Alternativas Seguras
    - Contraindicações
    """
    
    prontuario, provedor = consultar_llm(prompt_consulta, chaves_api)
    
    relatorio = f"{prontuario}\n\n---\n**🛠️ Telemetria:** Motor Ativo: `{provedor}` | Banco de Dados: `CSV Integrado`"
    return relatorio
