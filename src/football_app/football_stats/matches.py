from statsbombpy import sb
import json
from copy import copy
import pandas as pd
import numpy as np


# Retorna uma string JSON formatada de um DataFrame
def to_json(df: pd.DataFrame) -> str:
    return json.dumps(df, indent=2)


class PlayerStatsError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


def get_player_stats(match_id, player_name) -> str:
    """
    Returns the consolidated statistics of a specific player in a match.

    Parameters:
        match_id (int): ID of the match (provided by StatsBomb).
        player_name (str): Full name of the player.

    Returns:
        dict: Consolidated statistics of the player.

    Raises:
        PlayerStatsError: If any issue occurs while fetching or calculating the statistics.
    """
    try:
        # Load match events
        events = sb.events(match_id=match_id)
        
        # Validate if events were loaded
        if events.empty:
            raise PlayerStatsError(f"No events found for the match with ID {match_id}.")

        # Filter events for the specific player
        player_events = events[events['player'] == player_name]
        
        # Check if the player is present in the events
        if player_events.empty:
            raise PlayerStatsError(f"No events found for player '{player_name}' in match {match_id}.")

        # Consolidate statistics
        stats = {
            "player_name": player_name,
            "passes_completed": player_events[(player_events['type'] == 'Pass') & (player_events['pass_outcome'].isna())].shape[0],
            "passes_attempted": player_events[player_events['type'] == 'Pass'].shape[0],
            "shots": player_events[player_events['type'] == 'Shot'].shape[0],
            "shots_on_target": player_events[(player_events['type'] == 'Shot') & (player_events['shot_outcome'] == 'On Target')].shape[0],
            "fouls_committed": player_events[player_events['type'] == 'Foul Committed'].shape[0],
            "fouls_won": player_events[player_events['type'] == 'Foul Won'].shape[0],
            "tackles": player_events[player_events['type'] == 'Tackle'].shape[0],
            "interceptions": player_events[player_events['type'] == 'Interception'].shape[0],
            "dribbles_successful": player_events[(player_events['type'] == 'Dribble') & (player_events['dribble_outcome'] == 'Complete')].shape[0],
            "dribbles_attempted": player_events[player_events['type'] == 'Dribble'].shape[0],
        }
        
    except PlayerStatsError as e:
        # Propagate the error message
        raise PlayerStatsError(e.message)
    except Exception as e:
        # Handle any other unexpected error
        raise PlayerStatsError(f"An unexpected error occurred: {str(e)}")
    
    return to_json(stats)


def return_overview_events_goals(match_id: int) -> pd.DataFrame():
    
    # Obtém os eventos como string JSON
    eventos_json_str = get_events(match_id)

    # # Salva os eventos em um arquivo JSON
    # with open('eventos.json', 'w') as f:
    #     f.write(eventos_json_str)

    # Converte a string JSON para um objeto Python (lista de dicionários)
    eventos_parsed = json.loads(eventos_json_str)

    # Carrega os eventos em um DataFrame
    df_eventos = pd.read_json(eventos_json_str)

    # Filtra os eventos para apenas os chutes que resultaram em gol
    df_eventos = df_eventos[
        df_eventos['shot'].apply(
            lambda x: x.get('outcome', {}).get('name') == 'Goal' 
            if isinstance(x, dict) else False
        )
    ]

    # Extrai o ID do passe-chave (assistência)
    df_eventos['assistent'] = df_eventos['shot'].apply(
        lambda x: x.get('key_pass_id', None) if isinstance(x, dict) else None
    )

    # Aplica a função para obter o jogador assistente
    df_eventos['key_pass_player'] = df_eventos['assistent'].apply(
        lambda x: find_key_pass_player(x, eventos_parsed)
    )
    
    # ['minute','team','player','key_pass_player']
    events_list = []
    for _, row in df_eventos.iterrows():
        dict_event = {
            # 'minute': row['minute'],
            'team': row['team'],
            'player': row['player'],
            'key_pass_player': row['key_pass_player']
        }
        events_list.append(dict_event)
    
    return df_eventos, events_list


def get_cards_overview(match):
    # Filtra os eventos para cartões amarelos e vermelhos
    # Obtém os eventos como string JSON
    eventos_json_str = get_events(match)

    # # Salva os eventos em um arquivo JSON
    # with open('eventos.json', 'w') as f:
    #     f.write(eventos_json_str)

    # Converte a string JSON para um objeto Python (lista de dicionários)
    eventos_parsed = json.loads(eventos_json_str)
    
    eventos_cartoes = [
        evento for evento in eventos_parsed
        if isinstance(evento.get('foul_committed'), dict) and 
        evento['foul_committed'].get('card', {}).get('name') in ['Yellow Card', 'Red Card']
    ]

    # Cria um DataFrame para os cartões
    df_eventos_cartoes = pd.DataFrame(eventos_cartoes)

    # Extrai o nome do cartão
    df_eventos_cartoes['card_name'] = df_eventos_cartoes['foul_committed'].apply(
        lambda x: x['card']['name'] if isinstance(x, dict) else None
    )

    # Exibe os cartões
    # display(df_eventos_cartoes[['minute', 'team', 'player', 'card_name']])
    
    # Cria dicionário com os cartões ['minute', 'team', 'player', 'card_name']
    cards_list = []
    for _, row in df_eventos_cartoes.iterrows():
        dict_cartoes = {
            'card': {
                # 'minute': row['minute'],
                'team': row['team'],
                'player': row['player'],
                'card_name': row['card_name']
            }
        }        
        cards_list.append(dict_cartoes)
    
    return df_eventos_cartoes, cards_list


# Função para encontrar o jogador que fez o passe-chave
def find_key_pass_player(pass_id, eventos):
    if not pass_id:
        return None
    for evento in eventos:
        if evento.get('id') == pass_id:
            return evento.get('player')
    return None


def process_match_lineups(match_id):
    """Extrai e processa as escalações da partida, retornando um DataFrame"""
    try:
        # Obtendo a formação
        lineups_data = get_lineups(match_id)
        
        # Convertendo o JSON para dicionário
        lineups_dict = json.loads(lineups_data)
        
        # Verificando as equipes
        if len(lineups_dict) != 2:
            raise ValueError("Esperado apenas 2 equipes na formação da partida.")
        
        # Extraindo as equipes
        team_a_name, team_b_name = lineups_dict.keys()
        team_a_players = lineups_dict[team_a_name]
        team_b_players = lineups_dict[team_b_name]
        
        # Convertendo os jogadores para DataFrame
        df_team_a = pd.DataFrame(team_a_players)
        df_team_b = pd.DataFrame(team_b_players)
        
        # Concatenando as duas equipes
        df_players = pd.concat([df_team_a, df_team_b], ignore_index=True)
        
        # Selecionando apenas as colunas relevantes
        df_players = df_players[['player_name', 'player_id']]
        
        return df_players
    
    except Exception as e:
        print(f"Erro ao obter ou processar as escalações: {e}")
        return pd.DataFrame()  # Retorna um DataFrame vazio em caso de erro


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

def get_events(match_id: int) -> str:
    events = sb.events(match_id=match_id, split=True, flatten_attrs=False)
    full_events = pd.concat([v for _, v in events.items()])
    return to_json([
        {k: v for k, v in event.items() if v is not np.nan} 
        for event in full_events.sort_values(by="minute").to_dict(orient='records')
    ])

