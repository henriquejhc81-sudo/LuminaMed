import streamlit as st
from motor_dados import carregar_banco_medicamentos, buscar_apresentacoes
from robo_ia import listar_opcoes_tratamento, gerar_prontuario_final

st.set_page_config(page_title="Lumina Med", page_icon="⚕️", layout="centered")

# --- COLOQUE SUAS CHAVES DE API AQUI DENTRO DAS ASPAS ---
CHAVES_API = {
    'groq': 'SUA_CHAVE_GROQ_AQUI',
    'openrouter': 'SUA_CHAVE_OPENROUTER_AQUI'
}
# --------------------------------------------------------

st.title("⚕️ Lumina Med")
st.subheader("Terminal Clínico CDSS Advanced")

# Controle do Funil
if 'etapa' not in st.session_state: st.session_state.etapa = 1
if 'opcoes_estoque' not in st.session_state: st.session_state.opcoes_estoque = []
if 'dados_paciente' not in st.session_state: st.session_state.dados_paciente = {}
if 'escolha_final' not in st.session_state: st.session_state.escolha_final = ""

# MOTOR DE DADOS BLINDADO (Sem dar tela vermelha!)
banco_csv = carregar_banco_medicamentos()
if "ERRO" in banco_csv:
    st.error(f"⚠️ Erro ao ler a planilha: {banco_csv['ERRO']['FALHA_LEITURA'][0]}")
    st.stop()

# --- ETAPA 1 ---
if st.session_state.etapa == 1:
    st.markdown("### ETAPA 1: Triagem e Biometria")
    with st.form("form_triagem"):
        sintomas = st.text_area("Quadro Clínico OU Nome do medicamento:")
        col1, col2 = st.columns(2)
        uso_continuo = col1.text_input("Uso contínuo (ex: Losartana):")
        alergias = col2.text_input("Alergias (ex: Penicilina):")
        
        c1, c2, c3, c4 = st.columns(4)
        idade = c1.number_input("Idade:", value=30)
        peso = c2.number_input("Peso (kg):", value=70.0)
        sexo = c3.selectbox("Sexo Biológico:", ["Masculino", "Feminino"])
        creatinina = c4.number_input("Creatinina (opcional):", value=0.0)
        
        if st.form_submit_button("Analisar e Buscar"):
            if not sintomas:
                st.warning("Descreva o quadro clínico ou o remédio.")
            else:
                with st.spinner("Analisando e cruzando com a planilha..."):
                    st.session_state.dados_paciente = {
                        "Sintomas": sintomas, "Alergias": alergias, "Uso Contínuo": uso_continuo,
                        "Idade": idade, "Peso": peso, "Sexo": sexo, "Creatinina": creatinina
                    }
                    
                    sugestoes_ia = listar_opcoes_tratamento(sintomas, alergias, uso_continuo, CHAVES_API)
                    
                    opcoes_encontradas = []
                    for principio_sugerido in sugestoes_ia:
                        encontrados = buscar_apresentacoes(principio_sugerido, banco_csv)
                        opcoes_encontradas.extend(encontrados)
                    
                    if opcoes_encontradas:
                        st.session_state.opcoes_estoque = list(set(opcoes_encontradas))
                        st.session_state.etapa = 2
                        st.rerun()
                    else:
                        st.warning(f"A IA sugeriu: {sugestoes_ia}, mas NENHUMA apresentação foi encontrada na sua planilha medicamentos.csv.")

# --- ETAPA 2 ---
elif st.session_state.etapa == 2:
    st.markdown("### ETAPA 2: Escolha a Apresentação")
    st.info("Opções encontradas no seu estoque:")
    
    escolha = st.radio("Selecione para gerar dosagem exata:", st.session_state.opcoes_estoque)
    
    col1, col2 = st.columns(2)
    if col1.button("Gerar Prontuário Seguro"):
        st.session_state.escolha_final = escolha
        st.session_state.etapa = 3
        st.rerun()
    if col2.button("Voltar"):
        st.session_state.etapa = 1
        st.rerun()

# --- ETAPA 3 ---
elif st.session_state.etapa == 3:
    st.markdown("### ETAPA 3: Auditoria Final e Veredito")
    with st.spinner("Gerando laudo seguro e link da Anvisa..."):
        prontuario = gerar_prontuario_final(
            st.session_state.escolha_final, 
            st.session_state.dados_paciente, 
            CHAVES_API
        )
        st.success("Prontuário Validado com Sucesso!")
        st.markdown(prontuario)
        
    if st.button("Nova Consulta"):
        st.session_state.etapa = 1
        st.session_state.opcoes_estoque = []
        st.rerun()
