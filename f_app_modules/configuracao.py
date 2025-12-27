import streamlit as st
from datetime import datetime
from f_app_modules.salvar_dados import salvar_dados
from f_app_modules.variaveis_arquivo import variaveis

a, arquivo_financeiro, c, d = variaveis()

def alterar_config_financeira_ui():
    """Interface para alterar o valor da mensalidade e do convite."""
    st.header("⚙️ Configuração Financeira")
    
    col_mens, col_conv = st.columns(2)
    with col_mens:
        alterar_valor_mensalidade_ui()
    with col_conv:
        alterar_valor_convidado_ui()

def alterar_valor_mensalidade_ui():
    """Interface para alterar o valor da mensalidade (sub-função)."""
    st.subheader("Alterar Valor da Mensalidade")
    FINANCEIRO = st.session_state['financeiro']
    VALOR_ATUAL = FINANCEIRO['config']['mensalidade_atual']
    DATA_ATUAL = FINANCEIRO['config']['data_alt_mensalidade']
    
    st.info(f"Valor atual: R$ {VALOR_ATUAL:.2f}. Última alteração: {DATA_ATUAL}")
    
    with st.form("config_mensalidade_form"):
        novo_valor = st.number_input("Novo Valor da Mensalidade:", min_value=0.0, step=0.01, key='novo_val_mensal')
        
        submitted = st.form_submit_button("Alterar Mensalidade", key='btn_alterar_mensal')

        if submitted:
            # ... (Lógica de salvamento original da mensalidade) ...
            if novo_valor <= 0:
                st.error("❌ O valor deve ser positivo.")
                return

            DATA_ULTIMA_ALTERACAO = datetime.now().strftime("%Y-%m-%d")

            FINANCEIRO['config']['mensalidade_atual'] = novo_valor
            FINANCEIRO['config']['data_alt_mensalidade'] = DATA_ULTIMA_ALTERACAO

            salvar_dados(FINANCEIRO, arquivo_financeiro)
            st.success(f"✅ Mensalidade alterada para R$ {novo_valor:.2f} em {DATA_ULTIMA_ALTERACAO}.")

def alterar_valor_convidado_ui():
    """Interface para alterar o valor fixo do convidado."""
    st.subheader("Alterar Valor do Convite")
    FINANCEIRO = st.session_state['financeiro']
    VALOR_ATUAL = FINANCEIRO['config']['valor_convite_atual']
    DATA_ATUAL = FINANCEIRO['config']['data_alt_convite']
    
    st.info(f"Valor atual do convite: R$ {VALOR_ATUAL:.2f}. Última alteração: {DATA_ATUAL}")
    
    with st.form("config_convite_form"):
        novo_valor = st.number_input("Novo Valor Fixo do Convite:", min_value=0.0, step=5.0)
        
        submitted = st.form_submit_button("Alterar Valor Convite")

        if submitted:
            if novo_valor < 0:
                st.error("❌ O valor não pode ser negativo.")
                return

            DATA_ULTIMA_ALTERACAO = datetime.now().strftime("%Y-%m-%d")

            FINANCEIRO['config']['valor_convite_atual'] = novo_valor
            FINANCEIRO['config']['data_alt_convite'] = DATA_ULTIMA_ALTERACAO

            salvar_dados(FINANCEIRO, arquivo_financeiro)
            st.success(f"✅ Valor do convite alterado para R$ {novo_valor:.2f} em {DATA_ULTIMA_ALTERACAO}.")
