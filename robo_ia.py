import json
import re
import requests

def consultar_llm_direto(provedor, prompt, chave):
    if not chave:
        return None
        
    try:
        if provedor == "openrouter":
            url = "https://openrouter.ai/api/v1/chat/completions"
            payload = {"model": "meta-llama/llama-3.1-8b-instruct", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
        elif provedor == "groq":
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {"model": "llama3-70b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
        else: 
            return None
            
        headers = {"Authorization": f"Bearer {chave}", "Content-Type": "application/json"}
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        
        if res.status_code == 200: 
            return res.json()['choices'][0]['message']['content']
    except requests.exceptions.RequestException as e:
        print(f"Erro na API {provedor}: {e}")
    return None

def listar_opcoes_tratamento(sintomas, alergias, uso_continuo, chaves_api):
    prompt = f"""
    Atue como Farmacêutico Clínico Sênior. 
    Quadro: "{sintomas}". Alergias: "{alergias}". Uso Contínuo: "{uso_continuo}".
    
    DIRETRIZES DE SEGURANÇA: Evite alergias cruzadas e interações medicamentosas.
    Liste até 8 princípios ativos genéricos para o tratamento.
    
    IMPORTANTE: Retorne APENAS um JSON válido no formato abaixo, sem nenhum texto introdutório ou formatação Markdown:
    {{"opcoes": ["Principio1", "Principio2"]}}
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: 
        resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
    
    if not resposta: 
        return ["Falha na conexão com as IAs (Verifique suas chaves no Secrets)."]
        
    try:
        # Usa Regex para capturar e extrair exatamente o bloco JSON, ignorando conversas extras
        match = re.search(r'\{.*\}', resposta.strip(), re.DOTALL)
        if match:
            texto_json = match.group(0)
            dados = json.loads(texto_json)
            return dados.get("opcoes", ["Nenhuma opção encontrada no JSON."])
        else:
            return ["Erro: A IA não formatou a resposta em JSON."]
    except json.JSONDecodeError:
        return ["Erro: A IA gerou um formato inválido ou corrompido."]
    except Exception as e:
        return [f"Erro interno de processamento: {str(e)}"]

def gerar_prontuario_final(escolha_final, dados_paciente, chaves_api):
    prompt = f"""
    Atue como Médico e Farmacêutico. Escreva um Prontuário em Markdown.
    DADOS: {dados_paciente}
    MEDICAMENTO: {escolha_final}
    
    Inclua: Princípio Ativo, Posologia Sugerida baseada no peso/idade, Análise Renal e Contraindicações.
    Adicione o link exato: [Consultar Bula ANVISA](https://consultas.anvisa.gov.br/#/bulario/q/?nomeProduto={escolha_final.split()[0].replace(' ', '%20')})
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: 
        resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
        
    return resposta if resposta else "Falha na auditoria final (IAs indisponíveis)."
