import requests

def buscar_bula_anvisa(principio_ativo):
    """
    Motor independente em Python que acessa a API aberta da ANVISA
    para buscar o link do PDF oficial da bula do paciente.
    """
    # Endpoint público de pesquisa de bulário
    url_busca = f"https://consultas.anvisa.gov.br/api/consulta/bulario?count=1&filter[nomeProduto]={principio_ativo}"
    
    # Headers para simular um navegador real e evitar bloqueios da ANVISA
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json, text/plain, */*"
    }
    
    try:
        # O Healer Engine começa aqui: Timeout rápido para não travar o sistema
        resposta = requests.get(url_busca, headers=headers, timeout=5)
        
        if resposta.status_code == 200:
            dados = resposta.json()
            
            # Se a ANVISA retornar conteúdo
            if dados.get("content") and len(dados["content"]) > 0:
                # Extrai o ID protegido da bula do paciente
                id_bula = dados["content"][0].get("idBulaPacienteProtegido")
                
                if id_bula:
                    # Retorna o link oficial de download do PDF
                    return f"https://consultas.anvisa.gov.br/api/consulta/medicamentos/arquivo/bula/parecer/{id_bula}/?Authorization="
                    
        return None
    except Exception as e:
        # Se a ANVISA cair, o Healer Engine silencia o erro
        return None
