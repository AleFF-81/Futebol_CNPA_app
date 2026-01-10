from datetime import datetime
import streamlit as st
import pandas as pd
from f_app_modules.jogadores import gerar_dados_para_lista_global_jogadores
from f_app_modules.salvar_dados import salvar_dados
from f_app_modules.variaveis_arquivo import variaveis
from f_app_modules.datas import gerar_ano_anterior
from f_app_modules.pagamentos import calcular_saldo_ano_anterior

arquivo_jogadores, b, arquivo_sumulas, d = variaveis()

def calcular_geral_ui():
    """Calcula e exibe o saldo geral do grupo (Receitas - Despesas)."""
    ano = str(datetime.now().year)
    st.subheader(f"💰 Balanço Financeiro - {ano}")
    FINANCEIRO = st.session_state['financeiro']
    JOGADORES = st.session_state['jogadores']
    saldo_ano_anterior = calcular_saldo_ano_anterior(ano)
    ano_anterior = gerar_ano_anterior(ano)
    
    receitas = 0.0
    despesas = sum(gasto['valor'] for gasto in FINANCEIRO['gastos_comuns'] if gasto['data'].startswith(ano))
    
    # Soma todas as mensalidades PAGAS
    for apelido in FINANCEIRO['mensalidades']:
        for mes in FINANCEIRO['mensalidades'][apelido]:
            if mes.startswith(ano):
                info = FINANCEIRO['mensalidades'][apelido][mes]
                if info.get('pago'):
                    # Usa 'valor_pago' se existir, senão 'valor_devido' (mantendo a lógica de valor efetivamente pago)
                    valor = info.get('valor_pago', info.get('valor_devido', 0.0))
                    receitas += valor
                
    for responsavel, lista_convites in FINANCEIRO['convites'].items():
        for convite in lista_convites:
            if convite['data_jogo'].startswith(ano) and convite['pago']:
                receitas += convite['valor_cobrado']
                
    # Sumariza convites pagos (assumindo que foram registrados via pagamentos de mensalidade ou gastos comuns)
    
    saldo = receitas - despesas
    
    col_1, col_2, col_3, col_sld = st.columns(4)
    with col_1:
        st.metric(("Mensalidade atual:"), f"R$ {FINANCEIRO['config']['mensalidade_atual']:.2f}")
        st.metric(("Convite atual:"), f"R$ {FINANCEIRO['config']['valor_convite_atual']:.2f}")
    with col_2:
        st.metric("Total Receitas (Mensalidades e convites)", f"R$ {receitas:.2f}")
        st.metric("Total Despesas (Gastos Comuns)", f"R$ {despesas:.2f}")
    with col_3:
        st.metric(f"SALDO - {ano}:\n", f"R$ {saldo:.2f}")
        st.metric(f"SALDO - {ano_anterior}:\n", f"R$ {saldo_ano_anterior:.2f}")
    with col_sld:
        st.metric("📊 SALDO FINAL:\n", f"R$ {(saldo + saldo_ano_anterior):.2f}")
    
    st.markdown('---')
        
    # calcula as estatísticas Globais
    if JOGADORES:
        lista_global = gerar_dados_para_lista_global_jogadores('outro') # Carrega dados das estatísticas globais
        if len(lista_global) >= 3:
            st.subheader('📊 Jogadores em destaque')
            col_global, col_anual = st.columns(2)
            
            with col_global:
            # TOP 3 artilheiros globais:
                st.markdown('ESTATÍSTICA GLOBAL')
                df_tres_melhores_global = lista_global.nlargest(n=3, columns='Gols').reset_index(drop=True)
                
                jogador_ouro_global = df_tres_melhores_global.at[0, 'Apelido']
                jogador_prata_global = df_tres_melhores_global.at[1, 'Apelido']
                jogador_bronze_global = df_tres_melhores_global.at[2, 'Apelido']
                gols_ouro_global = df_tres_melhores_global.at[0, 'Gols']
                gols_prata_global = df_tres_melhores_global.at[1, 'Gols']
                gols_bronze_global = df_tres_melhores_global.at[2, 'Gols']
                
                if gols_ouro_global > 0:
                    col_gols1, col_gols2 = st.columns([1,3])
                    with col_gols1:
                        st.image('imgs/chuteira_ouro.png')
                    with col_gols2:    
                        st.metric("Chuteira de OURO \n", f'{jogador_ouro_global} - {gols_ouro_global} Gols')
                    
                    st.markdown(f'2º - Chuteira de Prata - {jogador_prata_global} - {gols_prata_global} Gols')
                    st.markdown(f'3º - Chuteira de Bronze - {jogador_bronze_global} - {gols_bronze_global} Gols')
                        
            with col_anual:
                st.markdown('ESTATÍSTICA ANUAL')
                lista_anual = gerar_estatistica_anual(ano)
                
                if lista_anual.empty:
                    st.error(f'Não há dados para o ano de {ano}.')

                if len(lista_anual) >= 3:    
                    with st.form('estat_anual_dash'):
                        ano_input = st.text_input('Digite o ano:', value=ano, key='ano_input')
                        submitted = st.form_submit_button('Gerar estatísticas')
                        
                        if submitted:
                            lista_anual = gerar_estatistica_anual(ano_input)
                            df_tres_melhores_anual = lista_anual.nlargest(n=3, columns='Gols').reset_index(drop=True)
                    
                            jogador_ouro_anual = df_tres_melhores_anual.at[0, 'Apelido']
                            jogador_prata_anual = df_tres_melhores_anual.at[1, 'Apelido']
                            jogador_bronze_anual = df_tres_melhores_anual.at[2, 'Apelido']
                            gols_ouro_anual = df_tres_melhores_anual.at[0, 'Gols']
                            gols_prata_anual = df_tres_melhores_anual.at[1, 'Gols']
                            gols_bronze_anual = df_tres_melhores_anual.at[2, 'Gols']
                            
                            if gols_ouro_anual > 0:
                                st.subheader(f'DESTAQUES DE "{ano_input}"')
                                col_gols1, col_gols2 = st.columns([1,3])
                                with col_gols1:
                                    st.image('imgs/chuteira_ouro.png')
                                with col_gols2:    
                                    st.metric("Chuteira de OURO \n", f'{jogador_ouro_anual} - {gols_ouro_anual} Gols')
                                
                                st.markdown(f'2º - Chuteira de Prata - {jogador_prata_anual} - {gols_prata_anual} Gols')
                                st.markdown(f'3º - Chuteira de Bronze - {jogador_bronze_anual} - {gols_bronze_anual} Gols')

