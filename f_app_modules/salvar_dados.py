import json

def salvar_dados(dados, nome_arquivo):
    """Salva dados em um arquivo JSON e exibe feedback no Streamlit."""
    with open(nome_arquivo, 'w', encoding='utf-8') as f:
        json.dump(dados, f, indent=4)
    # if nome_arquivo != ARQUIVO_DADOS_USUARIOS:
    #     st.sidebar.success(f"✅ Dados salvos em '{nome_arquivo}'.")