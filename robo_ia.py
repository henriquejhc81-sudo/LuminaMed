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
    Atue como Farmacêutico Clínico Sênior em um Sistema de Suporte à Decisão (CDSS).
    
    PERFIL DO PACIENTE:
    - Quadro Clínico: "{sintomas}"
    - Alergias Declaradas: "{alergias}"
    - Uso Contínuo: "{uso_continuo}"
    
    DIRETRIZES CLÍNICAS RIGOROSAS:
    1. ANTIBIÓTICOS: NUNCA sugira antibióticos a menos que haja SINAIS CLAROS de infecção bacteriana (pus, febre alta persistente). Para quadros comuns respiratórios, prefira EXPECTORANTES, ANTITUSSÍGENOS ou ANTI-HISTAMÍNICOS.
    2. ALERGIA CRUZADA: Evite sugerir qualquer medicamento da mesma família de substâncias às quais o paciente é alérgico.
    
    Retorne APENAS um JSON válido no formato abaixo com até 6 princípios ativos. Não adicione texto ou markdown:
    {{"opcoes": ["Principio1", "Principio2"]}}
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: 
        resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
    
    if not resposta: 
        return ["Falha na conexão com as IAs."]
        
    try:
        match = re.search(r'\{.*\}', resposta.strip(), re.DOTALL)
        if match:
            dados = json.loads(match.group(0))
            return dados.get("opcoes", ["Nenhuma opção encontrada no JSON."])
        return ["Erro: A IA não formatou a resposta em JSON."]
    except Exception as e:
        return [f"Erro na decodificação JSON da IA: {str(e)}"]

# AQUI ESTÁ A CORREÇÃO DA ASSINATURA DA FUNÇÃO (5 Parâmetros)
def gerar_prontuario_final(substancia, apresentacoes_reais, tarja, dados_paciente, chaves_api):
    substancia_segura = str(substancia) if substancia else "Medicamento Genérico"
    
    prompt = f"""
    Atue como Médico e Farmacêutico. Escreva um Prontuário Clínico Profissional em Markdown.
    
    DADOS DO PACIENTE: {dados_paciente}
    BASE QUÍMICA (SUBSTÂNCIA): {substancia_segura}
    CLASSE DE RECEITA: {tarja}
    
    INVENTÁRIO FÍSICO DA FARMÁCIA (MARCAS E APRESENTAÇÕES DISPONÍVEIS):
    {apresentacoes_reais}
    
    DIRETRIZES DO LAUDO:
    1. ESCOLHA DE ESTOQUE: Analise a idade e peso do paciente e escolha UMA embalagem/marca/apresentação EXATA da lista de inventário acima.
    2. POSOLOGIA MATEMÁTICA: Calcule a dose baseada ESTRITAMENTE na concentração da caixa que você escolheu. 
    3. INCLUA: Análise de Interação Medicamentosa, Categoria da Tarja escolhida e Função Renal.
    4. Adicione o link de bula: [Consultar Bula ANVISA](https://consultas.anvisa.gov.br/#/bulario/q/?nomeProduto={substancia_segura.split()[0].replace(' ', '%20')})
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: 
        resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
        
    return str(resposta) if resposta else "Falha na geração do Prontuário: Motores de IA Indisponíveis."
