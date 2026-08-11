import json
import requests
from pydantic import BaseModel, ValidationError

# Estrutura de Validação Pydantic (Sophistication UP!)
class SugestoesTratamento(BaseModel):
    opcoes: list[str]

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
    Retorne ESTRITAMENTE um JSON válido neste formato: {{"opcoes": ["Principio1", "Principio2"]}}. Não adicione nenhum texto explicativo.
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: 
        resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
    
    if not resposta: 
        return ["Falha na conexão com as IAs (Verifique suas chaves)."]
        
    # Tratamento sofisticado e extração segura
    try:
        texto_limpo = resposta.replace("```json", "").replace("```", "").strip()
        # Validação pesada com Pydantic
        dados_validados = SugestoesTratamento.model_validate_json(texto_limpo)
        return dados_validados.opcoes
    except ValidationError:
        return ["Erro: A IA não retornou um formato estruturado válido."]
    except Exception as e:
        return [f"Erro interno de processamento: {str(e)}"]

def gerar_prontuario_final(escolha_final, dados_paciente, chaves_api):
    prompt = f"""
    Atue como Médico e Farmacêutico. Escreva um Prontuário em Markdown.
    DADOS: {dados_paciente}
    MEDICAMENTO: {escolha_final}
    
    Inclua: Princípio Ativo, Posologia Sugerida, Análise Renal e Contraindicações.
    Adicione o link: [Consultar Bula ANVISA](https://consultas.anvisa.gov.br/#/bulario/q/?nomeProduto={escolha_final.split()[0].replace(' ', '%20')})
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: 
        resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
        
    return resposta if resposta else "Falha na auditoria final (IAs indisponíveis)."
