import csv

def calcular_dosagem():
    print("\n" + "="*70)
    print(" L U M I N A   M E D  -  Motor Clínico Avançado v4")
    print("="*70)
    
    # 1. Coleta Inteligente Inicial
    sintomas_input = input("\nQuais os sintomas do paciente? (ex: dor, febre): ").lower()
    
    try:
        idade_paciente = float(input("Qual a idade do paciente (em anos)? "))
    except ValueError:
        print("\n❌ Idade inválida. Operação cancelada.")
        return

    palavras_usuario = set(sintomas_input.replace(',', ' ').replace(' e ', ' ').split())
    medicamentos_encontrados = []
    
    # 2. Busca e Cruzamento de Dados
    with open('medicamentos.csv', mode='r', encoding='utf-8') as arquivo:
        leitor = csv.DictReader(arquivo)
        for linha in leitor:
            palavras_chave_db = set(linha['sintomas_chave'].lower().split())
            
            if palavras_usuario.intersection(palavras_chave_db):
                if idade_paciente >= float(linha['idade_minima']):
                    medicamentos_encontrados.append(linha)
                
    if not medicamentos_encontrados:
        print("\n❌ Nenhum tratamento localizado para esses sintomas ou faixa etária.\n")
        return 

    # 3. Menu de Escolha
    print(f"\nEncontramos {len(medicamentos_encontrados)} opção(ões) de tratamento adequadas:")
    for indice, remedio in enumerate(medicamentos_encontrados):
        print(f"[{indice + 1}] {remedio['principio_ativo']} (Classe: {remedio['classe_farmacologica']})")
        
    try:
        escolha_usuario = int(input("\nDigite o número do princípio ativo desejado: ")) - 1
        if escolha_usuario < 0 or escolha_usuario >= len(medicamentos_encontrados):
            print("\n❌ Número inválido.\n")
            return
        med = medicamentos_encontrados[escolha_usuario]
    except ValueError:
        print("\n❌ Digite apenas números.\n")
        return

    # 4. Lógica de Bifurcação: Adulto vs Pediátrico
    idade_adulta = float(med['idade_adulta'])
    freq_horas = int(med['frequencia_horas'])
    limite_max = float(med['limite_maximo_diario_mg'])
    
    dose_por_vez = 0
    dose_diaria_total = 0
    ajustado_pelo_teto = False
    tipo_dose = ""

    if idade_paciente >= idade_adulta:
        # Lógica Adulta (Dose Fixa)
        tipo_dose = "Dose Fixa Adulto"
        dose_por_vez = float(med['dose_adulta_mg'])
        dose_diaria_total = dose_por_vez * (24 / freq_horas)
        
    else:
        # Lógica Pediátrica (Baseada no Peso)
        tipo_dose = "Dose Pediátrica (Baseada no Peso)"
        try:
            peso_texto = input(f"\nPaciente pediátrico. Qual o peso em KG? (ex: 15.5): ").replace(',', '.')
            peso_paciente = float(peso_texto)
        except ValueError:
            print("\n❌ Peso inválido.\n")
            return
            
        dose_mg_kg = float(med['dosagem_mg_kg'])
        dose_diaria_total = dose_mg_kg * peso_paciente
        
        # Trava de Segurança
        if dose_diaria_total > limite_max:
            dose_diaria_total = limite_max
            ajustado_pelo_teto = True
            
        doses_por_dia = 24 / freq_horas
        dose_por_vez = dose_diaria_total / doses_por_dia

    # 5. Exibição do Prontuário Inteligente
    print("\n" + "="*70)
    print(" 📋 PRESCRIÇÃO E INFORMAÇÕES CLÍNICAS")
    print("="*70)
    print(f"🔹 Princípio Ativo: {med['principio_ativo']}")
    print(f"🔹 Classe Farmacológica: {med['classe_farmacologica']}")
    print(f"🔹 Protocolo Utilizado: {tipo_dose}")
    print("-" * 70)
    print(f"💊 POSOLOGIA:")
    print(f"   Dar {dose_por_vez:.2f} mg a cada {freq_horas} horas.")
    if ajustado_pelo_teto:
        print(f"   (⚠️ Ajustado pelo teto máximo de segurança diário de {limite_max}mg)")
    print("-" * 70)
    print(f"⚠️ AVISOS DE ALERGIA E RESTRIÇÕES:")
    print(f"   {med['avisos_alergia']}")
    print(f"   Similares no mesmo grupo a evitar: {med['similares']}")
    print("="*70 + "\n")

if __name__ == "__main__":
    calcular_dosagem()