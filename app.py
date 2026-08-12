import os
import streamlit as st
from motor_dados import carregar_banco_medicamentos, buscar_apresentacoes, auditar_alergia_cruzada
from robo_ia import listar_opcoes_tratamento, gerar_prontuario_final

st.set_page_config(page_title="Lumina Med | CDSS", page_icon="⚕️", layout="centered")

st.markdown("""
<style>
    div.stButton > button {
        background-color: transparent;
        color: #00ff99;
        border: 1px solid #00ff99;
        border-radius: 4px;
        font-weight: bold;
        transition: all 0.3s ease-in-out;
        width: 100%;
    }
    div.stButton > button:hover {
        background-color: #00ff99;
        color: #0e1117;
        box-shadow: 0 0 15px #00ff99;
    }
</style>
""", unsafe_allow_html=True)

# Gerenciador de Segredos Direto do Streamlit Cloud
CHAVES_API = {
    'groq': st.secrets.get("GROQ_API_KEY", ""),
    'openrouter': st.secrets.get("OPENROUTER_API_KEY", ""),
    'openai': st.secrets.get("OPENAI_API_KEY", ""),
    'gemini': st.secrets.get("GEMINI_API_KEY", "")
}

st.title("⚕️ Lumina Med")
st.subheader("Terminal Clínico CDSS Advanced")

# 1. CARREGAMENTO DOS DADOS - Resolvido o erro da Tela Vermelha!
banco_dados, df_completo = carregar_banco_medicamentos()

if banco_dados and "ERRO" in banco_dados:
    st.error(f"⚠️ {banco_dados['ERRO']}")
    st.stop()

# Controle de Estado da Sessão
if 'etapa' not in st.session_state: st.session_state.etapa = 1
if 'opcoes_estoque' not in st.session_state: st.session_state.opcoes_estoque = []
if 'dados_paciente' not in st.session_state: st.session_state.dados_paciente = {}
if 'escolha_final' not in st.session_state: st.session_state.escolha_final = ""
if 'alertas_bloqueio' not in st.session_state: st.session_state.alertas_bloqueio = []

def resetar_consulta():
    st.session_state.etapa = 1
    st.session_state.opcoes_estoque = []
    st.session_state.dados_paciente = {}
    st.session_state.alertas_bloqueio = []

