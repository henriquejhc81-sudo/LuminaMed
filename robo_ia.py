import json

# BASE DE CONHECIMENTO CIENTÍFICO INTEGRADA
# (Esta base é a "Constituição" do Lumina Med)

CORTICOIDES = {
    "Hidrocortisona": {"potencia": 1, "dose_eq": 20, "retencao": "Alta"},
    "Cortisona": {"potencia": 0.8, "dose_eq": 25, "retencao": "Alta"},
    "Prednisona": {"potencia": 4, "dose_eq": 5, "retencao": "Baixa"},
    "Prednisolona": {"potencia": 4, "dose_eq": 5, "retencao": "Baixa"},
    "Metilprednisolona": {"potencia": 5, "dose_eq": 4, "retencao": "Nula"},
    "Triancinolona": {"potencia": 5, "dose_eq": 4, "retencao": "Nula"},
    "Dexametasona": {"potencia": 30, "dose_eq": 0.75, "retencao": "Nula"},
    "Betametasona": {"potencia": 30, "dose_eq": 0.6, "retencao": "Nula"}
}

AINEs = {
    "Salicilatos": ["Aspirina (AAS)"],
    "Propiônicos": ["Ibuprofeno", "Naproxeno", "Cetoprofeno", "Flurbiprofeno"],
    "Acéticos": ["Diclofenaco Sódico", "Diclofenaco Potássico", "Cetorolaco", "Aceclofenaco"],
    "Oxicans": ["Piroxicam", "Tenoxicam", "Meloxicam", "Lornoxicam"],
    "Fenamatos": ["Ácido Mefenâmico", "Nimesulida"],
    "Coxibes": ["Celecoxibe", "Etoricoxibe", "Parecoxibe"]
}

def consultar_llm_com_healer(prompt, chaves_api):
    # ... (Manter a mesma função de consulta que já criamos, ela continua funcional)
    pass 

def gerar_prontuario_final(principio, sintomas, idade, peso, alergias, chaves_api):
    """Motor de Prescrição com Validação Cruzada de Base de Dados"""
    
    # 1. Validação de Segurança (A IA é forçada a consultar nossa tabela)
    contexto_tecnico = ""
    if principio in CORTICOIDES:
        dados = CORTICOIDES[principio]
        contexto_tecnico = f"NORMA TÉCNICA CORTICOIDE: Potência {dados['potencia']}x, Dose Equivalente Base {dados['dose_eq']}mg. Retenção: {dados['retencao']}."
    elif any(principio in lista for lista in AINEs.values()):
        contexto_tecnico = "NORMA TÉCNICA AINE: O uso deve considerar proteção gástrica e função renal."

    prompt = f"""
    Como Farmacêutico Clínico, gere a prescrição para: {principio}.
    Paciente: {idade} anos, {peso}kg. Sintomas: {sintomas}. Alergias: {alergias}.
    
    {contexto_tecnico}
    
    REGRA OBRIGATÓRIA: Calcule a dosagem exata baseada no peso do paciente ({peso}kg) e na potência técnica informada.
    NÃO gere prescrição se houver contraindicação com as alergias informadas.
    
    Estrutura:
    - Princípio Ativo e Classe
    - Indicação Clínica
    - Posologia Matemática Exata (mg/kg/dia)
    - Alerta de Segurança (Alergias/Alternativas)
    """
    
    # ... (resto da lógica de auditoria e retorno ANVISA)
    return prontuario_auditado, link_bula
