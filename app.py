import streamlit as st
from robo_ia import analisar_consenso_autonomo

# 1. CONFIGURAÇÃO VISUAL DA INTERFACE
st.set_page_config(page_title="Lumina Med - Autônomo", page_icon="⚕️", layout="centered")

st.title("⚕️ Lumina Med - V7 DoctorBot Autônomo")
st.subheader("Sistema Inteligente de Suporte à Prescrição")
st.markdown("---")

# 2. RECUPERAÇÃO DAS CHAVES DO COFRE DE SEGURANÇA
chaves_api = {
    "openai": st.secrets.get("OPENAI_KEY", ""),
    "gemini": st.secrets.get("GEMINI_KEY", ""),
    "groq": st.secrets.get("GROQ_KEY", ""),
    "openrouter": st.secrets.get("OPENROUTER_KEY", "")
}

# 3. FUNÇÃO DE LIMPEZA PROFUNDA DA MEMÓRIA
def limpar_consulta():
    st.session_state.clear()

# 4. FORMULÁRIO CENTRALIZADO
with st.form("form_paciente"):
    st.write("📋 **Dados do Paciente**")
    
    # Vinculamos as entradas diretamente à "chave" (key) da memória do Streamlit
    sintomas_input = st.text_area(
        "Descreva o quadro do paciente de forma natural:", 
        placeholder="Ex: dor e febre e ancia de vomito",
        key="sintomas_chave"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        # value=None permite que o campo inicie perfeitamente vazio
        idade_input = st.number_input("Idade (anos):", min_value=0, max_value=120, value=None, step=1, placeholder="Digite a idade", key="idade_chave")
    with col2:
        peso_input = st.number_input("Peso (kg):", min_value=0.0, max_value=200.0, value=None, step=0.5, placeholder="Digite o peso", key="peso_chave")
        
    submit_button = st.form_submit_button("Consultar DoctorBot")

# 5. PROCESSAMENTO AUTÔNOMO PELO ENXAME DE IAs
if submit_button:
    if not sintomas_input:
        st.warning("Por favor, descreva o quadro do paciente na caixa de texto.")
    elif idade_input is None or peso_input is None:
        st.error("⚠️ Operação bloqueada: A idade e o peso são campos obrigatórios e não podem estar vazios.")
    else:
        with st.spinner("🧠 DoctorBot Autônomo operando. Calculando posologia em tempo real através da junta de IAs..."):
            analise_das_ias = analisar_consenso_autonomo(sintomas_input, idade_input, peso_input, chaves_api)
            
            if not analise_das_ias:
                st.error("Nenhuma Inteligência Artificial conseguiu processar a requisição no momento. Verifique suas chaves de API.")
            else:
                st.success("✅ Diagnóstico autônomo e cálculos posológicos concluídos!")
                
                # Exibe a resposta independente de cada IA como se fossem médicos consultores
                for nome_ia, resposta in analise_das_ias:
                    with st.expander(f"🤖 Parecer Analítico: Dr. {nome_ia}", expanded=True):
                        st.markdown(resposta)

# 6. MECANISMO DE RESET (CHAMA A FUNÇÃO DE LIMPEZA PROFUNDA)
st.markdown("---")
st.button("🔄 Nova Consulta", on_click=limpar_consulta)
