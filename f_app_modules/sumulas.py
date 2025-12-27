import streamlit as st
import pandas as pd
from datetime import datetime
from f_app_modules.variaveis_arquivo import variaveis
from f_app_modules.salvar_dados import salvar_dados

a, arquivo_financeiro, arquivo_sumulas, d = variaveis()

def criar_sumula_simples_ui():
    """Interface e lógica para criar um registro de súmula simples (data e observações)."""
    st.subheader(f"🗓️ Criar Súmula")
    
    # Carrega o estado atual da súmula
    SUMULAS = st.session_state['sumulas'] 
    
    with st.form("form_criar_sumula_simples", clear_on_submit=True):
        # 1. Opção simples para criar dados de súmula
        data_jogo = st.date_input("Data do Jogo:", value=datetime.now(), key="data_nova_sumula")
        data_str = data_jogo.strftime("%Y-%m-%d")
        
        observacoes = st.text_area("Observações da Partida (Opcional):", key="obs_nova_sumula")
        
        submitted = st.form_submit_button("Criar")
        
        if submitted:
            if data_str in SUMULAS:
                st.warning(f"⚠️ Súmula para a data {data_str} já existe! Edite a súmula existente.")
            else:
                # Inicializa a estrutura da súmula
                SUMULAS[data_str] = {
                    'observacoes': observacoes,
                    'lista_presenca': [], # Lista de apelidos que estarão na súmula
                    'detalhes_jogadores': {} # Armazenará os dados estatísticos e a posição por jogador/convidado nesta data
                }
                
                # Salva a súmula
                salvar_dados(SUMULAS, arquivo_sumulas)
                
                st.success(f"✅ Súmula simples para **{data_str}** criada com sucesso!")
                st.rerun()

