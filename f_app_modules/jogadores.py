from datetime import datetime
import streamlit as st
import pandas as pd
from f_app_modules.salvar_dados import salvar_dados
from f_app_modules.variaveis_arquivo import variaveis

arquivo_jogadores, arquivo_financeiro, c, d = variaveis()

def adicionar_jogador_ui():
    """Interface para adicionar um novo jogador (mensalista ou convidado)."""
    st.subheader("🤝 Cadastrar jogador", anchor="cadastrar-jogador")
    st.markdown("[Ver lista de jogadores](#lista_jogadores)")
    
    JOGADORES = st.session_state['jogadores']
    FINANCEIRO = st.session_state['financeiro']
    
    VALOR_MENSALIDADE_ATUAL = FINANCEIRO['config']['mensalidade_atual']

    with st.form("cadastro_jogador", clear_on_submit=True):
        apelido = st.text_input("Apelido (ID único):", key="apelido_c").strip().title()
        posicao = st.selectbox("Posição:", ['Linha', 'Goleiro'], key="pos_c")
        telefone = st.text_input("Telefone: (Opcional)", key="tel_c").strip()
        nome_completo = st.text_input("Nome Completo: (Opcional)", key="nome_c").strip().title()
        status = st.checkbox("É Mensalista?", value=True)
        submitted = st.form_submit_button("Cadastrar jogador")

        if submitted:
            if not apelido or apelido in JOGADORES:
                st.error(f"❌ Apelido {apelido} inválido ou já em uso.")
                return
            
            # A única validação obrigatória é o Apelido
            
            JOGADORES[apelido] = {
                'nome': nome_completo or None, # Salva como None se estiver vazio
                'telefone': telefone or None, # Salva como None se estiver vazio
                'posicao': posicao,
                'mensalista': status,
                'data_cadastro': datetime.now().strftime("%Y-%m-%d"),
                'stats': {'gols': 0, 'amarelos': 0, 'vermelhos': 0}
            }
            
            mes_atual = datetime.now().strftime("%Y-%m")
            valor_devido = 0.0 if posicao == 'Goleiro' else VALOR_MENSALIDADE_ATUAL
            
            if apelido not in FINANCEIRO['mensalidades'] and JOGADORES[apelido]['mensalista'] == True:
                FINANCEIRO['mensalidades'][apelido] = {}
                
                FINANCEIRO['mensalidades'][apelido][mes_atual] = {
                    'pago': False,
                    'valor_devido': valor_devido,
                    'data_pagamento': None
                }  
                salvar_dados(FINANCEIRO, arquivo_financeiro)
            
            salvar_dados(JOGADORES, arquivo_jogadores)
            
            
            st.success(f'✅ Jogador "{apelido}" na posição "{posicao}" adicionado com sucesso!')

