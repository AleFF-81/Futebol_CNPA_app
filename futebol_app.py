import streamlit as st
import bcrypt as bc
from datetime import datetime
from f_app_modules import (
    variaveis,
    adicionar_jogador_ui, alterar_dados_jogador_ui, listas_e_qtd_mensalistas_convidados, listar_jogadores_ui, salvar_dados, registrar_pagamento_mensalidade_ui, registrar_pagamento_convite_ui,
    calcular_geral_ui, editar_estatisticas_sumula_ui, exibir_estatistica_anual,
    criar_sumula_simples_ui, cadastrar_jogadores_na_sumula_ui,
    gerar_relatorio_ui,
    registrar_gasto_comum_ui, listar_gastos_comuns_ui,
    alterar_config_financeira_ui,
    carregar_dados,
    sidebar_logo
)

#--- VARIÁVEIS DE CONFIGURAÇÃO (Constantes) ---
ARQUIVO_DADOS_JOGADORES, ARQUIVO_DADOS_FINANCEIRO, ARQUIVO_DADOS_SUMULAS, ARQUIVO_DADOS_USUARIOS = variaveis()

def inicializar_estado():
    # Trecho de FUNÇÕES DE PERSISTÊNCIA e INICIALIZAÇÃO DE ESTADO
    
    # 1. Carrega Jogadores
    if 'jogadores' not in st.session_state:
        st.session_state['jogadores'] = carregar_dados(ARQUIVO_DADOS_JOGADORES)
        
    # 2. Carrega Financeiro
    if 'financeiro' not in st.session_state:
        FINANCEIRO = carregar_dados(ARQUIVO_DADOS_FINANCEIRO)
        
        if 'mensalidades' not in FINANCEIRO:
            FINANCEIRO['mensalidades'] = {}
        if 'gastos_comuns' not in FINANCEIRO:
            FINANCEIRO['gastos_comuns'] = []
        if 'convites' not in FINANCEIRO:
            FINANCEIRO['convites'] = {}
            
        if 'config' not in FINANCEIRO:
            VALOR_MENSALIDADE_ATUAL = 20.00
            VALOR_CONVITE_ATUAL = 10.00
            DATA_ALT_MENSALIDADE = datetime.now().strftime("%Y-%m-%d")
            DATA_ALT_CONVITE = datetime.now().strftime("%Y-%m-%d")
            
            FINANCEIRO['config'] = {
                'mensalidade_atual': VALOR_MENSALIDADE_ATUAL, 
                'valor_convite_atual': VALOR_CONVITE_ATUAL, 
                'data_alt_mensalidade': DATA_ALT_MENSALIDADE,
                'data_alt_convite': DATA_ALT_CONVITE
            }
            
        st.session_state['financeiro'] = FINANCEIRO
        
    # 3. 🆕 Carrega Súmulas
    if 'sumulas' not in st.session_state:
        st.session_state['sumulas'] = carregar_dados(ARQUIVO_DADOS_SUMULAS)
    
    # 4. Carrega Usuários
    if 'usuarios' not in st.session_state:
        st.session_state['usuarios'] = carregar_dados(ARQUIVO_DADOS_USUARIOS)

def login_page():
    if 'usuarios' not in st.session_state:
        st.session_state['usuarios'] = carregar_dados(ARQUIVO_DADOS_USUARIOS)
    
    USUARIOS = st.session_state['usuarios']
    
    # Inicializa o estado de autenticação se ainda não existir
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
        st.session_state['username'] = None
        
    if st.session_state['authenticated']:
        # Se autenticado, chama a aplicação principal
        main_app() 
        return

    # --- 3. TELA DE LOGIN (Executado apenas se 'authenticated' for False)
    if not USUARIOS:
        senha_admin = gerar_hash_senha('admin')
        USUARIOS['admin'] = {
            'senha': senha_admin
        }
        
        salvar_dados(USUARIOS, ARQUIVO_DADOS_USUARIOS)
        st.success('Parabéns! Esse é seu primeiro acesso ao sistema. Entre com o usuário: Admin e senha: admin')
        
    sidebar_logo()
    st.markdown('---')
    col_esq, col_meio, col_dir = st.columns([1, 2, 1])
    with col_meio:
        with st.form("login_form", width=500):
            st.subheader(":closed_lock_with_key: Login de usuário")
            username = st.text_input("Usuário: ").lower()
            password = st.text_input("Senha:", type="password")
            submitted = st.form_submit_button("Entrar")

            if submitted:
                if username in USUARIOS:
                    senha_armazenada = USUARIOS[username]['senha']
                    
                    if verificar_senha(password, senha_armazenada):
                                        
                    # Credenciais válidas: Atualiza o estado
                        st.session_state['authenticated'] = True
                        st.session_state['username'] = username
                        st.success(f"Bem-vindo(a), {username}!")
                    
                        # Força a reexecução para carregar a main_app
                        st.rerun() 
                    else:
                        st.error("Usuário ou senha inválidos.")
                else:
                    st.error("Usuário ou senha inválidos.")

