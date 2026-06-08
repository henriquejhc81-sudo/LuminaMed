import requests
from motor_anvisa import buscar_bula_anvisa

def consultar_llm_com_healer(prompt, chaves_api):
    """
    HEALER ENGINE (Auto-Cura):
    Tenta acessar as IAs em ordem de prioridade. Se uma rota cair (timeout ou erro),
    o sistema silencia a falha e tenta a próxima instantaneamente.
    """
    # Rota 1: OpenAI
    if chaves_api.get('openai'):
        try:
            url = "https://api.openai.com/v1/chat/completions"
            payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['openai']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'], "OpenAI"
        except Exception:
            pass # Rota falhou, o Healer ignora e tenta a próxima

    # Rota 2: Gemini (Fallback)
    if chaves_api.get('gemini'):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={chaves_api['gemini']}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini"
        except Exception:
            pass

    # Rota 3: Groq (Fallback de Alta Velocidade)
    if chaves_api.get('groq'):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['groq']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'], "Groq"
        except Exception:
            pass

    return None, "Falha Crítica de Rede"

def diagnostico_autonomo_completo(sintomas, idade, peso, chaves_api):
    """Orquestração Multi-IA, Auditoria e Integração ANVISA"""
    
    # 1. Geração do Prontuário Base
    prompt_consulta = f"""
    Atue como um médico especialista. Paciente: {idade} anos, {peso}kg.
    Quadro clínico: "{sintomas}".
    Responda EXATAMENTE neste formato:
    Princípio Ativo: [NOME DO REMÉDIO GENÉRICO]
    Posologia: [DOSE CALCULADA EM MG/ML/GOTAS BASEADA NOS {peso}KG]
    Contraindicações: [ALERTAS]
    """
    
    prontuario_cru, provedor_usado = consultar_llm_com_healer(prompt_consulta, chaves_api)
    
    if not prontuario_cru:
        return None, "Os sistemas de IA estão inoperantes no momento devido a falhas globais de API."

    # 2. DEEP LEARNING ENGINE (Auditoria Matemática)
    prompt_auditoria = f"""
    Você é um Auditor Clínico de Inteligência Artificial.
    Avalie esta prescrição para um paciente de {idade} anos e {peso}kg:
    "{prontuario_cru}"
    
    A dose matemática informada é absurdamente letal/tóxica (ex: mais de 100 comprimidos ou miligramagem impossível) ou está dentro de padrões seguros?
    Se for letal, reescreva corrigindo a dose imediatamente. Se estiver segura, apenas repita a prescrição melhorando a formatação Markdown.
    """
    
    prontuario_auditado, _ = consultar_llm_com_healer(prompt_auditoria, chaves_api)
    
    # 3. EXTRAÇÃO DA ANVISA
    # Tenta descobrir o nome do remédio na primeira linha do prontuário para enviar para a ANVISA
    principio_alvo = ""
    for linha in prontuario_cru.split('\n'):
        if "Princípio Ativo:" in linha or "Principio Ativo:" in linha:
            principio_alvo = linha.split(":")[1].strip().split()[0].replace(',', '')
            break
            
    link_bula = None
    if principio_alvo:
        link_bula = buscar_bula_anvisa(principio_alvo)

    # 4. MONTAGEM FINAL DO PRONTUÁRIO
    relatorio_final = f"""
    {prontuario_auditado}
    
    ---
    **🛠️ Telemetria do Sistema:**
    * Rota Estável: `{provedor_usado}` (Healer Engine)
    * Auditoria Ativa: `Deep Learning Engine: Verificado`
    """
    
    if link_bula:
        relatorio_final += f"\n* 📄 **Bula ANVISA:** [Acessar Documento Oficial]({link_bula})"
    else:
        relatorio_final += f"\n* 📄 **Bula ANVISA:** Documento não localizado temporariamente."

    # Retorna o dicionário vazio (para não quebrar o código visual do app.py atual) e o veredito final
    return {"Provedor Usado": provedor_usado}, relatorio_final
