import streamlit as st
import pandas as pd
from datetime import datetime
from f_app_modules.variaveis_arquivo import variaveis
from f_app_modules.salvar_dados import salvar_dados

a, arquivo_financeiro, c, d = variaveis()

def registrar_pagamento_mensalidade_ui():
    """Interface para registrar o pagamento da mensalidade com detalhes de data."""
    st.subheader("💲Pagamento de Mensalidade")
    JOGADORES = st.session_state['jogadores']
    FINANCEIRO = st.session_state['financeiro']
    VALOR_MENSALIDADE_ATUAL = FINANCEIRO['config']['mensalidade_atual']

    # Lista dos mensalistas cadastrados com filtro para excluir os goleiros (isentos da mensalidade)
    mensalistas = {k: v for k, v in JOGADORES.items() if v.get('mensalista', False) and v.get('posicao') == 'Linha'}
    
    # Adicionando um key para limpar o formulário após o registro
    with st.form("pagamento_form", clear_on_submit=True): 
        apelido = st.selectbox("Apelido do jogador que pagou:", [''] + sorted(mensalistas.keys()), key="pg_apelido")
        
        # Datas e Referências
        mes_referencia = st.text_input("Mês e ano de Referência (AAAA-MM, ex: 2025-11):", 
                                    value=datetime.now().strftime("%Y-%m"), key="pg_ref")
        data_efetiva = st.date_input("Data Efetiva do Pagamento:", 
                                    value=datetime.now(), key="pg_data_efetiva")
        
        # Tenta pré-calcular o valor devido se o jogador for selecionado
        valor_devido_calc = 0.0
        if apelido and apelido in mensalistas:
            pos = mensalistas[apelido]['posicao']
            # PONTO 2: Valor Devido é o valor da mensalidade (Mensalidade/0.0)
            valor_devido_calc = 0.0 if pos == 'Goleiro' else VALOR_MENSALIDADE_ATUAL
        
        # st.info(f"Valor Devido (Mensalidade Fixa): R$ {valor_devido_calc:.2f}")

        # PONTO 2: Valor Pago é o que foi efetivamente pago
        valor_pago = st.number_input(f"Valor Pago Efetivamente:", 
                                    min_value=0.0, step=0.01, key="pg_valor_pago")
        
        submitted = st.form_submit_button("Registrar Pagamento")

        if submitted:
            if not apelido or apelido not in mensalistas:
                st.error("❌ Selecione um mensalista válido.")
                return
            
            if valor_pago <= 0:
                st.error('❌ Digite uma valor maior que zero')
                return

            # Data de registro interno
            data_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data_efetiva_str = data_efetiva.strftime("%Y-%m-%d")

            if apelido not in FINANCEIRO['mensalidades']:
                FINANCEIRO['mensalidades'][apelido] = {}

            # Estrutura do novo registro:
            novo_registro = {
                'pago': True, 
                'valor_devido': valor_devido_calc,
                'valor_pago': valor_pago,
                'data_referencia': mes_referencia,
                'data_efetiva': data_efetiva_str,
                'data_registro_sistema': data_registro
            }
            
            # Sobrescreve o registro, garantindo que a referência é única
            FINANCEIRO['mensalidades'][apelido][mes_referencia] = novo_registro
            
            salvar_dados(FINANCEIRO, arquivo_financeiro)
            st.success(f'✅ Pagamento de R$ {valor_pago:.2f} registrado para "{apelido.upper()}" referente a {mes_referencia}.')

            # O Streamlit limpa o formulário automaticamente se 'clear_on_submit=True'
            # O cursor retorna automaticamente ao primeiro campo.

def registrar_pagamento_convite_ui():
    """Interface para registrar o pagamento de convites pendentes."""
    st.subheader("💲Pagamento de Convites")
    
    FINANCEIRO = st.session_state['financeiro']
    
    # 1. Preparar a lista de convites pendentes
    opcoes_pagamento = []
    
    # Itera sobre os responsáveis e seus convites
    for responsavel, lista_convites in FINANCEIRO['convites'].items():
        # Usamos enumerate(lista_convites) para obter o índice (i) de forma segura
        for i, convite in enumerate(lista_convites):
            if not convite.get('pago', False): # Verifica se o convite está PENDENTE
                
                data_jogo = convite['data_jogo']
                apelido_convidado = convite['convidado_apelido']
                valor = convite['valor_cobrado']
                
                # Cria uma string descritiva para o selectbox
                descricao = f"R$ {valor:.2f} | {data_jogo} | Convidado: {apelido_convidado} (Resp: {responsavel})"
                
                # Armazena a opção completa (índice, responsável)
                opcoes_pagamento.append({
                    'label': descricao,
                    'responsavel': responsavel,
                    'indice': i
                })

    # --- Lógica de Exibição / Supressão do Formulário ---
    
    if not opcoes_pagamento:
        # Se não há pendências, exibe a informação e termina a função.
        st.info("🎉 Não há convites pendentes de pagamento.")
        return # ⬅️ O `return` garante que o restante do código (Formulário e Tabela) não será executado.

    # 2. Formulário de Pagamento (Só é exibido se houver opcoes_pagamento)
    with st.form("form_pagamento_convite"):
        
        # Cria uma lista de labels para o selectbox
        labels = [op['label'] for op in opcoes_pagamento]
        
        # Permite ao usuário selecionar o convite
        convite_selecionado_label = st.selectbox(
            "Convites Pendentes:", 
            labels,
            key="select_convite_pago"
        )
        
        data_pag = st.date_input("Data Efetiva do Pagamento:", 
                                value=datetime.now(), 
                                key="pg_conv")
        data_pag_str = data_pag.strftime("%Y-%m-%d")
        
        submitted = st.form_submit_button("Marcar como Pago")
        
        if submitted:
            # Encontra o objeto de opção completo (com responsavel e indice)
            opcao_selecionada = next(
                (op for op in opcoes_pagamento if op['label'] == convite_selecionado_label), 
                None
            )

            if opcao_selecionada:
                resp = opcao_selecionada['responsavel']
                idx = opcao_selecionada['indice']
                
                # 3. Atualizar o status 'pago' e registrar a data de pagamento
                FINANCEIRO['convites'][resp][idx]['pago'] = True
                FINANCEIRO['convites'][resp][idx]['data_pag'] = data_pag_str
                
                # 4. Persistir os dados
                salvar_dados(FINANCEIRO, arquivo_financeiro)
                
                st.success(f"✅ Pagamento do convite de **{FINANCEIRO['convites'][resp][idx]['convidado_apelido']}** registrado com sucesso!")
                
                st.rerun()
            else:
                st.error("Erro ao processar o pagamento. Tente selecionar novamente.")
    
    # --- Tabela de Visualização ---
    st.markdown("---")
    st.markdown("#### Relação de Convites Pendentes")
    
    dados_tabela = []
    # Reutiliza a lista 'opcoes_pagamento' que já está filtrada e populada
    for op in opcoes_pagamento:
        resp = op['responsavel']
        idx = op['indice']
        
        # Acessa os dados diretamente do FINANCEIRO usando o índice e responsável
        convite = FINANCEIRO['convites'][resp][idx] 
        dados_tabela.append({
            "Responsável": resp,
            "Convidado": convite['convidado_apelido'],
            "Data do Jogo": convite['data_jogo'],
            "Valor (R$)": f"{convite['valor_cobrado']:.2f}"
        })
        
    if dados_tabela:
        df_pendentes = pd.DataFrame(dados_tabela)
        st.dataframe(df_pendentes, hide_index=True, use_container_width=True)