def alterar_dados_jogador_ui():
    """Permite alterar o nome, telefone, posição ou status de mensalista de um jogador."""
    st.subheader("✏️ Alterar Dados de Jogador", anchor='alterar-jogador')
    JOGADORES = st.session_state['jogadores']
    FINANCEIRO = st.session_state['financeiro']
    VALOR_MENSALIDADE_ATUAL = FINANCEIRO['config']['mensalidade_atual']

    apelido_escolhido = st.selectbox("Selecione o jogador para alterar:", 
                                    [''] + sorted(JOGADORES.keys()))
    
    if apelido_escolhido:
        jogador = JOGADORES[apelido_escolhido]
        
        with st.form("alterar_jogador_form", clear_on_submit=True):
            st.markdown(f'**Dados atuais de "{apelido_escolhido.upper()}":**')
            
            novo_nome = st.text_input("Novo Nome Completo:", value=jogador['nome'])
            novo_telefone = st.text_input("Novo Telefone:", value=jogador['telefone'])
            nova_posicao = st.selectbox("Nova Posição:", 
                                        ['Linha', 'Goleiro'], 
                                        index=0 if jogador['posicao'] == 'Linha' else 1)
            novo_status_mensalista = st.checkbox("É Mensalista?", value=jogador['mensalista'])

            submitted = st.form_submit_button("Salvar Alterações")

            if submitted:
                # Lógica de atualização
                jogador['nome'] = novo_nome
                jogador['telefone'] = novo_telefone
                
                # Ajuste de posição e status
                old_pos = jogador['posicao']
                old_mensalista = jogador['mensalista']
                
                jogador['posicao'] = nova_posicao
                jogador['mensalista'] = novo_status_mensalista
                
                # Lógica de ajuste financeiro (se status/posição mudou)
                if old_pos != nova_posicao or old_mensalista != novo_status_mensalista:
                    mes_atual = datetime.now().strftime("%Y-%m")
                    valor_devido = 0.0
                    
                    if apelido_escolhido not in FINANCEIRO['mensalidades'] and nova_posicao == 'Linha':
                        FINANCEIRO['mensalidades'][apelido_escolhido]= {}
                        FINANCEIRO['mensalidades'][apelido_escolhido][mes_atual] = {
                            'pago': False,
                            'valor_devido': valor_devido,
                            'data_pagamento': None
                            }
                    
                    if apelido_escolhido in FINANCEIRO['mensalidades'] and mes_atual in FINANCEIRO['mensalidades'][apelido_escolhido] and not FINANCEIRO['mensalidades'][apelido_escolhido][mes_atual]['pago']:
                        
                        if novo_status_mensalista and nova_posicao == 'Linha':
                            valor_devido = VALOR_MENSALIDADE_ATUAL
                            
                        FINANCEIRO['mensalidades'][apelido_escolhido][mes_atual]['valor_devido'] = valor_devido
                        st.warning("⚠️ Status/Posição alterada. O valor da mensalidade do mês atual foi ajustado.")

                salvar_dados(JOGADORES, arquivo_jogadores)
                salvar_dados(FINANCEIRO, arquivo_financeiro)
                st.success(f"✅ Dados de '{apelido_escolhido}' atualizados com sucesso.")

def listas_e_qtd_mensalistas_convidados():
    JOGADORES = st.session_state['jogadores']
    
    mensalistas = sorted([a for a, d in JOGADORES.items() if d.get('mensalista', False)])
    convidados = sorted([a for a, d in JOGADORES.items() if not d.get('mensalista', False)])
    qtd_mensalistas = len(mensalistas)
    qtd_convidados = len(convidados)
    return mensalistas, convidados, qtd_mensalistas, qtd_convidados

def gerar_dados_para_lista_global_jogadores(tipo_lista):
    JOGADORES = st.session_state['jogadores']
    FINANCEIRO = st.session_state['financeiro']
    SUMULAS = st.session_state['sumulas']
    
    mes_atual = datetime.now().strftime("%Y-%m")

    if not JOGADORES:
        st.info("Nenhum jogador cadastrado.")
        return

    dados_tabela = []
    jogadores_ordenados = sorted(JOGADORES.items())
    
    for apelido, dados in jogadores_ordenados:
        status = "N/A"
        gols, amarelos, vermelhos = 0, 0, 0

        if dados.get('mensalista', False):
            info_mensalidade = FINANCEIRO['mensalidades'].get(apelido, {}).get(mes_atual, {})
            if info_mensalidade:
                status = f"PAGO ({mes_atual})" if info_mensalidade.get('pago') else f"DEVEDOR R$ {info_mensalidade.get('valor_devido', 0.0):.2f}"
            else:
                status = "N/A (Novo Mês)"
        
        if 'stats' in dados:
            gols = dados['stats']['gols']
            amarelos = dados['stats']['amarelos']
            vermelhos = dados['stats']['vermelhos']

        linha = {
            'Apelido': apelido,
            'Posicao': dados['posicao'],
            'Status Jogador': 'Mensalista' if dados.get('mensalista', False) else 'Convidado',
            'Gols': gols,
            '🟨': amarelos,
            '🟥': vermelhos,
        }
        
        if tipo_lista == 'cadastro':
            linha[f'Status Mensalidade ({mes_atual})'] = status
        
        dados_tabela.append(linha)
    
    df = pd.DataFrame(dados_tabela)
    
    return df

def listar_jogadores_ui(tipo_lista):
    df = gerar_dados_para_lista_global_jogadores(tipo_lista)
    with st.form('lista_jogadores'):
        submitted = st.form_submit_button(f'Atualizar dados')
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        if submitted:
            st.rerun()
    return
