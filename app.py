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

# 1. A CORREÇÃO ESTÁ AQUI: Desempacotando a tupla (banco e df) para o Pandas não dar erro
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
        sintomas = st.text_area("Quadro Clínico (Sintomas detalhados):", placeholder="Ex: Febre alta, tosse seca...")
        
        col1, col2 = st.columns(2)
        uso_continuo = col1.text_input("Uso contínuo:", placeholder="Ex: Losartana")
        alergias = col2.text_input("Alergias:", placeholder="Ex: Penicilina")
        
        c1, c2, c3 = st.columns(3)
        idade = c1.number_input("Idade:", min_value=0, max_value=120, value=None, placeholder="Ex: 30")
        peso = c2.number_input("Peso (kg):", min_value=1.0, max_value=250.0, value=None, placeholder="Ex: 70.0")
        sexo = c3.selectbox("Sexo:", ["Masculino", "Feminino", "Outro"], index=None, placeholder="Selecione")
        
        if st.form_submit_button("Processar Triagem"):
            if not sintomas or idade is None or peso is None or sexo is None:
                st.warning("⚠️ Preencha os Sintomas, Idade, Peso e Sexo para prosseguir.")
            else:
                st.session_state.dados_paciente = {
                    "Sintomas": sintomas, "Alergias": alergias, "Uso": uso_continuo,
                    "Idade": idade, "Peso": peso, "Sexo": sexo
                }
                
                with st.status("🧠 Cruzando biometria com Inteligência Artificial...", expanded=True) as status:
                    st.write("Consultando diagnóstico e interações na IA...")
                    sugestoes_ia = listar_opcoes_tratamento(sintomas, alergias, uso_continuo, CHAVES_API)
                    
                    if not sugestoes_ia or "Erro" in sugestoes_ia[0] or "Falha" in sugestoes_ia[0]:
                        status.update(label="Falha de Comunicação", state="error", expanded=False)
                        st.error(sugestoes_ia[0] if sugestoes_ia else "Erro desconhecido na API.")
                        st.stop()

                    st.info(f"💡 A IA sugeriu: {', '.join(sugestoes_ia)}")
                    st.write("Buscando apresentações no estoque e cruzando códigos ATC...")
                    
                    opcoes_encontradas = []
                    bloqueios = []
                    
                    # 2. INTEGRAÇÃO DA REGRA DE NEGÓCIO ATC
                    for principio in sugestoes_ia:
                        seguro, msg_alerta = auditar_alergia_cruzada(principio, alergias, banco_dados)
                        
                        if seguro:
                            encontrados = buscar_apresentacoes(principio, banco_dados)
                            opcoes_encontradas.extend(encontrados)
                        else:
                            bloqueios.append(msg_alerta)
                    
                    st.session_state.alertas_bloqueio = bloqueios
                    
                    if opcoes_encontradas:
                        st.session_state.opcoes_estoque = list(set(opcoes_encontradas))
                        st.session_state.etapa = 2
                        status.update(label="Análise Concluída!", state="complete", expanded=False)
                        st.rerun()
                    else:
                        status.update(label="Falha no Cruzamento", state="error", expanded=False)
                        if bloqueios:
                            st.error("Medicamentos foram bloqueados por risco de alergia cruzada!")
                        st.warning("Nenhum medicamento seguro foi encontrado na planilha para esta indicação.")

# --- ETAPA 2 ---
elif st.session_state.etapa == 2:
    st.markdown("### ETAPA 2: Validação Farmacêutica")
    
    # Exibe os bloqueios da auditoria ATC, se houver
    if st.session_state.alertas_bloqueio:
        for bloqueio in st.session_state.alertas_bloqueio:
            st.error(bloqueio)
            
    st.info("Bases ativas aprovadas e compatíveis com o quadro:")
    
    escolha = st.radio("Selecione o Princípio Ativo para prescrição:", st.session_state.opcoes_estoque)
    
    col_a, col_b = st.columns(2)
    if col_a.button("Gerar Prontuário"):
        st.session_state.escolha_final = escolha
        st.session_state.etapa = 3
        st.rerun()
    if col_b.button("Voltar / Editar"):
        st.session_state.etapa = 1
        st.rerun()

# --- ETAPA 3 ---
elif st.session_state.etapa == 3:
    st.markdown("### ETAPA 3: Laudo CDSS Final")
    with st.spinner("Compilando dados matemáticos e interações..."):
        prontuario = gerar_prontuario_final(
            st.session_state.escolha_final, 
            st.session_state.dados_paciente, 
            CHAVES_API
        )
        st.success("✅ Protocolo Clínico Gerado.")
        st.markdown(prontuario)
        
    st.markdown("---")
    st.button("🔄 Iniciar Nova Triagem", on_click=resetar_consulta)