# --- ETAPA 1 ---
if st.session_state.etapa == 1:
    st.markdown("### ETAPA 1: Triagem e Biometria")
    with st.form("form_triagem"):
        # NOVA LÓGICA: O usuário pode digitar um Sintoma OU um Medicamento
        sintomas = st.text_area("Quadro Clínico OU Nome do Princípio Ativo:", placeholder="Ex: Febre alta, tosse seca... OU Amoxicilina, Dipirona...")
        
        col1, col2 = st.columns(2)
        uso_continuo = col1.text_input("Uso contínuo:", placeholder="Ex: Losartana")
        alergias = col2.text_input("Alergias:", placeholder="Ex: Penicilina")
        
        c1, c2, c3 = st.columns(3)
        idade = c1.number_input("Idade:", min_value=0, max_value=120, value=None, placeholder="Ex: 30")
        peso = c2.number_input("Peso (kg):", min_value=1.0, max_value=250.0, value=None, placeholder="Ex: 70.0")
        sexo = c3.selectbox("Sexo:", ["Masculino", "Feminino", "Outro"], index=None, placeholder="Selecione")
        
        if st.form_submit_button("Processar Triagem / Buscar Medicamento"):
            if not sintomas or idade is None or peso is None or sexo is None:
                st.warning("⚠️ Preencha o Quadro Clínico/Medicamento, Idade, Peso e Sexo para prosseguir.")
            else:
                st.session_state.dados_paciente = {
                    "Sintomas_ou_Medicamento": sintomas, "Alergias": alergias, "Uso": uso_continuo,
                    "Idade": idade, "Peso": peso, "Sexo": sexo
                }
                
                with st.status("🧠 Analisando requisição...", expanded=True) as status:
                    opcoes_encontradas = []
                    bloqueios = []
                    
                    # PASSO A: Tenta buscar direto no banco (se o usuário digitou "Amoxicilina")
                    st.write("Verificando se é uma busca direta de medicamento...")
                    busca_direta = buscar_apresentacoes(sintomas, banco_dados)
                    
                    # Se achou algo no banco que bate com a palavra (Ex: Amoxicilina), pula a IA
                    if busca_direta:
                        st.info(f"🔍 Busca Direta ativada! Encontramos compostos para: {sintomas}")
                        sugestoes_analise = [sintomas.strip().upper()] # Força a análise de alergia na palavra buscada
                        opcoes_pre_aprovadas = busca_direta 
                    
                    # PASSO B: Se não achou medicamento exato, chama a IA para diagnosticar o sintoma
                    else:
                        st.write("Consultando diagnóstico e interações na IA...")
                        sugestoes_ia = listar_opcoes_tratamento(sintomas, alergias, uso_continuo, CHAVES_API)
                        
                        if not sugestoes_ia or "Erro" in sugestoes_ia[0] or "Falha" in sugestoes_ia[0]:
                            status.update(label="Falha de Comunicação", state="error", expanded=False)
                            st.error(sugestoes_ia[0] if sugestoes_ia else "Erro desconhecido na API.")
                            st.stop()

                        st.info(f"💡 A IA sugeriu: {', '.join(sugestoes_ia)}")
                        st.write("Buscando apresentações no estoque...")
                        
                        sugestoes_analise = sugestoes_ia
                        opcoes_pre_aprovadas = []
                        for principio in sugestoes_ia:
                            opcoes_pre_aprovadas.extend(buscar_apresentacoes(principio, banco_dados))
                    
                    # PASSO C: Auditoria ATC de Alergias (Acontece nos 2 casos!)
                    st.write("Aplicando Firewall ATC de Alergias...")
                    # Varre tudo que foi encontrado para ver se tem risco de alergia cruzada
                    for opcao_bruta in opcoes_pre_aprovadas:
                        # Extrai o nome limpo (Remove a cor da tarja se tiver)
                        nome_limpo = str(opcao_bruta).split(" | ")[0].strip() if " | " in str(opcao_bruta) else str(opcao_bruta)
                        
                        seguro, msg_alerta = auditar_alergia_cruzada(nome_limpo, alergias, banco_dados)
                        
                        if seguro:
                            opcoes_encontradas.append(opcao_bruta)
                        else:
                            if msg_alerta not in bloqueios:
                                bloqueios.append(msg_alerta)
                    
                    st.session_state.alertas_bloqueio = bloqueios
                    
                    if opcoes_encontradas:
                        # Limpa duplicatas
                        st.session_state.opcoes_estoque = list(set(opcoes_encontradas))
                        st.session_state.etapa = 2
                        status.update(label="Análise Concluída!", state="complete", expanded=False)
                        st.rerun()
                    else:
                        status.update(label="Falha no Cruzamento / Bloqueio", state="error", expanded=False)
                        if bloqueios:
                            st.error("Medicamentos foram bloqueados pelo Firewall por risco de alergia cruzada!")
                        st.warning("Nenhum medicamento seguro ou correspondente foi encontrado no estoque para esta requisição.")

# --- ETAPA 2 ---
elif st.session_state.etapa == 2:
    st.markdown("### ETAPA 2: Validação Farmacêutica")
    
    # Exibe os bloqueios da auditoria ATC, se houver
    if st.session_state.alertas_bloqueio:
        st.error("🚨 O Firewall bloqueou algumas opções devido ao histórico de alergias!")
        for bloqueio in st.session_state.alertas_bloqueio:
            st.warning(bloqueio)
            
    st.info("Apresentações ativas aprovadas e compatíveis no seu estoque:")
    
    escolha = st.radio("Selecione a Apresentação para prescrição matemática:", st.session_state.opcoes_estoque)
    
    col_a, col_b = st.columns(2)
    if col_a.button("Gerar Prontuário Posológico"):
        st.session_state.escolha_final = escolha
        st.session_state.etapa = 3
        st.rerun()
    if col_b.button("Voltar / Editar"):
        st.session_state.etapa = 1
        st.rerun()

# --- ETAPA 3 ---
elif st.session_state.etapa == 3:
    st.markdown("### ETAPA 3: Laudo CDSS Final")
    with st.spinner("Calculando posologia exata com base no inventário da farmácia..."):
        
        # O sistema agora corta a Tarja para isolar o nome da Substância e buscar as apresentações reais
        nome_puro = st.session_state.escolha_final.split(" | ")[0].strip()
        
        try:
            apresentacoes_em_estoque = banco_dados[nome_puro]['Apresentacoes']
            tarja_original = banco_dados[nome_puro]['Tarja']
        except KeyError:
             # Fallback de segurança se o nome da substância for complexo (Ex: Amoxicilina + Clavulanato)
             apresentacoes_em_estoque = ["Apresentação genérica (Consulte o farmacêutico)"]
             tarja_original = "Tarja sob Avaliação"

        prontuario = gerar_prontuario_final(
            nome_puro, 
            apresentacoes_em_estoque,
            tarja_original,
            st.session_state.dados_paciente, 
            CHAVES_API
        )
        st.success("✅ Protocolo Clínico Gerado com Sucesso.")
        st.markdown(prontuario)
        
    st.markdown("---")
    st.button("🔄 Iniciar Nova Triagem", on_click=resetar_consulta)
