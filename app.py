import streamlit as st
import pandas as pd
from motor_clinico import carregar_dados
from robo_ia import diagnosticar_principio_ativo

st.set_page_config(page_title="Lumina Med - Híbrido", page_icon="⚕️", layout="centered")
st.title("⚕️ Lumina Med - V8 Híbrido")
st.subheader("Inteligência Artificial + Segurança Matemática")
st.markdown("---")

df_medicamentos = carregar_dados()

chaves_api = {
    "openai": st.secrets.get("OPENAI_KEY", ""),
    "gemini": st.secrets.get("GEMINI_KEY", ""),
    "groq": st.secrets.get("GROQ_KEY", "")
}

def limpar_consulta():
    st.session_state.clear()

with st.form("form_paciente"):
    st.write("📋 **Dados do Paciente**")
    sintomas_input = st.text_area("Descreva o quadro do paciente de forma natural:", placeholder="Ex: vomito e dor de cabeça forte", key="sintomas_chave")
    
    col1, col2 = st.columns(2)
    with col1:
        idade_input = st.number_input("Idade (anos):", min_value=0, max_value=120, value=None, step=1, key="idade_chave")
    with col2:
        peso_input = st.number_input("Peso (kg):", min_value=0.0, max_value=200.0, value=None, step=0.5, key="peso_chave")
        
    submit_button = st.form_submit_button("Consultar DoctorBot")

if submit_button:
    if not sintomas_input or idade_input is None or peso_input is None:
        st.error("⚠️ Preencha os sintomas, idade e peso para prosseguir.")
    else:
        with st.spinner("🧠 IA interpretando sintomas e buscando princípios ativos..."):
            # PASSO 1: A IA descobre o princípio ativo
            principios_ia = diagnosticar_principio_ativo(sintomas_input, chaves_api)
            
            if not principios_ia:
                st.error("Falha na comunicação com a IA. Verifique se as chaves em 'Settings > Secrets' estão corretas e sem espaços extras.")
            else:
                st.info(f"💡 A IA identificou necessidade dos seguintes ativos: **{', '.join(principios_ia).title()}**")
                st.write("⚙️ *Cruzando com a base de segurança local...*")
                
                # PASSO 2: O sistema local faz a matemática segura
                encontrou_tratamento = False
                for index, row in df_medicamentos.iterrows():
                    principio_banco = str(row.get('principio_ativo', '')).lower()
                    
                    # Verifica se algum remédio da IA bate com o nosso CSV
                    if any(p_ia in principio_banco for p_ia in principios_ia):
                        if idade_input >= float(row.get('idade_minima', 0)):
                            encontrou_tratamento = True
                            
                            with st.expander(f"💊 {row['principio_ativo'].title()} (Classe: {row['classe_farmacologica']})", expanded=True):
                                
                                # Cálculo de Posologia
                                idade_adulta = float(row.get('idade_adulta', 12))
                                freq = int(row.get('frequencia_horas', 8))
                                lim_max = float(row.get('limite_maximo_diario_mg', 1000))
                                dose_final_mg = 0
                                
                                if idade_input < idade_adulta:
                                    dose_diaria = float(row.get('dosagem_mg_kg', 0)) * peso_input
                                    if dose_diaria > lim_max: dose_diaria = lim_max
                                    dose_final_mg = dose_diaria / (24 / freq)
                                    st.write(f"**Uso Pediátrico:** {dose_final_mg:.1f}mg a cada {freq} horas.")
                                else:
                                    dose_final_mg = float(row.get('dose_adulta_mg', 0))
                                    st.write(f"**Uso Adulto:** {dose_final_mg:.1f}mg a cada {freq} horas.")
                                    
                                # Conversão Gotas/ML
                                concentracao = float(row.get('concentracao_mg_por_unidade', 1))
                                tipo = str(row.get('tipo_apresentacao', 'comprimido')).lower()
                                qtd = dose_final_mg / concentracao if concentracao > 0 else 0
                                
                                if tipo == 'gotas':
                                    st.success(f"💧 **Como administrar:** Dar {int(qtd)} gota(s).")
                                elif tipo in ['ml', 'xarope', 'suspensao']:
                                    st.success(f"🥄 **Como administrar:** Dar {qtd:.1f} ml.")
                                else:
                                    st.success(f"💊 **Como administrar:** Tomar {qtd:.1f} unidade(s).")
                                    
                                st.warning(f"⚠️ **Alergias/Avisos:** {row.get('avisos_alergia', '')}")
                                
                if not encontrou_tratamento:
                    st.warning("A IA sugeriu princípios ativos que ainda não possuem parâmetros matemáticos cadastrados no nosso CSV. Por favor, adicione-os no banco de dados para liberar a prescrição.")

st.markdown("---")
st.button("🔄 Nova Consulta", on_click=limpar_consulta)
