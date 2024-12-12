from statsbombpy import sb
import json
from copy import copy
import pandas as pd


# Retorna uma string JSON formatada de um DataFrame
def to_json(df: pd.DataFrame) -> str:
    return json.dumps(df, indent=2)


# Obtém as escalações de uma partida específica usando sb.lineups, processa os dados, e retorna um JSON
def get_lineups(match_id: int) -> str:
    data = sb.lineups(match_id=match_id)
    data_final = copy(data)
    list_fields = ['cards', 'positions']
    for field in list_fields:
        for key, df in data.items():
            df[field] = df[field].apply(lambda v: {field: v})
            data_final[key] = df.to_dict(orient='records')
    return to_json(data_final)