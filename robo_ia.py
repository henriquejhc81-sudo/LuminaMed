import json

# BASE DE DADOS ESTRUTURADA (O CÉREBRO)
AINEs = {
    "Ácido Salicílico": ["Aspirina (AAS)"],
    "Ácido Propiônico": ["Ibuprofeno", "Naproxeno", "Cetoprofeno"],
    "Ácido Acético": ["Diclofenaco Sódico", "Diclofenaco Potássico", "Cetorolaco"],
    "Oxicam": ["Piroxicam", "Tenoxicam", "Meloxicam"],
    "Fenamatos": ["Ácido Mefenâmico"],
    "Coxibes": ["Celecoxibe", "Etoricoxibe"]
}

CORTICOIDES = {
    "Cortisona": {"potencia": 0.8, "duracao": "Curta", "dose_eq": 25, "retencao": "Alta"},
    "Hidrocortisona": {"potencia": 1.0, "duracao": "Curta", "dose_eq": 20, "retencao": "Alta"},
    "Prednisona": {"potencia": 4.5, "duracao": "Intermediária", "dose_eq": 5, "retencao": "Baixa"},
    "Prednisolona": {"potencia": 4.5, "duracao": "Intermediária", "dose_eq": 5, "retencao": "Baixa"},
    "Metilprednisolona": {"potencia": 6.0, "duracao": "Intermediária", "dose_eq": 4, "retencao": "Nula"},
    "Dexametasona": {"potencia": 27.5, "duracao": "Longa", "dose_eq": 0.75, "retencao": "Nula"},
    "Betametasona": {"potencia": 27.5, "duracao": "Longa", "dose_eq": 0.6, "retencao": "Nula"}
}

def listar_opcoes_tratamento(sintomas, alergias, chaves_api):
    # Prompt focado em usar nossas classes reais
    prompt = f"""
    Sintomas: {sintomas}. Alergias: {alergias}.
    Com base nestas categorias de medicamentos: {list(AINEs.keys())} e estas de Corticoides: {list(CORTICOIDES.keys())},
    selecione 4 opções de princípios ativos altamente eficazes para esse quadro.
    Responda apenas em JSON: {{"opcoes": ["Principio1", "Principio2", "Principio3", "Principio4"]}}
    """
    # ... (restante da lógica de chamada de API igual à anterior)
    
def gerar_prontuario_final(principio, sintomas, idade, peso, alergias, chaves_api):
    # Se o principio escolhido for um corticoide, injetamos nossa tabela na análise
    info_adicional = ""
    if principio in CORTICOIDES:
        dados = CORTICOIDES[principio]
        info_adicional = f"\nDETALHES TÉCNICOS: Potência Relativa {dados['potencia']}x | Dose Equivalente: {dados['dose_eq']}mg | Retenção Salina: {dados['retencao']}."

    prompt = f"""
    Prescrição: {principio}. 
    Paciente: {idade} anos, {peso}kg. 
    {info_adicional}
    Gere a prescrição médica detalhada, incluindo posologia para o peso e contraindicações.
    """
    # ... (chamada de IA)
