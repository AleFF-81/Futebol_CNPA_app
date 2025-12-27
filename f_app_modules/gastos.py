import streamlit as st
import pandas as pd
from datetime import datetime
from f_app_modules.salvar_dados import salvar_dados
from f_app_modules.variaveis_arquivo import variaveis
from f_app_modules.datas import converter_data, reverter_data

a, arquivo_financeiro, c, d = variaveis()

def registrar_gasto_comum_ui():
    """Interface para registrar gastos comuns do grupo."""
    st.subheader("💸 Registrar Gasto Comum do Grupo")
    FINANCEIRO = st.session_state['financeiro']
    
    with st.form("gasto_form", clear_on_submit=True):
        descricao = st.text_input("Descrição do Gasto:").strip()
        valor = st.number_input("Valor Total do Gasto:", min_value=0.0, step=0.01)
        data_gasto = st.date_input("Data do Gasto:", value=datetime.now())
        
        submitted = st.form_submit_button("Registrar Gasto")

        if submitted:
            data_str = data_gasto.strftime("%Y-%m-%d")
            
            FINANCEIRO['gastos_comuns'].append({
                'data': data_str,
                'descricao': descricao,
                'valor': valor
            })

            salvar_dados(FINANCEIRO, arquivo_financeiro)
            st.success(f"✅ Gasto de R$ {valor:.2f} registrado para '{descricao}'.")

def listar_gastos_comuns_ui():
    ### LISTA OS GASTOS REALIZADOS E POSSIBILITA EDIÇÃO DOS DADOS
    st.subheader("✅💸 Gastos lançados")
    FINANCEIRO = st.session_state['financeiro']

    if not FINANCEIRO['gastos_comuns']:
        st.info("Nenhum gasto cadastrado.")
        return

    gastos = []
    total_gastos = 0
    
    for dados in FINANCEIRO['gastos_comuns']:
        total_gastos += dados['valor']
        data_convertida = converter_data(dados['data'])
        gastos.append({
            'Data': data_convertida,
            'Descrição': dados['descricao'],
            'Valor': f" R$ {dados['valor']:.2f}"
        })
    
    df2 = pd.DataFrame(gastos)
    st.markdown(f'Total de gastos: R$ {total_gastos:.2f}')
    # Exibição e Edição dos dados registrados
    df_editado2 = st.data_editor(
        df2, 
        use_container_width=True, 
        hide_index=True, 
        key="gatos",
        column_config={
            # Tornar editáveis as colunas
            "Data": st.column_config.Column(disabled=False),
            "Descrição": st.column_config.Column(disabled=False),
            "Valor": st.column_config.Column(disabled=False)
        }
    )
    
    if st.button(f"Salvar Gastos", key=f"btn_salvar_gastos"):
        detalhes_gastos = []
        # Salvar os novos dados dos gastos no Financeiro (dados_financeiro.json)
        for index, row in df_editado2.iterrows():
            valor_convertido = float(row['Valor'].removeprefix(" R$ "))
            data_revertida = reverter_data(row['Data'])
            
            # Atualiza o dicionário de gastos no Financeiro
            detalhes_gastos.append({
                'data': data_revertida,
                'descricao': str(row['Descrição']),
                'valor': valor_convertido
            })
            
        # Persiste o arquivo Financeiro
        FINANCEIRO['gastos_comuns'] = detalhes_gastos
        salvar_dados(FINANCEIRO, arquivo_financeiro)
        st.success(f'Dados salvos com sucesso!')
        #st.rerun()
    
    #st.dataframe(df, use_container_width=True, hide_index=True)
