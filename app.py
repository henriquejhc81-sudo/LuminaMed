import os
import streamlit as st
from motor_dados import carregar_banco_medicamentos, buscar_apresentacoes, auditar_alergia_cruzada, listar_proibidos_por_familia, buscar_alternativas_seguras
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

CHAVES_API = {
    'groq': st.secrets.get("GROQ_API_KEY", ""),
    'openrouter': st.secrets.get("OPENROUTER_API_KEY", ""),
    'openai': st.secrets.get("OPENAI_API_KEY", ""),
    'gemini': st.secrets.get("GEMINI_API_KEY", "")
}

st.title("⚕️ Lumina Med")
st.subheader("Terminal Clínico CDSS Advanced")

banco_dados, df_completo = carregar_banco_medicamentos()

if banco_dados and "ERRO" in banco_dados:
    st.error(f"⚠️ {banco_dados['ERRO']}")
    st.stop()

if 'etapa' not in st.session_state: st.session_state.etapa = 1
if 'opcoes_estoque' not in st.session_state: st.session_state.opcoes_estoque = []
if 'dados_paciente' not in st.session_state: st.session_state.dados_paciente = {}
if 'escolha_final' not in st.session_state: st.session_state.escolha_final = ""
if 'bloqueios_detalhados' not in st.session_state: st.session_state.bloqueios_detalhados = []

def resetar_consulta():
    st.session_state.etapa = 1
    st.session_state.opcoes_estoque = []
    st.session_state.dados_paciente = {}
    st.session_state.bloqueios_detalhados = []

# --- ETAPA 1 ---
if st.session_state.etapa == 1:
    st.markdown("### ETAPA 1: Triagem e Biometria")
    with st.form("form_triagem"):
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
                    bloqueios_temp = []
                    
                    st.write("Verificando se é uma busca direta de medicamento...")
                    busca_direta = buscar_apresentacoes(sintomas, banco_dados)
                    
                    if busca_direta:
                        st.info(f"🔍 Busca Direta ativada para: {sintomas}")
                        opcoes_pre_aprovadas = busca_direta 
                    else:
                        st.write("Consultando diagnóstico e interações na IA...")
                        sugestoes_ia = listar_opcoes_tratamento(sintomas, alergias, uso_continuo, CHAVES_API)
                        
                        if not sugestoes_ia or "Erro" in sugestoes_ia[0] or "Falha" in sugestoes_ia[0]:
                            status.update(label="Falha de Comunicação", state="error", expanded=False)
                            st.error(sugestoes_ia[0] if sugestoes_ia else "Erro na API.")
                            st.stop()

                        st.info(f"💡 A IA sugeriu: {', '.join(sugestoes_ia)}")
                        st.write("Buscando apresentações no estoque...")
                        
                        opcoes_pre_aprovadas = []
                        for principio in sugestoes_ia:
                            opcoes_pre_aprovadas.extend(buscar_apresentacoes(principio, banco_dados))
                    
                    st.write("Aplicando Firewall ATC de Alergias...")
                    
                    for opcao_bruta in opcoes_pre_aprovadas:
                        nome_limpo = str(opcao_bruta).split(" | ")[0].strip() if " | " in str(opcao_bruta) else str(opcao_bruta)
                        seguro, msg_alerta, atc_bloq, classe_bloq, sintomas_bloq = auditar_alergia_cruzada(nome_limpo, alergias, banco_dados)
                        
                        if seguro:
                            opcoes_encontradas.append(opcao_bruta)
                        else:
                            bloqueio_info = {"msg": msg_alerta, "atc": atc_bloq, "classe": classe_bloq, "sintomas": sintomas_bloq}
                            if bloqueio_info not in bloqueios_temp:
                                bloqueios_temp.append(bloqueio_info)
                    
                    st.session_state.bloqueios_detalhados = bloqueios_temp
                    
                    # SE TUDO FOI BLOQUEADO (EX: O caso do Tenoxicam com alergia a Meloxicam)
                    if not opcoes_encontradas and bloqueios_temp:
                        st.write("🔄 Buscando alternativas seguras de outras classes terapêuticas...")
                        alternativas_gerais = []
                        for b in bloqueios_temp:
                            alts = buscar_alternativas_seguras(b['sintomas'], b['atc'], banco_dados)
                            alternativas_gerais.extend(alts)
                            
                        if alternativas_gerais:
                            st.session_state.opcoes_estoque = list(set(alternativas_gerais))
                            st.session_state.etapa = 2
                            status.update(label="Bloqueio ATC: Substituição Terapêutica Ativada!", state="complete", expanded=False)
                            st.rerun()
                        else:
                            status.update(label="Falha Crítica", state="error", expanded=False)
                            st.error("🛑 Medicamentos bloqueados e não há alternativas na base para os mesmos sintomas.")
                            st.stop()
                    
                    # SE PASSOU DIRETO (SEM ALERGIAS GRAVES)
                    elif opcoes_encontradas:
                        st.session_state.opcoes_estoque = list(set(opcoes_encontradas))
                        st.session_state.etapa = 2
                        status.update(label="Análise Concluída!", state="complete", expanded=False)
                        st.rerun()
                    
                    else:
                        status.update(label="Falha no Cruzamento", state="error", expanded=False)
                        st.warning("Nenhum medicamento correspondente foi encontrado no estoque para esta requisição.")

# --- ETAPA 2 ---
elif st.session_state.etapa == 2:
    st.markdown("### ETAPA 2: Validação Farmacêutica")
    
    # Exibe os bloqueios detalhados e as alternativas
    if st.session_state.get('bloqueios_detalhados'):
        st.error("🛑 **ALERTA DE SEGURANÇA: RISCO CLÍNICO DETECTADO**")
        
        for b in st.session_state.bloqueios_detalhados:
            st.warning(b['msg'])
            # Expansor com TODOS os remédios da família do paciente
            with st.expander(f"🚫 Ver TODOS os medicamentos da classe proibida ({b['classe']})"):
                proibidos = listar_proibidos_por_familia(b['atc'], banco_dados)
                if proibidos:
                    st.write("**Lista de compostos bloqueados no estoque:** " + ", ".join(proibidos))
                else:
                    st.write("Nenhum outro medicamento desta classe no estoque.")
                    
        st.success("✅ O sistema localizou automaticamente as seguintes Alternativas Seguras (De outras famílias químicas):")
    else:
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
        
        nome_puro = st.session_state.escolha_final.split(" | ")[0].strip()
        
        try:
            apresentacoes_em_estoque = banco_dados[nome_puro]['Apresentacoes']
            tarja_original = banco_dados[nome_puro]['Tarja']
        except KeyError:
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