def editar_estatisticas_sumula_ui():
    """Interface para editar as estatísticas por data e salvar os dados no SUMULAS."""
    JOGADORES = st.session_state['jogadores']
    SUMULAS = st.session_state['sumulas'] 
    
    todas_datas = sorted(SUMULAS.keys(), reverse=True)
    if not todas_datas:
        st.warning("Crie uma súmula primeiro.")
        return
        
    # 1. Seleção da Data
    st.info('Selecione uma data para EXIBIR ou EDITAR estatísticas da partida 👇')
    data_consulta = st.selectbox("Data:", [''] + todas_datas, key="data_edicao_stats")
    
    if not data_consulta: return
    
    sumula_atual = SUMULAS[data_consulta]
    detalhes = sumula_atual['detalhes_jogadores']
    
    # 2. Preparar dados para o DataFrame
    dados_tabela = []
    
    # Ordenação (Mensalistas primeiro, Convidados depois, ambos alfabeticamente)
    lista_ordenada = []
    
    # Separação e ordenação (reutilizando a lógica anterior)
    mensalistas = []
    convidados = []
    
    for apelido in sumula_atual.get('lista_presenca', []):
        registro = detalhes.get(apelido)
        if registro:
            if registro['status'] == 'Mensalista':
                mensalistas.append(registro)
            else:
                convidados.append(registro)
    
    mensalistas.sort(key=lambda x: x['apelido'])
    convidados.sort(key=lambda x: x['apelido'])
    lista_ordenada = mensalistas + convidados

    # Monta a estrutura de dados com as estatísticas atuais da súmula
    for registro in lista_ordenada:
        stats = registro.get('stats_data', {'gols': 0, 'amarelos': 0, 'vermelhos': 0})
        
        dados_tabela.append({
            'Apelido': registro['apelido'],
            'Status': 'Mens' if registro['status'] == 'Mensalista' else 'Conv',
            'Posição': 'L' if registro['posicao'] == 'Linha' else 'G',
            'Resp.': registro['responsavel'],
            # Colunas Editáveis (Controle estatístico individual por data)
            'Gols': stats['gols'],
            '🟨': stats['amarelos'],
            '🟥': stats['vermelhos']
        })
        
    df_sumula = pd.DataFrame(dados_tabela)

    st.markdown(f"#### Súmula de {data_consulta} - Edição de Estatísticas")
    
    # 3. Exibição e Edição
    df_editado = st.data_editor(
        df_sumula, 
        use_container_width=True, 
        hide_index=True, 
        key=f"sumula_stats_editor_{data_consulta}",
        column_config={
            # Tornar não editáveis as colunas de identificação
            "Apelido": st.column_config.Column(disabled=True),
            "Status": st.column_config.Column(disabled=True),
            "Posição": st.column_config.Column(disabled=True),
            "Resp.": st.column_config.Column(disabled=True),
            # Definir Gols/Cartões como números inteiros
            "Gols": st.column_config.NumberColumn(min_value=0, default=0),
            "🟨": st.column_config.NumberColumn(min_value=0, default=0),
            "🟥": st.column_config.NumberColumn(min_value=0, default=0)
        }
    )
    
    # 4. Salvar Estatísticas na Súmula (SUMULAS)
    if st.button(f"Salvar Estatísticas da Partida e Atualizar Globais ({data_consulta})", key=f"btn_salvar_stats_{data_consulta}"):
        
        # 4.1. Salvar na Súmula (dados_sumula.json)
        for index, row in df_editado.iterrows():
            apelido = row['Apelido']
            
            # Atualiza o dicionário de detalhes da súmula atual
            detalhes[apelido]['stats_data'] = {
                'gols': int(row['Gols']),
                'amarelos': int(row['🟨']),
                'vermelhos': int(row['🟥'])
            }
            
        # Persiste a súmula
        SUMULAS[data_consulta]['detalhes_jogadores'] = detalhes
        salvar_dados(SUMULAS, arquivo_sumulas)
        
        # 4.2. Atualizar Estatísticas Globais (JOGADORES)
        atualizar_estatisticas_globais(JOGADORES, SUMULAS) # Chamamos a próxima função
        
        st.success(f"✅ Estatísticas da partida e estatísticas globais atualizadas com sucesso para **{data_consulta}**!")
        st.rerun()

