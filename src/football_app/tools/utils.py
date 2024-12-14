import yaml
import numpy as np


def save_dict_as_yaml(data: dict, filepath: str):
    """
    Salva um dicionário como um arquivo YAML, convertendo valores NumPy para tipos nativos do Python.

    Args:
        data (dict): O dicionário a ser salvo.
        filepath (str): O caminho completo do arquivo YAML onde os dados serão salvos.
    """
    def convert_numpy_to_native(obj):
        """
        Converte tipos NumPy em tipos nativos do Python de forma recursiva.
        """
        if isinstance(obj, dict):
            return {key: convert_numpy_to_native(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_numpy_to_native(element) for element in obj]
        elif isinstance(obj, np.integer):  # Verifica números inteiros do NumPy
            return int(obj)
        elif isinstance(obj, np.floating):  # Verifica números de ponto flutuante do NumPy
            return float(obj)
        elif isinstance(obj, np.ndarray):  # Verifica arrays NumPy
            return obj.tolist()
        return obj

    # Converte os valores NumPy para tipos nativos
    cleaned_data = convert_numpy_to_native(data)
    
    # Salva o YAML preservando os caracteres UTF-8
    with open(filepath, 'w', encoding='utf-8') as f:
        yaml.dump(
            cleaned_data,
            f,
            default_flow_style=False,
            allow_unicode=True  # Garante que caracteres UTF-8 sejam preservados
        )