import requests
from motor_anvisa import buscar_bula_anvisa

def consultar_llm_com_healer(prompt, chaves_api):
    """
    HEALER ENGINE (Modo Diagnóstico Ativado):
    Tenta acessar as IAs em ordem de prioridade. Se falhar, registra o motivo exato 
    para identificarmos o gargalo de comunicação.
    """
    erros_detalhados = []
    
    # Rota 1: OpenAI
    if chaves_api.get('openai'):
        try:
            url = "https://api.openai.com/v1/chat/completions"
            payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['openai']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'], "OpenAI"
            else:
                erros_detalhados.append(f"OpenAI Recusou ({res.status_code}): {res.text}")
        except Exception as e:
            erros_detalhados.append(f"OpenAI Erro de Rede: {str(e)}")
    else:
        erros_detalhados.append("Chave OpenAI não encontrada no cofre.")

    # Rota 2: Gemini
    if chaves_api.get('gemini'):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={chaves_api['gemini']}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
            
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini"
            else:
                erros_detalhados.append(f"Gemini Recusou ({res.status_code}): {res.text}")
        except Exception as e:
            erros_detalhados.append(f"Gemini Erro de Rede: {str(e)}")
    else:
        erros_detalhados.append("Chave Gemini não encontrada no cofre.")

    # Rota 3: Groq
    if chaves_api.get('groq'):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            payload = {"model": "llama3-8b-8192", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['groq']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'], "Groq"
            else:
                erros_detalhados.append(f"Groq Recusou ({res.status_code}): {res.text}")
        except Exception as e:
            erros_detalhados.append(f"Groq Erro de Rede: {str(e)}")
    else:
        erros_detalhados.append("Chave Groq não encontrada no cofre.")

    # Se todas as rotas falharam, juntamos todos os erros para mostrar na tela
    motivo_real = " | ".join(erros_detalhados)
    return None, f"⚠️ FALHA NAS APIs: {motivo_real}"

def diagnostico_autonomo_completo(sintomas, idade, peso, chaves_api):
    """Orquestração Multi-IA, Auditoria e Integração ANVISA"""
    
    prompt_consulta = f"""
    Atue como um médico especialista. Paciente: {idade} anos, {peso}kg.
    Quadro clínico: "{sintomas}".
    Responda EXATAMENTE neste formato:
    Princípio Ativo: [NOME DO REMÉDIO GENÉRICO]
    Posologia: [DOSE CALCULADA EM MG/ML/GOTAS BASEADA NOS {peso}KG]
    Contraindicações: [ALERTAS]
    """
    
    prontuario_cru, provedor_usado = consultar_llm_com_healer(prompt_consulta, chaves_api)
    
    # Se a IA não retornou o prontuário, devolvemos a mensagem de erro exata capturada no Healer
    if not prontuario_cru:
        return None, provedor_usado

    prompt_auditoria = f"""
    Você é um Auditor Clínico de Inteligência Artificial.
    Avalie esta prescrição para um paciente de {idade} anos e {peso}kg:
    "{prontuario_cru}"
    
    A dose matemática informada é absurdamente letal/tóxica ou está dentro de padrões seguros?
    Se for letal, reescreva corrigindo a dose imediatamente. Se estiver segura, apenas repita a prescrição melhorando a formatação Markdown.
    """
    
    prontuario_auditado, _ = consultar_llm_com_healer(prompt_auditoria, chaves_api)
    
    if not prontuario_auditado:
        return None, "A IA de auditoria falhou. A prescrição não pode ser liberada sem auditoria de segurança."
    
    principio_alvo = ""
    for linha in prontuario_cru.split('\n'):
        if "Princípio Ativo:" in linha or "Principio Ativo:" in linha:
            principio_alvo = linha.split(":")[1].strip().split()[0].replace(',', '')
            break
            
    link_bula = None
    if principio_alvo:
        link_bula = buscar_bula_anvisa(principio_alvo)

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

    return {"Provedor Usado": provedor_usado}, relatorio_final