def gerar_estatistica_anual(ano):
    JOGADORES = st.session_state['jogadores']
    SUMULAS = st.session_state['sumulas']
    
    estatistica_anual = []
    df = pd.DataFrame(estatistica_anual)
        
    for apelido in sorted(JOGADORES.keys()):
        estatistica_acumulada = {
            'Apelido': apelido,
            'Gols': 0,
            'Ama': 0,
            'Verm': 0
        }
        
        for data_str, sumula in SUMULAS.items():
            if data_str.startswith(ano):
                detalhes_jogadores = sumula.get('detalhes_jogadores', {})
                
                registro = detalhes_jogadores.get(apelido)
                
                if registro:
                    
                    stats_data = registro.get('stats_data', {'gols': 0, 'amarelos': 0, 'vermelhos': 0})
                    
                    estatistica_acumulada['Gols'] += stats_data['gols']
                    estatistica_acumulada['Ama'] += stats_data['amarelos']
                    estatistica_acumulada['Verm'] += stats_data['vermelhos']  
        
        estatistica_anual.append(estatistica_acumulada)

    df = pd.DataFrame(estatistica_anual)

    return df

def exibir_estatistica_anual():
    with st.form("estat_anual", clear_on_submit=True):
        ano = st.text_input("Ano (AAAA):", value=str(datetime.now().year), key="rel_ind_ano")
        
        submitted = st.form_submit_button('Gerar Estatísticas')
        
        if submitted:
            df = gerar_estatistica_anual(ano)
            
            if not df.empty:
                st.info(f'Estatísticas de {ano}:')
                st.dataframe(df, use_container_width=True, hide_index=True)
            else:
                st.warning(f'Não há estatísticas para exibir do ano "{ano}".')

def atualizar_estatisticas_globais(JOGADORES, SUMULAS):
    """Soma as estatísticas de todas as súmulas e atualiza o dicionário global JOGADORES."""
    
    # 1. Resetar todas as estatísticas globais dos Mensalistas
    for apelido in JOGADORES:
        JOGADORES[apelido]['stats'] = {'gols': 0, 'amarelos': 0, 'vermelhos': 0}
        
    # 2. Recalcular a soma total a partir de todas as súmulas
    
    # Itera sobre todas as datas (súmulas)
    for data_str, sumula in SUMULAS.items():
        
        # Itera sobre todos os jogadores/convidados naquela súmula
        for apelido, registro in sumula.get('detalhes_jogadores', {}).items():
            
            stats_data = registro.get('stats_data', {'gols': 0, 'amarelos': 0, 'vermelhos': 0})
            
            # Checa se o jogador existe
            if apelido in JOGADORES:
                # Soma as estatísticas no registro global do Mensalista
                JOGADORES[apelido]['stats']['gols'] += stats_data['gols']
                JOGADORES[apelido]['stats']['amarelos'] += stats_data['amarelos']
                JOGADORES[apelido]['stats']['vermelhos'] += stats_data['vermelhos']

    # 3. Salvar o arquivo de JOGADORES atualizado
    salvar_dados(JOGADORES, arquivo_jogadores)
    
    # Nota: Esta função não tem UI e será chamada apenas internamente.
    # O feedback de sucesso é dado pela função que a chamou (editar_estatisticas_sumula_ui).
    return True
