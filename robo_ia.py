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
    
    DIRETRIZES CLÍNICAS RIGOROSAS (NÃO IGNORE):
    1. ANTIBIÓTICOS: NUNCA sugira antibióticos (ex: Amoxicilina, Azitromicina) a menos que haja SINAIS CLAROS de infecção bacteriana (pus, febre alta prolongada). Para "tosse com secreção", "gripe" ou "resfriado", prescreva EXPECTORANTES (ex: Ambroxol, Acetilcisteína) e MUCOLÍTICOS.
    2. ALERGIA CRUZADA: O paciente tem alergia a "{alergias}". É PROIBIDO sugerir medicamentos da mesma família farmacológica. Exemplo: se tem alergia a Iodo, não sugira compostos iodados.
    
    SUA TAREFA:
    Liste até 6 princípios ativos genéricos PERFEITAMENTE adequados e seguros para o quadro.
    
    Retorne APENAS um JSON válido no formato abaixo, sem texto explicativo, formatação ou markdown:
    {{"opcoes": ["Principio1", "Principio2"]}}
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: 
        resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
    
    if not resposta: 
        return ["Falha na conexão com as IAs (Verifique suas chaves no Secrets)."]
        
    try:
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

def gerar_prontuario_final(substancia, apresentacoes_reais, tarja, dados_paciente, chaves_api):
    # Garantia contra TypeError (Variáveis nulas)
    substancia_segura = str(substancia) if substancia else "Medicamento Genérico"
    
    prompt = f"""
    Atue como Médico e Farmacêutico. Escreva um Prontuário Clínico Profissional em Markdown.
    
    DADOS DO PACIENTE: {dados_paciente}
    MEDICAMENTO ESCOLHIDO: {substancia_segura}
    CLASSE DE RECEITA: {tarja}
    
    LISTA DE APRESENTAÇÕES FÍSICAS NO ESTOQUE DA FARMÁCIA:
    {apresentacoes_reais}
    
    DIRETRIZES DO LAUDO:
    1. ESCOLHA DE APRESENTAÇÃO: Analise a idade e peso do paciente e ESCOLHA UMA das apresentações exatas da lista acima (ex: suspensão oral para pediatria, comprimido para adulto).
    2. POSOLOGIA MATEMÁTICA: Calcule a dose (mg/ml, gotas ou unidade) baseada ESTRITAMENTE na concentração da apresentação que você escolheu. 
    3. INCLUA: Alertas da Tarja, Análise de Interação Medicamentosa e Função Renal.
    4. Adicione o link de validação: [Consultar Bula ANVISA](https://consultas.anvisa.gov.br/#/bulario/q/?nomeProduto={substancia_segura.split()[0].replace(' ', '%20')})
    """
    
    resposta = consultar_llm_direto("groq", prompt, chaves_api.get('groq'))
    if not resposta: 
        resposta = consultar_llm_direto("openrouter", prompt, chaves_api.get('openrouter'))
        
    return str(resposta) if resposta else "Falha na geração do Prontuário: Motores de IA Indisponíveis."
