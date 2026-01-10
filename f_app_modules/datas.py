from datetime import datetime

def converter_data(data):
    # Converte a data para ao formato (dia-mês-ano)
    
    # Define o formato de entrada (strptime)
    data_origem = datetime.strptime(data, '%Y-%m-%d')

    # Define o formato de saída (strftime)
    data_convertida = data_origem.strftime('%d-%m-%Y')
    return data_convertida

def reverter_data(data):
    # Reverte a data para ao formato (ano-mês-dia)
    
    # Define o formato de entrada (strptime)
    data_origem2 = datetime.strptime(data, '%d-%m-%Y')
    
    # Define o formato de saída
    data_revertida = data_origem2.strftime('%Y-%m-%d')
    return data_revertida

def gerar_ano_anterior(ano):
    ano_anterior = str(int(ano)-1)
    return ano_anterior
