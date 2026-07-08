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
    Quadro: "{sintomas}". Alergias: "{alergias}". Uso Contínuo: "{uso_continuo}".
    
    DIRETRIZES DE SEGURANÇA MÁXIMA:
    1. ALERGIAS CRUZADAS: Se o paciente tem alergia a um princípio ativo, NÃO sugira medicamentos da mesma classe farmacológica (ex: Família dos AINEs como Ibuprofeno/Flurbiprofeno).
    2. USO CONTÍNUO: NÃO sugira medicamentos que tenham interação.
    
    Liste até 8 princípios ativos altamente indicados.
    Responda ESTRITAMENTE em formato JSON: {{"opcoes": ["Principio1", "Principio2", "Principio3"]}}
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
    
    if not resposta: return ["Falha na conexão com a IA."]
        
    try:
        texto_limpo = resposta
        if "```json" in texto_limpo:
            texto_limpo = texto_limpo.split("```json")[1].split("```")[0]
        elif "```" in texto_limpo:
            texto_limpo = texto_limpo.split("```")[1].split("```")[0]
            
        dados = json.loads(texto_limpo.strip())
        return dados.get("opcoes", ["Nenhuma opção encontrada."])
    except Exception:
        return ["Erro ao ler os dados da IA."]

def gerar_prontuario_final(escolha_final, dados_paciente, chaves_api):
    prompt = f"""
    Atue como Médico Clínico e Farmacêutico. Escreva um Prontuário rápido.
    DADOS: {dados_paciente}
    MEDICAMENTO SELECIONADO: {escolha_final}
    
    DIRETRIZES DO LAUDO (Markdown):
    1. Princípio Ativo e Indicação.
    2. Posologia Matemática Exata.
    3. Análise de Função Renal/Interações.
    4. Contraindicações.
    5. Link para a Bula Oficial da ANVISA: Crie EXATAMENTE este link, substituindo NOME_DO_REMEDIO pelo princípio ativo exato (sem espaços, use %20): 
    [Consultar Bula Oficial na ANVISA](https://consultas.anvisa.gov.br/#/bulario/q/?nomeProduto=NOME_DO_REMEDIO)
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
        
    return resposta if resposta else "Falha de conexão com os motores de IA."
