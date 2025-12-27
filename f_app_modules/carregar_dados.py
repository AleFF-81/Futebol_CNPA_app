import json

def carregar_dados(nome_arquivo):
    """Carrega dados de um arquivo JSON. Retorna um dicionário vazio se o arquivo não existir."""
    try:
        with open(nome_arquivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
