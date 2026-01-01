import streamlit as st
import pandas as pd
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.lib import colors
from io import BytesIO
import os
from f_app_modules.jogadores import listas_e_qtd_mensalistas_convidados
from f_app_modules.datas import converter_data, gerar_ano_anterior


def gerar_dados_relatorio_individual(apelido, ano, JOGADORES, FINANCEIRO):
    """Calcula os dados do relatório individual e retorna os dados e o PDF."""
    a, b, qtd_mensalistas, d  = listas_e_qtd_mensalistas_convidados()
    saldo_ano_anterior = 0
    
    pagamentos_do_ano = {
        mes: info for mes, info in FINANCEIRO['mensalidades'].get(apelido, {}).items() 
        if mes.startswith(ano)
    }

    #if not pagamentos_do_ano:
    #   return None, None, 0.0, 0.0
    
    # Processar os pagamentos das mensalidades
    dados_mensalidade = []
    total_pago = 0.0
    total_devido = 0.0
    total_gastos = 0.0
    dados_tabela_gastos = []
    
    for mes in sorted(pagamentos_do_ano.keys()):
        info = pagamentos_do_ano[mes]
        status = "PAGO" if info['pago'] else "DEVEDOR"
        valor_devido = info.get('valor_devido', 0.0)
        
        # Se 'pago' é False, valor_pago é 0.0, senão usa o valor registrado.
        if info['pago']:
            valor_pago = info.get('valor_pago', valor_devido) # Se pago, usa o valor pago, senão o devido
        else:
            valor_pago = 0.0 # Se não foi pago, o valor pago é ZERO

        data_pag = info.get('data_efetiva', 'N/A')
        
        # Converte a data para ao formato (dia-mês-ano)
        if data_pag != 'N/A':
            data_pag = converter_data(data_pag)
        
        dados_mensalidade.append({
            'Mês': mes,
            'Status': status,
            'Devido': f"R$ {valor_devido:.2f}",
            'Pago': f"R$ {valor_pago:.2f}",
            'Data Pagamento': data_pag
        })
        
        if info['pago']:
            total_pago += valor_pago
        else:
            total_devido += valor_devido
            
    # Processar pagamentos de Convites (caso haja)
    dados_convites = []
    for responsavel, lista_convites in FINANCEIRO['convites'].items():
        for convite in lista_convites:
            if convite['data_jogo'].startswith(ano):
                if apelido == convite['convidado_apelido']:
                    data_jogo = convite['data_jogo']
                    status2 = 'PAGO' if convite['pago'] else 'DEVEDOR'
                    valor_pago2 = 0
                    valor_devido2 = convite['valor_cobrado']
                    
                    if convite['pago']:
                        data_pag2origem = convite['data_pag']
                        data_pag2 = converter_data(data_pag2origem)
                        valor_pago2 += convite['valor_cobrado']
                    else:
                        data_pag2 =  '-'
                        
                    dados_convites.append({
                        'Mês': data_jogo,
                        'Status': status2,
                        'Devido': f"R$ {valor_devido2:.2f}",
                        'Pago': f"R$ {valor_pago2:.2f}",
                        'Data Pagamento': data_pag2
                    })
                    total_pago += valor_pago2
                    
                    if not convite['pago']:
                        total_devido += valor_devido2
                        
    dados_convites.sort(key=lambda x: x['Mês'])
    
    dados_tabela = [{'Mês': '--Mensalidades--', 'Status': '', 'Devido': '', 'Pago': '', 'Data Pagamento': ''}] + dados_mensalidade + [{'Mês': '--Convites--', 'Status': '', 'Devido': '', 'Pago': '', 'Data Pagamento': ''}] + dados_convites
    
    # Gera o PDF
    titulo = f'Pagamentos Individuais de "{apelido}" - {ano}'
    pdf_buffer = criar_pdf_relatorio(titulo, dados_tabela, total_pago, total_devido, 'individual', dados_tabela_gastos, total_gastos, qtd_mensalistas, saldo_ano_anterior)
    
    return pdf_buffer, dados_tabela, total_pago, total_devido, dados_tabela_gastos, total_gastos, qtd_mensalistas, saldo_ano_anterior

