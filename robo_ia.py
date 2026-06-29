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
            
        res = requests.post(url, json=payload, headers=headers, timeout=12)
        if res.status_code == 200:
            return res.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"Erro no provedor {provedor}: {e}")
        pass
    return None

def listar_opcoes_tratamento(sintomas, alergias, uso_continuo, chaves_api):
    prompt = f"""
    Atue como Farmacêutico Clínico Sênior. 
    Usuário: "{sintomas}". Alergias: "{alergias}". Uso Contínuo: "{uso_continuo}".
    
    DIRETRIZ DE SEGURANÇA:
    NÃO sugira medicamentos que tenham interação grave com os medicamentos de Uso Contínuo relatados.
    
    1. Se for nome de remédio, liste ele e 2 alternativas da mesma classe (se seguro).
    2. Se for sintoma, liste de 8 a 12 princípios ativos altamente indicados.
    Responda ESTRITAMENTE em JSON: {{"opcoes": ["Remedio1", "Remedio2", "Remedio3"]}}
    """
    
    # Tenta Groq primeiro, se falhar tenta OpenRouter
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: 
        resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
    
    if not resposta:
        return ["Falha na conexão com a Inteligência Artificial. Verifique as Chaves API."]
        
    try:
        # Limpeza inteligente: As IAs costumam mandar o JSON dentro de blocos de formatação Markdown (```json)
        texto_limpo = resposta
        if "```json" in texto_limpo:
            texto_limpo = texto_limpo.split("```json")[1].split("```")[0]
        elif "```" in texto_limpo:
            texto_limpo = texto_limpo.split("```")[1].split("```")[0]
            
        dados = json.loads(texto_limpo.strip())
        return dados.get("opcoes", ["Nenhuma opção encontrada na resposta da IA."])
    except Exception as e:
        return [f"Erro ao ler os dados da IA: {str(e)}"]

def gerar_prontuario_final(dados_sessao, chaves_api):
    """
    Função necessária para não gerar erro de importação no app.py
    Gera o resumo final do atendimento.
    """
    prompt = f"""
    Atue como Médico Clínico. Escreva um Prontuário rápido (Resumo do Atendimento) 
    com base nestas informações: {dados_sessao}.
    Seja claro, objetivo e profissional.
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta:
        resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
        
    return resposta if resposta else "Falha ao gerar o prontuário final."
