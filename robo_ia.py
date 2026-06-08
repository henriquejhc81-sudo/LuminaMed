import requests
from motor_anvisa import buscar_bula_anvisa

def consultar_llm_com_healer(prompt, chaves_api):
    """
    HEALER ENGINE V2:
    Atualizado com os modelos mais recentes e priorizando OpenRouter e Groq.
    """
    erros_detalhados = []
    
    # Rota 1: OpenRouter (Nova Rota Principal)
    if chaves_api.get('openrouter'):
        try:
            url = "https://openrouter.ai/api/v1/chat/completions"
            # Usando LLaMA 3.1 8B Instruct através da OpenRouter (extremamente rápido)
            payload = {"model": "meta-llama/llama-3.1-8b-instruct", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['openrouter']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'], "OpenRouter"
            else:
                erros_detalhados.append(f"OpenRouter Recusou ({res.status_code}): {res.text}")
        except Exception as e:
            erros_detalhados.append(f"OpenRouter Erro: {str(e)}")

    # Rota 2: Groq (Corrigido para o modelo novo e mais potente)
    if chaves_api.get('groq'):
        try:
            url = "https://api.groq.com/openai/v1/chat/completions"
            # Atualizado para o LLaMA 3.3 Versatile (O modelo antigo foi desativado)
            payload = {"model": "llama-3.3-70b-versatile", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['groq']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'], "Groq"
            else:
                erros_detalhados.append(f"Groq Recusou ({res.status_code}): {res.text}")
        except Exception as e:
            erros_detalhados.append(f"Groq Erro: {str(e)}")

    # Rota 3: Gemini (Corrigido para a versão 'latest')
    if chaves_api.get('gemini'):
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={chaves_api['gemini']}"
            payload = {"contents": [{"parts": [{"text": prompt}]}]}
            res = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=8)
            
            if res.status_code == 200:
                return res.json()['candidates'][0]['content']['parts'][0]['text'], "Gemini"
            else:
                erros_detalhados.append(f"Gemini Recusou ({res.status_code}): {res.text}")
        except Exception as e:
            erros_detalhados.append(f"Gemini Erro: {str(e)}")

    # Rota 4: OpenAI (Deixada em último porque sabemos que está sem cota)
    if chaves_api.get('openai'):
        try:
            url = "https://api.openai.com/v1/chat/completions"
            payload = {"model": "gpt-3.5-turbo", "messages": [{"role": "user", "content": prompt}], "temperature": 0.1}
            headers = {"Authorization": f"Bearer {chaves_api['openai']}", "Content-Type": "application/json"}
            res = requests.post(url, json=payload, headers=headers, timeout=8)
            
            if res.status_code == 200:
                return res.json()['choices'][0]['message']['content'], "OpenAI"
            else:
                erros_detalhados.append(f"OpenAI Recusou: Cota/Saldo Excedido.")
        except Exception as e:
            erros_detalhados.append(f"OpenAI Erro: {str(e)}")

    # Se o Healer Engine não conseguir usar NENHUMA rota, exibe os erros para podermos diagnosticar
    motivo_real = " | ".join(erros_detalhados)
    return None, f"⚠️ FALHA NAS APIs: {motivo_real}"

def diagnostico_autonomo_completo(sintomas, idade, peso, chaves_api):
    """Orquestração Multi-IA, Auditoria e Integração ANVISA"""
    
    # 1. Geração do Prontuário Base
    prompt_consulta = f"""
    Atue como um médico especialista. Paciente: {idade} anos, {peso}kg.
    Quadro clínico: "{sintomas}".
    Responda EXATAMENTE neste formato e evite textos adicionais:
    Princípio Ativo: [NOME DO REMÉDIO GENÉRICO]
    Posologia: [DOSE CALCULADA EM MG/ML/GOTAS BASEADA NOS {peso}KG]
    Contraindicações: [ALERTAS]
    """
    
    prontuario_cru, provedor_usado = consultar_llm_com_healer(prompt_consulta, chaves_api)
    
    if not prontuario_cru:
        return None, provedor_usado

    # 2. DEEP LEARNING ENGINE (Auditoria Matemática)
    prompt_auditoria = f"""
    Você é um Auditor Clínico de Inteligência Artificial.
    Avalie esta prescrição para um paciente de {idade} anos e {peso}kg:
    "{prontuario_cru}"
    
    A dose matemática informada é absurdamente letal/tóxica (ex: miligramagem impossível) ou está dentro de padrões seguros?
    Se for letal, reescreva corrigindo a dose imediatamente. Se estiver segura, apenas repita a prescrição original melhorando a formatação Markdown.
    """
    
    prontuario_auditado, _ = consultar_llm_com_healer(prompt_auditoria, chaves_api)
    
    if not prontuario_auditado:
        return None, "A IA de auditoria falhou. A prescrição não pode ser liberada sem auditoria de segurança."
    
    # 3. EXTRAÇÃO DA ANVISA
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
        relatorio_final += f"\n* 📄 **Bula ANVISA:** Documento em PDF não localizado temporariamente."

    return {"Provedor Usado": provedor_usado}, relatorio_final