def gerar_dados_relatorio_geral(ano, JOGADORES, FINANCEIRO):
    """Calcula os dados do relatório geral (Mensalistas, Ex-mensalistas, Convidados e Gastos Comuns) e retorna os dados e o PDF."""
    
    dados_mensalistas = []
    dados_ex_mensalistas = []
    dados_convidados = []
    
    total_recebido_mensalistas = 0.0
    total_pendente_mensalistas = 0.0
    total_recebido_ex_mensalistas = 0.0
    total_pendente_ex_mensalistas = 0.0
    total_recebido_convidados = 0.0
    total_pendente_convidados = 0.0
    
    saldo_ano_anterior = 0

    # PROCESSAR ANO DESEJADO --
    
    # 1. PROCESSAR MENSALISTAS (Ordenado por Apelido)
    mensalistas, convidados, qtd_mensalistas, c = listas_e_qtd_mensalistas_convidados()

    for apelido in mensalistas:
        dados = JOGADORES[apelido]
        mensalidades_jogador = FINANCEIRO['mensalidades'].get(apelido, {})
        pago_anual = 0.0
        devido_anual = 0.0
        
        datas_pag = []
        
        for mes, info in mensalidades_jogador.items():
            if mes.startswith(ano):
                valor_devido = info.get('valor_devido', 0.0)
                
                if info.get('pago'):
                    valor_pago = info.get('valor_pago', valor_devido)
                    data_efetiva_pag = info.get('data_efetiva', {})
                    datas_pag.append(data_efetiva_pag)
                else:
                    valor_pago = 0.0
                
                if info.get('pago'):
                    pago_anual += valor_pago
                else:
                    devido_anual += valor_devido
        
        if datas_pag != []:
            datas_pag_ordenada = sorted(datas_pag)
            ultima_data_pag = datas_pag_ordenada[-1]
            
            # Converte o formato da data (dia-mês-ano)
            ultima_data_pag = converter_data(ultima_data_pag)
        else:
            ultima_data_pag = '-'

        total_recebido_mensalistas += pago_anual
        total_pendente_mensalistas += devido_anual
        
        dados_mensalistas.append({
            'Apelido': apelido,
            'Posição': dados['posicao'],
            'Última data PG': ultima_data_pag,
            'Pago no ano': f"R$ {pago_anual:.2f}",
            'Devido Pendente': f"R$ {devido_anual:.2f}"
        })
        
    # 2. PROCESSAR EX-MENSALISTAS (Ordenado por Apelido)
    
    for apelido2 in convidados:
        dados2 = JOGADORES[apelido2]
        mensalidades_jogador2 = FINANCEIRO['mensalidades'].get(apelido2, {})
        pago_anual2 = 0.0
        devido_anual2 = 0.0
        
        datas_pag2 = []
        
        for mes2, info2 in mensalidades_jogador2.items():
            if mes2.startswith(ano):
                valor_devido2 = info2.get('valor_devido', 0.0)
                
                if info2.get('pago'):
                    valor_pago2 = info2.get('valor_pago', valor_devido2)
                    data_efetiva_pag2 = info2.get('data_efetiva', {})
                    datas_pag2.append(data_efetiva_pag2)
                else:
                    valor_pago2 = 0.0
                
                if info2.get('pago'):
                    pago_anual2 += valor_pago2
                else:
                    devido_anual2 += valor_devido2
        
        if datas_pag2 != []:
            datas_pag_ordenada2 = sorted(datas_pag2)
            ultima_data_pag2 = datas_pag_ordenada2[-1]
            
            # Converte a data para o formato (dia-mês-ano)
            ultima_data_pag2 = converter_data(ultima_data_pag2)
            
        else:
            ultima_data_pag2 = '-'

        total_recebido_ex_mensalistas += pago_anual2
        total_pendente_ex_mensalistas += devido_anual2
        
        if pago_anual2 > 0:
            dados_ex_mensalistas.append({
                'Apelido': apelido2,
                'Posição': dados2['posicao'],
                'Última data PG': ultima_data_pag2,
                'Pago no ano': f"R$ {pago_anual2:.2f}",
                'Devido Pendente': f"R$ {devido_anual2:.2f}"
            })
        
    # 3. PROCESSAR CONVIDADOS (Nível separado, Ordenado por Apelido)
    # Dicionário temporário para somar os valores de convites por convidado (para evitar duplicatas por responsável)
    convites_sumarizados = {}
    
    for responsavel, lista_convites in FINANCEIRO['convites'].items():
        for convite in lista_convites:
            if convite['data_jogo'].startswith(ano):
                apelido_convidado = convite['convidado_apelido']
                if convite['pago']:
                    valor_convite_pago = convite['valor_cobrado']
                    valor_convite_pendente = 0.0
                else:
                    valor_convite_pago = 0.0
                    valor_convite_pendente = convite['valor_cobrado']
                
                # Assume-se que, no geral, o valor foi pago pelo responsável/convidado
                
                if apelido_convidado not in convites_sumarizados:
                    convites_sumarizados[apelido_convidado] = {
                        'valor_total_pago': 0.0,
                        'valor_total_pendente': 0.0,
                        'posicao': convite['posicao'],
                        'pagamentos': []
                    }
                
                convites_sumarizados[apelido_convidado]['valor_total_pago'] += valor_convite_pago
                convites_sumarizados[apelido_convidado]['valor_total_pendente'] += valor_convite_pendente
    
    # Gera a lista de convidados para o relatório (ordenado por apelido)
    for apelido_convidado in sorted(convites_sumarizados.keys()):
        info = convites_sumarizados[apelido_convidado]
        
        # Contabilizamos como recebido, pois o registro do convite com valor é a receita.
        total_recebido_convidados += info['valor_total_pago']
        total_pendente_convidados += info['valor_total_pendente']
        
        dados_convidados.append({
            'Apelido': apelido_convidado,
            'Posição': info['posicao'],
            'Última data PG': '-',
            'Pago no ano': f"R$ {info['valor_total_pago']:.2f}",
            'Devido Pendente': f"R$ {info['valor_total_pendente']:.2f}"
        })
    
    # Gera os dados dos gastos
    dados_tabela_gastos =[]
    total_gastos = 0
    
    for gasto in FINANCEIRO['gastos_comuns']:
        if gasto['data'].startswith(ano):
            valor = gasto['valor']
            total_gastos += valor
            data_convertida = converter_data(gasto['data'])
            
            dados_tabela_gastos.append({
                'Data do gasto': data_convertida,
                'Descrição': gasto['descricao'],
                'Valor': f"R$ {gasto['valor']:.2f}"
            })
    
    # 3. Geração do PDF e Retorno
    
    dados_tabela = [
        {'Apelido': '--- MENSALISTAS ---', 'Posição': '', 'Pago no ano': '', 'Devido Pendente': '', 'Última data PG': ''}
    ] + dados_mensalistas + [
        {'Apelido': '--- EX-MENSALISTAS ---', 'Posição': '', 'Pago no ano': '', 'Devido Pendente': '', 'Última data PG': ''}
    ] + dados_ex_mensalistas + [
        {'Apelido': '--- CONVIDADOS ---', 'Posição': '', 'Pago no ano': '', 'Devido Pendente': '', 'Última data PG': ''}
    ] + dados_convidados

    total_recebido_geral = total_recebido_mensalistas + total_recebido_ex_mensalistas + total_recebido_convidados
    total_pendente_geral = total_pendente_mensalistas + total_pendente_ex_mensalistas
    
    ## PROCESSAR SALDO ANO ANTERIOR
    
    # 1. Processar pagamentos de mensalidades (ANO ANTERIOR)
    
    ano_anterior = gerar_ano_anterior(ano)
    saldo_ano_anterior = 0
        
    for apelido3 in FINANCEIRO['mensalidades'].keys():
        mensalidades_pagas_jogador3 = 0
        mensalidades_jogador3 = FINANCEIRO['mensalidades'].get(apelido3, {})
        
        if mensalidades_jogador3 != {}:
            for mes3, info3 in mensalidades_jogador3.items():
                mensalidade_paga3 = 0
                if mes3.startswith(ano_anterior):
                    if info3.get('pago'):
                        mensalidade_paga3 += info3.get('valor_pago')
                
                mensalidades_pagas_jogador3 += mensalidade_paga3
        
        saldo_ano_anterior += mensalidades_pagas_jogador3
        
    # 2. Processar pagamentos de convites(ANO ANTERIOR)
    for responsavel, lista_convites2 in FINANCEIRO['convites'].items():
        for convite2 in lista_convites2:
            
            convites_pagos = 0
            if convite2['data_jogo'].startswith(ano_anterior) and convite2['pago']:
                    convites_pagos =+ convite2['valor_cobrado']
            else:
                convites_pagos = 0
        
        saldo_ano_anterior += convites_pagos
    
    # 3. Processar pagamentos do (ANO ANTERIOR)
    for gastos2 in FINANCEIRO['gastos_comuns']:
        gasto_ano_anterior = 0
        if gastos2['data'].startswith(ano_anterior):
            gasto_ano_anterior += gastos2['valor']
        else:
            gasto_ano_anterior = 0
    
        saldo_ano_anterior -= gasto_ano_anterior

    if not dados_tabela:
        return None, None, 0.0, 0.0

    # Gera o PDF
    titulo = f"Pagamentos e Gastos Gerais - {ano}"
    pdf_buffer = criar_pdf_relatorio(titulo, dados_tabela, total_recebido_geral, total_pendente_geral, 'geral', dados_tabela_gastos, total_gastos, qtd_mensalistas, saldo_ano_anterior)

    return pdf_buffer, dados_tabela, total_recebido_geral, total_pendente_geral, dados_tabela_gastos, total_gastos, qtd_mensalistas, saldo_ano_anterior

