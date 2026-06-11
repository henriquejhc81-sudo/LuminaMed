import requests
import urllib.parse

# ---------------------------------------------------------
# MÓDULO DE INTEGRAÇÃO ANVISA (Evolução do BulaController V1)
# ---------------------------------------------------------

def buscar_bula_anvisa(nome_medicamento, principio_ativo):
    """
    Simula a consulta ao portal da Anvisa para resgatar o link da bula.
    Garante que a funcionalidade do Node.js antigo seja preservada e aprimorada no Python.
    """
    print(f"📡 Iniciando varredura na Anvisa para: {nome_medicamento}...")
    
    # Tratamento de texto para URL (ex: "Dipirona Sódica" vira "Dipirona%20S%C3%B3dica")
    termo_busca = urllib.parse.quote(nome_medicamento)
    
    # URL de busca do Bulário Eletrônico da Anvisa (Padrão Oficial)
    url_bulario = f"https://consultas.anvisa.gov.br/#/bulario/q/?nomeProduto={termo_busca}"
    
    # Construção do pacote de dados da bula
    dados_bula = {
        "status": "sucesso",
        "medicamento": nome_medicamento,
        "principio_ativo": principio_ativo,
        "link_consulta": url_bulario,
        "mensagem_medico": "Link oficial gerado para consulta da bula do paciente e do profissional."
    }
    
    # Se estivéssemos consumindo uma API JSON da Anvisa, o código faria:
    # response = requests.get(api_url)
    # if response.status_code == 200: return response.json()
    
    return dados_bula

def extrair_alertas_anvisa(principio_ativo):
    """
    Cruza o princípio ativo com restrições conhecidas da agência reguladora.
    """
    alertas_criticos = {
        "DIPIRONA": "Risco de agranulocitose (raro). Proibido em alguns países, permitido pela Anvisa.",
        "IBUPROFENO": "Evitar uso prolongado em pacientes com insuficiência renal ou histórico de úlcera.",
        "AMOXICILINA": "Verificar histórico de hipersensibilidade a penicilinas.",
        "CORTICOIDE": "Uso prolongado requer desmame gradual para evitar insuficiência adrenal."
    }
    
    for chave, alerta in alertas_criticos.items():
        if chave in principio_ativo.upper():
            return alerta
            
    return "Nenhum alerta crítico fora do padrão na base de extração rápida."

# Teste isolado do motor
if __name__ == "__main__":
    resultado = buscar_bula_anvisa("Amoxicilina", "Amoxicilina Tri-hidratada")
    print("\n✅ Resultado da Integração Anvisa:")
    print(f"Link: {resultado['link_consulta']}")
    print(f"Alerta: {extrair_alertas_anvisa(resultado['principio_ativo'])}")
