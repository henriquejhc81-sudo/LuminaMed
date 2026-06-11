import os
import google.generativeai as genai
from dotenv import load_dotenv

# ---------------------------------------------------------
# 1. INICIALIZAÇÃO DA MATRIZ DA IA
# ---------------------------------------------------------
# Carrega variáveis de ambiente (para uso local)
load_dotenv()

def configurar_nexus_ai():
    """
    Inicializa o motor de Inteligência Artificial usando a chave de API.
    A arquitetura está pronta para evoluir para Multi-LLM no futuro.
    """
    # Busca a chave de segurança nas configurações do ambiente
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        return None
        
    genai.configure(api_key=api_key)
    
    # Instanciando o modelo atualizado para análises complexas
    # Pode ser expandido futuramente com LangChain para OpenAI ou Anthropic
    modelo = genai.GenerativeModel('gemini-1.5-pro')
    return modelo

# ---------------------------------------------------------
# 2. MOTOR DE PROCESSAMENTO CLÍNICO (A Evolução do V6)
# ---------------------------------------------------------
def analisar_caso_clinico(sintomas, idade, peso, lista_tratamentos):
    """
    Recebe os dados brutos calculados pelo app.py e gera uma segunda opinião
    farmacológica e alertas humanizados para o médico.
    """
    modelo = configurar_nexus_ai()
    
    if not modelo:
        return "⚠️ **Sistema Nexus em modo de espera:** Chave da API (GEMINI_API_KEY) não detectada nas configurações secretas do Streamlit."

    # Se o motor matemático não encontrou nada, a IA não inventa dados
    if not lista_tratamentos:
        return "O motor matemático não encontrou medicamentos correspondentes para iniciar a análise."

    # Formatando a lista de remédios para o cérebro da IA ler
    tratamentos_formatados = ""
    for t in lista_tratamentos:
        tratamentos_formatados += f"- {t['medicamento']} ({t['apresentacao']}) | Dose: {t['prescricao']} | Alergia: {t['alerta_alergia']}\n"

    # ---------------------------------------------------------
    # 3. ENGENHARIA DE PROMPT (A Personalidade do Nexus)
    # ---------------------------------------------------------
    prompt_sistema = f"""
    Você é o Nexus, a inteligência artificial do sistema médico Lumina Med.
    Sua função é auxiliar profissionais de saúde analisando os resultados gerados pelo nosso motor matemático de prescrição.
    
    📋 DADOS DO PACIENTE:
    - Idade: {idade} anos
    - Peso: {peso} kg
    - Quadro / Classe Buscada: {sintomas}
    
    💊 OPÇÕES DE TRATAMENTO CALCULADAS PELO SISTEMA:
    {tratamentos_formatados}
    
    🎯 SUA TAREFA:
    1. Faça um breve resumo clínico sobre a adequação dessas opções para a idade e peso do paciente.
    2. Destaque os alertas de alergia de forma chamativa (em bullet points).
    3. Informe se existe algum cuidado geral associado a essa classe de medicamentos (ex: irritação gástrica, sonolência).
    
    REGRAS RÍGIDAS:
    - Nunca altere as dosagens fornecidas na lista acima. As doses são definitivas.
    - Mantenha um tom profissional, direto e científico.
    - Seja conciso (máximo de 3 parágrafos curtos).
    """
    
    try:
        # Gera a resposta com base no contexto estruturado
        resposta = modelo.generate_content(prompt_sistema)
        return resposta.text
    except Exception as e:
        return f"❌ **Erro na matriz de comunicação com a IA:** {e}"

# ---------------------------------------------------------
# 4. TESTE DE IGNIÇÃO (Apenas executado se rodar o arquivo direto)
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Iniciando diagnóstico dos sistemas do Nexus AI...")
    if configurar_nexus_ai():
        print("✅ Motor IA operacional. Chave de API reconhecida.")
    else:
        print("⚠️ Motor IA offline. Configure a variável GEMINI_API_KEY.")