def gerar_relatorio_ui():

    """Gera relatórios individuais e gerais anuais com opção de exportação em PDF."""
    st.header("📈 Relatórios Anuais de Pagamento")
    
    JOGADORES = st.session_state['jogadores']
    FINANCEIRO = st.session_state['financeiro']
    
    # Colunas para organizar as opções
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Relatório Individual")
        apelido = st.selectbox("Selecione o jogador:", [''] + sorted([k for k, v in JOGADORES.items()]), key="rel_ind_apelido")
        ano_ind = st.text_input("Ano (AAAA):", value=str(datetime.now().year), key="rel_ind_ano")
        
        if st.button("Gerar Individual", key='btn_gerar_ind'):
            if not apelido:
                st.error('O campo apelido não pode ficar vazio')
            
            if apelido and ano_ind:
                # Chama a função de geração de dados e recebe os resultados
                pdf_buffer, dados_tabela, total_pago, total_devido, dados_tabela_gastos, total_gastos, qtd_mensalistas, saldo_ano_anterior = gerar_dados_relatorio_individual(apelido, ano_ind, JOGADORES, FINANCEIRO)
                
                if len(dados_tabela) > 2:
                    st.success(f'Relatório de {ano_ind} para {apelido.upper()} gerado com sucesso!')
                    
                    # Botão de download
                    st.download_button(
                        label="Exportar para PDF",
                        data=pdf_buffer,
                        file_name=f"Relatorio_Individual_{apelido}_{ano_ind}.pdf",
                        mime="application/pdf"
                    )
                    
                    # Apresenta os dados na tela (opcional, mas bom para visualização)
                    df = pd.DataFrame(dados_tabela)
                    st.dataframe(df, use_container_width=True, hide_index=True)
                    st.markdown(f"**Resumo Anual** - Total Pago: R$ {total_pago:.2f} | Total Devido Pendente: R$ {total_devido:.2f}")
                else:
                    st.info("Nenhum dado encontrado para este relatório.")

    with col2:
        st.subheader("Relatório Geral")
        ano_geral = st.text_input("Ano (AAAA):", value=str(datetime.now().year), key="rel_geral_ano")
        ano_anterior = gerar_ano_anterior(ano_geral)
        
        if st.button("Gerar Geral", key='btn_gerar_geral'):
            if ano_geral:
                # Chama a função de geração de dados e recebe os resultados
                pdf_buffer, dados_tabela, total_recebido_geral, total_pendente_geral, dados_tabela_gastos, total_gastos, qtd_mensalistas, saldo_ano_anterior = gerar_dados_relatorio_geral(ano_geral, JOGADORES, FINANCEIRO)
                
                if dados_tabela:
                    st.success(f'Relatório de {ano_geral} gerado com sucesso!')
                    df = pd.DataFrame(dados_tabela)
                    
                    # Apresenta os dados na tela           
                    col_qtd, col_btn = st.columns(2)
                    with col_qtd:
                        st.markdown(f'Quantidade de mensalistas: {qtd_mensalistas}')    
                    with col_btn:
                        # Botão de download
                        st.download_button(
                        label="Exportar para PDF",
                        data=pdf_buffer,
                        file_name=f"Relatorio_Geral_{ano_geral}.pdf",
                        mime="application/pdf"
                        )
                    saldo = total_recebido_geral - total_gastos
                    
                    st.markdown(f"**Resumo Financeiro de {ano_geral}:**")
                    st.markdown(f'Saldo do ano anterior ({ano_anterior}): R$ {saldo_ano_anterior:.2f}')
                    st.markdown(f'Total Recebido: R$ {total_recebido_geral:.2f} - Total Pendente: R$ {total_pendente_geral:.2f}')
                    st.markdown(f'Total Gasto: R$ {total_gastos:.2f} - Saldo ({ano_geral}): R$ {saldo:.2f}')
                    st.markdown(f'Saldo efetivo: R$ {(saldo_ano_anterior + saldo):.2f}')
                    st.dataframe(df, use_container_width=True, hide_index=True)
                else:
                    st.info("Nenhum dado encontrado para este relatório.")

