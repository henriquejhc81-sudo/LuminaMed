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
            opcoes_enriquecidas.append(f"{remedio} (Disponível em: {', '.join(apresentacoes[:3])})")
        else:
            opcoes_enriquecidas.append(f"{remedio} (Dose a calcular clinicamente)")
            
    return opcoes_enriquecidas

def gerar_prontuario_final(principio_escolhido, sintomas, idade, peso, alergias, chaves_api):
    prompt_consulta = f"""
    Prescrição alvo: {principio_escolhido}.
    Paciente: {idade} anos, {peso}kg. Sintomas: {sintomas}. Alergias: {alergias if alergias else 'Nenhuma'}.
    Gere a prescrição final.
    Regra 1: A posologia DEVE usar a apresentação específica informada na prescrição alvo se existir.
    Regra 2: Calcule a dose correta em mg/kg/dia baseada no peso de {peso}kg.
    Estrutura:
    - Princípio Ativo e Classe
    - Indicação / Para que serve
    - Posologia Matemática Exata
    - Alergias e Alternativas
    - Contraindicações
    """
    
    prontuario_cru, provedor = consultar_llm_com_healer(prompt_consulta, chaves_api)
    if not prontuario_cru: return None, provedor

    nome_bula = principio_escolhido.split()[0].split('(')[0].strip()
    link_bula = f"https://consultas.anvisa.gov.br/#/medicamentos/q/?nomeProduto={nome_bula}"

    relatorio_final = f"""
{prontuario_cru}
    
---
**🛠️ Telemetria do Sistema:**
* Motor Ativo: `{provedor}`
* Integração de Dados: `Data Warehouse Ativo (CSV)`
* 📄 **Bula Oficial (ANVISA):** [Buscar Documento]({link_bula})
    """
    return relatorio_final