def cadastrar_jogadores_na_sumula_ui():
    """Interface para adicionar mensalistas e convidados a uma súmula existente, mantendo a ordem e estatísticas."""
    st.subheader("✍️ Cadastrar Jogadores na Súmula")
    
    JOGADORES = st.session_state['jogadores']
    SUMULAS = st.session_state['sumulas']
    FINANCEIRO = st.session_state['financeiro']
    
    # 2.1 Seleção da Data
    todas_datas = sorted(SUMULAS.keys(), reverse=True)
    if not todas_datas:
        st.warning("Crie uma súmula simples primeiro.")
        return
        
    data_consulta = st.selectbox("Selecione a Data da Súmula:", [''] + todas_datas, key="data_cadastro_sumula")
    
    if not data_consulta: return
    
    sumula_atual = SUMULAS[data_consulta]
    
    # --- FORMULÁRIO DE CADASTRO DE MENSALISTAS/CONVIDADOS ---
    col1, col2 = st.columns(2)
    with col1:
        with st.form("form_adicionar_jogador_sumula", clear_on_submit=True):
            st.markdown("##### Dados do jogador")
            
            todos_jogadores = sorted(JOGADORES.keys())
            mensalistas_ativos = sorted([k for k, v in JOGADORES.items() if v.get('mensalista', False)])
            
            apelido = st.selectbox("Apelido do Mensalista ou Convidado", [''] + todos_jogadores, key="resp_convidado")
            
            responsavel = st.selectbox("Apelido do Responsável (necessário para CONVIDADOS): ", [''] + mensalistas_ativos, key="apelido_convidado").strip()
            
            posicao = JOGADORES.get(apelido, {}).get('posicao')
            
            if JOGADORES.get(apelido, {}).get('mensalista') is True:
                status = 'Mensalista'
            else:
                status = 'Convidado'
            
            # Se for  Mensalistas
            if apelido in mensalistas_ativos:
                responsavel = 'N/A'

            submitted = st.form_submit_button(f"Adicionar jogador à Súmula {data_consulta}")
            
            if submitted:
                if not apelido:
                    st.error('O campo "APELIDO" não pode estar vazio.')
                    return

                if apelido in sumula_atual['lista_presenca']:
                    st.error(f'"{apelido.upper()}" já está registrado na súmula de {data_consulta}.')
                    return
                
                if not responsavel and apelido not in mensalistas_ativos:
                    st.error(f'"{apelido.upper()}" não é mensalista. insira um "RESPONSÁVEL".')
                    return

                # Estrutura de registro do jogador na súmula (Ponto 2 e Ponto 3)
                novo_registro = {
                    'apelido': apelido,
                    'status': status,
                    'posicao': posicao,
                    'responsavel': responsavel, # N/A para mensalistas
                    # Ponto 5: O controle estatístico será individual por cada jogador, em cada data
                    'stats_data': {'gols': 0, 'amarelos': 0, 'vermelhos': 0} 
                }
                
                # Adiciona o jogador à lista de presença
                sumula_atual['lista_presenca'].append(apelido)
                # Armazena os detalhes, usando o apelido como chave
                sumula_atual['detalhes_jogadores'][apelido] = novo_registro

                # 4. A súmula deve ficar em ordem alfabética
                # Simplificação: Garantimos a ordem no momento da visualização, mas a lista de presença pode ser ordenada aqui.
                sumula_atual['lista_presenca'].sort()

                # Salva a súmula com os novos dados
                SUMULAS[data_consulta] = sumula_atual
                salvar_dados(SUMULAS, arquivo_sumulas)
                
                # Lógica para adicionar o convite no Financeiro
                
                if status == 'Convidado' and posicao != 'Goleiro':
                    convite_atual = FINANCEIRO['config']['valor_convite_atual']
                    novo_convite = {
                        'data_jogo': data_consulta,
                        'convidado_apelido': apelido,
                        'posicao': posicao,
                        'valor_cobrado': convite_atual,
                        'pago': False,
                        'data_pag': None,
                    }
                    
                    # Armazenamento no FINANCEIRO, agrupado por responsável
                    if responsavel not in FINANCEIRO['convites']:
                        FINANCEIRO['convites'][responsavel] = []
                        
                    FINANCEIRO['convites'][responsavel].append(novo_convite)
                
                    salvar_dados(FINANCEIRO, arquivo_financeiro) # Salva no arquivo financeiro
                
                    st.success(f'✅ Convidado "**{apelido}**"" registrado com sucesso. Cobrança de R$ {convite_atual:.2f} adicionada para **{responsavel}**.')

                else:
                    st.success(f'✅ Jogador "**{apelido}**" adicionado à súmula de {data_consulta}!')
                #st.rerun()
    with col2:
            # --- VISUALIZAÇÃO DA SÚMULA ATUAL ---
            st.markdown(f"### Jogadores confirmados em {data_consulta}")
    
            # Ponto 4: A súmula deve ficar em ordem alfabética, primeiro os mensalistas, em seguida os convidados.
            
            # Filtra os registros para ordenação
            mensalistas = []
            convidados = []
            
            for apelido in sumula_atual['lista_presenca']:
                registro = sumula_atual['detalhes_jogadores'][apelido]
                if registro['status'] == 'Mensalista':
                    mensalistas.append(registro)
                else:
                    convidados.append(registro)
                    
            # Ordena ambas as listas alfabeticamente pelo apelido
            mensalistas.sort(key=lambda x: x['apelido'])
            convidados.sort(key=lambda x: x['apelido'])
            
            lista_ordenada = mensalistas + convidados
            
            # Cria a tabela de exibição
            df = pd.DataFrame([
                {
                    'Apelido': p['apelido'], 
                    'Status': p['status'],
                    'Posição': p['posicao'],
                    'Responsável': p['responsavel'] if p['status'] != 'Mensalista' else '—'
                }
                for p in lista_ordenada
            ])
            
            if not df.empty:
                st.dataframe(df, hide_index=True, use_container_width=True)