def criar_pdf_relatorio(titulo, dados_tabela, total_pago, total_pendente, tipo_relatorio, dados_tabela_gastos, total_gastos, qtd_mensalistas, saldo_ano_anterior):
    """Gera um PDF em memória (BytesIO) com os dados do relatório."""
    # --- 1. PREPARAR ELEMENTOS DO CABEÇALHO ---
    
    # a) Preparar a Logo
    caminho_logo = 'imgs/logo3.png'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    Story = []
    
    logo_elemento = Spacer(1, 1) # Elemento vazio padrão, caso a logo não exista
    if os.path.exists(caminho_logo):
        # Cria o objeto Image e define seu tamanho fixo
        logo_elemento = Image(caminho_logo, width=3.0 * cm, height=2.5 * cm)
    
    # b) Preparar os Títulos e a Data de Geração
    
    # 1º Título: Relatório Financeiro
    paragrafo_relatorio = Paragraph(f"<b>Relatório Financeiro</b>", styles['Title'])
    
    # 2º Título: Título Específico (Ex: Mensalista X ou Geral)
    paragrafo_titulo = Paragraph(f"<b>{titulo}</b>", styles['Title'])
    
    # Agrupa todos os textos em uma única coluna vertical
    titulo_coluna = [paragrafo_relatorio, paragrafo_titulo]
    
    # --- 2. CRIAR A TABELA DO CABEÇALHO ---
    
    # Define as células da tabela (uma linha, duas colunas)
    cabecalho_data = [
        [logo_elemento, titulo_coluna]
    ]

    # Define as larguras das colunas: 
    # Coluna 1 (Logo): Largura fixa do tamanho da logo.
    # Coluna 2 (Textos): Largura restante (asterisco '*').
    col_widths = [(2.5*cm) + (0.5*cm), '*'] # +0.5 cm para um pequeno espaçamento

    # Cria a tabela de layout (sem bordas)
    cabecalho_tabela = Table(cabecalho_data, colWidths=col_widths, style=[
        ('VALIGN', (0, 0), (-1, -1), 'TOP'), # Alinha todos os elementos ao topo da linha
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),  # Alinha a logo à esquerda
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),  # Alinha o texto à esquerda
    ])
    
    # 3. Adiciona a tabela de cabeçalho ao Story
    Story.append(cabecalho_tabela)
    Story.append(Spacer(1, 18))
    

    # Preparar Dados para Tabela (ReportLab)
    
    # 1. Definir Cabeçalho e Colunas
    if tipo_relatorio == 'individual':
        headers = ['Mês / Data-Jogo', 'Status', 'Devido', 'Pago', 'Data Pagamento']
        data = [headers] + [[d['Mês'], d['Status'], d['Devido'], d['Pago'], d['Data Pagamento']] for d in dados_tabela]
    else: # Geral
        headers = ['Apelido', 'Posição', 'Pago no Ano', 'Devido Pendente', 'Último pagamento']
        data = [headers] + [[d['Apelido'], d['Posição'], d['Pago no ano'], d['Devido Pendente'], d['Última data PG']] for d in dados_tabela]
    
        # Tabela de gastos
        if dados_tabela_gastos != []:
            headers2 = ['Data do gasto', 'Descrição', 'Valor']
            data2 = [headers2] + [[a['Data do gasto'], a['Descrição'], a['Valor']] for a in dados_tabela_gastos]
        else:
            data2 = []

    # 
    # 2. Configurar Estilo da Tabela
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]
    if tipo_relatorio != 'individual':
        Story.append(Paragraph(f"<b>Mensalistas: {qtd_mensalistas} atletas</b>", styles['Normal']))
        Story.append(Spacer(1, 8))
        
    # Resumo
    Story.append(Paragraph(f"<b>RESUMO FINANCEIRO</b>", styles['h3']))
    Story.append(Paragraph(f"Total Arrecadado: <b>R$ {total_pago:.2f}</b> - Total Pendente: <b>R$ {total_pendente:.2f}</b>", styles['Normal']))
    Story.append(Spacer(1, 8))
    
    if tipo_relatorio == 'geral':
        Story.append(Paragraph(f"Total de Gastos: <b>R$ {total_gastos:.2f}</b> - Saldo corrente: <b>R$ {(total_pago - total_gastos):.2f}</b> - Saldo ano anterior: <b>R$ {saldo_ano_anterior:.2f}</b>", styles['Normal']))
        Story.append(Paragraph(f"Saldo final(em caixa): <b>R$ {(total_pago - total_gastos + saldo_ano_anterior):.2f}</b>", styles['Normal']))
        Story.append(Spacer(1, 8))
    
    # Listas dos mensalistas, ex-mensalitas e convidados
    Story.append(Paragraph(f"<b>MENSALIDADES E CONVITES:</b>", styles['Normal']))
        
    Story.append(Spacer(1, 12))
    t = Table(data, style=table_style)
    Story.append(t)
    Story.append(Spacer(1, 18))
    
    # Story.append(PageBreak()) - QUEBRA DE PÁGINA
    if tipo_relatorio == 'geral' and data2 != []:
        Story.append(Paragraph(f"<b>GASTOS COMUNS DO GRUPO:</b>", styles['Normal']))
        Story.append(Spacer(1, 12))
        t2 = Table(data2, style=table_style)
        Story.append(t2)
        Story.append(Spacer(1, 18))
        
    # Data de Geração
    dia_geracao = datetime.now().strftime("%d/%m/%Y")
    hora_geracao = datetime.now().strftime("%H:%M:%S")
    Story.append(Paragraph(f"<i>Relatório gerado em: {dia_geracao} às {hora_geracao}.</i>", styles['Normal']))

    doc.build(Story)
    buffer.seek(0)
    return buffer