def gerar_hash_senha(senha_pura):
    # O bcrypt.gensalt() gera um "salt" (valor aleatório) que garante que duas senhas 
    # idênticas tenham hashes diferentes, aumentando a segurança.
    salt = bc.gensalt()
    
    # O hash é gerado com a senha pura e o salt
    senha_hasheada = bc.hashpw(senha_pura.encode('utf-8'), salt)
    
    # Armazene o resultado em string para JSON ou dicionário
    return senha_hasheada.decode('utf-8')

def verificar_senha(senha_pura, hash_armazenada):
    # A senha pura e a hash armazenada devem ser codificadas de volta para bytes
    return bc.checkpw(senha_pura.encode('utf-8'), hash_armazenada.encode('utf-8'))

def main_app():
    ### Define a interface e o roteamento da aplicação Streamlit.
    # Chama a função para garantir que os dados estão carregados no st.session_state
    inicializar_estado() 
    
    st.set_page_config(layout="wide", page_title="Amigos do CNPA", page_icon='⚽')
    
    # --- MENU LATERAL (Sidebar) ---
    usuario = str(st.session_state['username']).title()
    
    sidebar_logo()
    with st.sidebar:
        #st.markdown('---')
        
        col_usu, col_bv = st.columns([1,6])
        with col_usu:
            st.image('imgs/usuario.png')
        with col_bv:
            st.markdown(f' ***{usuario}***')   
            
    
    menu_selecionado = st.sidebar.radio(
        "",
        [
            "🏠 Dashboard",
            "🤝 Cadastro de Jogadores",
            "💲 Mensalidades e Convites",
            "⚽ Súmulas e Estatísticas",
            "📈 Relatórios Financeiros",
            "💸 Controle de gasto comum",
            "⚙️ Configurações"
        ]
    )
    #st.sidebar.markdown('---')
    st.sidebar.button("Sair do sistema", on_click=logout)
    
    # Roteamento
    if menu_selecionado == "🏠 Dashboard":
        st.header("🏠 Dashboard")
        st.markdown("---")
        calcular_geral_ui()
        
        
    elif menu_selecionado == "🤝 Cadastro de Jogadores":
        st.header('📋 CADASTRO DE JOGADORES', anchor='lista_jogadores')
        col1, col2 = st.columns([1, 3]) # links de atalhos para CADASTRAR e ALTERAR dados dos jogadores
        with col1:
            st.markdown("[Cadastrar Jogador](#cadastrar-jogador)")
        with col2:
            st.markdown("[Alterar dados do Jogador](#alterar-jogador)")
        
        st.subheader("Jogadores cadastrados, estatísticas globais e status financeiro")
        a, b, qtd_mensalistas, qtd_convidados = listas_e_qtd_mensalistas_convidados()
        st.markdown(f'Mensalista(s): {qtd_mensalistas} | Convidado(s): {qtd_convidados}')
        
        listar_jogadores_ui('cadastro')
        col_cad, col_list = st.columns(2)
        with col_cad:
            adicionar_jogador_ui()
        with col_list:
            alterar_dados_jogador_ui()
        
    elif menu_selecionado == "💲 Mensalidades e Convites":
        col_mens, col_conv = st.columns(2)
        with col_mens:
            registrar_pagamento_mensalidade_ui()
        with col_conv:
            registrar_pagamento_convite_ui()
        
    elif menu_selecionado == "⚽ Súmulas e Estatísticas":
        st.header("⚽ Súmulas e Estatísticas")
        st.markdown("---")
        col1, col2 = st.columns([1, 3])
        with col1:
            criar_sumula_simples_ui()
        
        with col2:
            cadastrar_jogadores_na_sumula_ui()
        st.markdown("---")
        st.subheader("📊 ETATÍSTICAS")
        col_d, col_g = st.columns(2)
        with col_d:
            st.subheader(':calendar: Por partida')
            editar_estatisticas_sumula_ui()
        with col_g:
            st.subheader(':calendar: Anual')
            exibir_estatistica_anual()
            
        st.subheader(':globe_with_meridians: Globais')
        listar_jogadores_ui('estatisticas')

    elif menu_selecionado == "📈 Relatórios Financeiros":
        gerar_relatorio_ui()
    
    elif menu_selecionado == "💸 Controle de gasto comum":
        col1, col2 = st.columns(2)
        with col1:
            registrar_gasto_comum_ui()
        with col2:

            listar_gastos_comuns_ui()
    elif menu_selecionado == "⚙️ Configurações":
        alterar_config_financeira_ui()

def logout():
    st.session_state['authenticated'] = False
    st.session_state['username'] = None
    
if __name__ == "__main__":
    login_page()