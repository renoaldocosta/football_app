from statsbombpy import sb  # type: ignore
from langchain.tools import BaseTool
import json
import os
from langchain_google_genai import GoogleGenerativeAI
import yaml
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv
import pandas as pd
from langchain.tools import tool
from collections import defaultdict

from football_stats.matches import return_overview_events_goals, get_cards_overview
from football_stats.competitions import get_matches
from football_stats.matches import get_lineups
# src\football_app\football_stats\matches.py
load_dotenv()


@tool
def get_match_details(action_input:str) -> str:
    """
    Get the details of a specific match 
    
    Args:
        - action_input(str): The input data containing the match_id.
          format: {
              "match_id": 12345
              "competition_id": 123,
                "season_id": 02
            }
    """
    return yaml.dump(retrieve_match_details(action_input))

def get_all_action_types(match_id):
    raw_data = sb.events(match_id=match_id, fmt="dict")
    
    action_types = set()  # Usar um set para evitar duplicatas

    # Iterar pelos eventos da partida
    for key, event in raw_data.items():
        try:
            # Captura o nome do tipo de jogada
            action_type = event["type"]["name"]
            action_types.add(action_type)  # Adiciona ao conjunto
        except KeyError:
            pass  # Ignora eventos incompletos

    message = "Tipos de jogadas encontrados na partida:\n"
    message = ""
    for action in action_types:
        message += f"- {action}\n"
    # return list(action_types)  # Retorna como lista
    return message
    

@tool
def top_players_by_pass(action_input: str) -> str:
    """
    Get the players with the most passes in a specific match.
    
    Args:
        - action_input(str): The input data containing the match_id.
            format: {
                "match_id": 12345
            }
    """
    try:
        input_data = json.loads(action_input)
        match_id = input_data.get("match_id")
        if not match_id:
            return "Error: 'match_id' not provided in the input."
    except json.JSONDecodeError:
        return "Error: Invalid JSON format for action_input."

    action_type_filter = "Pass"
    raw_data = sb.events(match_id=match_id, fmt="dict")

    # Dictionary to count actions per player
    player_action_count = defaultdict(int)

    # Iterate through the data and filter by action type
    for key in raw_data.keys():
        dicionario = raw_data[key]
        try:
            player_name = dicionario["player"]["name"]
            action_type = dicionario["type"]["name"]

            if action_type == action_type_filter:
                player_action_count[player_name] += 1
        except KeyError:
            pass  # Ignore incomplete data

    if not player_action_count:
        return f"No actions of type '{action_type_filter}' found for match ID {match_id}."

    # Find the maximum number of actions
    max_actions = max(player_action_count.values())

    # Get all players with the maximum number of actions
    top_players = [
        player for player, count in player_action_count.items() if count == max_actions
    ]

    message = f"Players with the most '{action_type_filter}' actions:\n"
    for player in top_players:
        message += f"Player: {player} | Number of Actions: {max_actions}\n"
    return message


# class TopPlayersByActionTool(BaseTool):
#     name = "top_players_by_action"
#     description = "Retorna os jogadores com mais ações de um tipo específico em uma partida."

#     def _run(self, tool_input: str):
#         # Parse o input, por exemplo, usando JSON
#         import json
#         params = json.loads(tool_input)
#         match_id = params.get("match_id")
#         action_type_filter = params.get("action_type_filter")
        
#         # Aqui você incluiria a lógica da sua função original
#         raw_data = sb.events(match_id=match_id, fmt="dict")
#         player_action_count = defaultdict(int)
        
#         for key in raw_data.keys():
#             dicionario = raw_data[key]
#             try:
#                 player_name = dicionario["player"]["name"]
#                 action_type = dicionario["type"]["name"]

#                 if action_type == action_type_filter:
#                     player_action_count[player_name] += 1
#             except KeyError:
#                 pass

#         max_actions = max(player_action_count.values(), default=0)
#         top_players = [player for player, count in player_action_count.items() if count == max_actions]

#         message = f"Jogadores com mais ações do tipo '{action_type_filter}':"
#         for player in top_players:
#             message += f"\nJogador: {player} | Quantidade de Ações: {max_actions}"
#         return message

#     async def _arun(self, tool_input: str):
#         raise NotImplementedError("Este método não está implementado.")



# Função para retornar jogadores com mais ações de um tipo específico
# @tool
# def top_players_by_action(match_id, action_type_filter):
#     """
#     Retorna os jogadores com mais ações de um determinado tipo em uma partida.
#     Args:
#         match_id (int): O ID da partida.
#         action_type_filter (str): O tipo de ação a ser filtrada (por exemplo, "Pass", "Shot").
#     Returns:
#         str: Uma mensagem contendo os jogadores com mais ações do tipo especificado e a quantidade de ações.
#     Exceções:
#         KeyError: Ignora dados incompletos que não possuem as chaves esperadas.
#     """
    
#     raw_data = sb.events(match_id=match_id, fmt="dict")
    
#     # Dicionário para contar as ações por jogador
#     player_action_count = defaultdict(int)

#     # Iterar pelos dados e filtrar pelo tipo de jogada
#     for key in raw_data.keys():
#         dicionario = raw_data[key]
#         try:
#             player_name = dicionario["player"]["name"]
#             action_type = dicionario["type"]["name"]

#             # Verifica se o tipo de jogada corresponde ao filtro
#             if action_type == action_type_filter:
#                 player_action_count[player_name] += 1
#         except KeyError:
#             pass  # Ignora dados incompletos

#     # Encontrar a maior contagem de ações
#     max_actions = max(player_action_count.values(), default=0)

#     # Filtrar jogadores com a contagem máxima
#     top_players = [player for player, count in player_action_count.items() if count == max_actions]

#     message = ""
#     # return list(action_types)  # Retorna como lista
#     message = f"Jogadores com mais ações do tipo '{action_type_filter}':"
#     for player in top_players:
#         message += f"\nJogador: {player} | Quantidade de Ações: {max_actions}"
#     return message

# Função para obter o prompt baseado no estilo escolhido
def get_prompt(style):
    """
    Retrieves the prompt string based on the given style.
    
    Args:
        style (str): The style of the prompt (e.g., 'formal', 'humoristico', 'tecnico').
    
    Returns:
        str: The prompt string corresponding to the selected style.
    """
    # Load the YAML file
    with open('./data/commentary_prompts.yaml', 'r', encoding='utf-8') as file:
        prompts = yaml.safe_load(file)
    
    # Retrieve the selected style's dictionary; default to 'padrao' if not found
    selected_style = prompts['commentary_prompts'].get(style, prompts['commentary_prompts']['padrao'])
    
    # Extract and return the 'prompt' string
    return selected_style['prompt']


def get_match_summary(match_id):
    general_data_match, match_overview = get_match_overview(match_id)

    # Obtém os principais eventos da partida
    df_goal, goal_list = return_overview_events_goals(match_id)

    # Obtém os cartões da partida
    df_eventos_cartoes,list_cartoes = get_cards_overview(match_id)
    # # save_dict_as_yaml(match_overview, game_overview_path)
    # # save_dict_as_yaml(goal_list, goals_path)
    # # save_dict_as_yaml(list_cartoes, cards_path)
    
    match_overview_yaml = yaml.dump(match_overview)
    goals_yaml = yaml.dump(goal_list)
    cards_yaml = yaml.dump(list_cartoes)


    # with open(game_overview_path, 'r') as f:
    #     game_overview = f.read()
    # with open(goals_path, 'r', encoding='UTF-8') as f:
    #     goals = f.read()
    # with open(cards_path, 'r') as f:
    #     cards = f.read()

    prompt = f"""
    You are a sports commentator with expertise in football (soccer). Respond as
        if you are delivering an speed summary for a TV audience. Here is the
        information to include:

        Instructions:
        1. Game Overview:
            - Mention the teams that played the match.
            - Provide the final score.
        2. Goals:
            - Mention the playeres who made the goal.
            - Mention who assisted the goal.
        3. Cards:
            - Mention the players who received a card.
            - Mention the type of card.
        
        The Game Overview are provided by the provided as follow: 
        {match_overview_yaml}
        
        The players who scored the goals, the players who assisted the goals and the teams that the players are playing are provided here:
        {goals_yaml}
        
        The cards, players and the teams that the players are playing are provided here:
        {cards_yaml}
        
        Provide the clear and friendly commentary with this <FORMAT>:
        
        "O time A venceu o time B por 2 a 0. Os destaques foram os gols de João e Lucas, além de uma assistência de Ana. O jogador do time B, Pedro, recebeu um cartão amarelo."
        
        Atention:
        - Mention every goal and card and the teams that the players are playing.
        - Respond in portuguese-BR
        """
    
    llm = GoogleGenerativeAI(model="gemini-pro")
    summary_match_result = llm.invoke(prompt)
    return summary_match_result

def get_match_details_match_id(match_id: int) -> dict:
    """
    Get the details of a specific match using the match ID.
    Args:
        match_id (int): The unique identifier of the match.
        
    Returns:
        dict: The details of the match.
    """
    raw_data = sb.events(match_id=match_id, fmt="dict")
    return raw_data


# Salva dados das partidas da Copa do Mundo FIFA em um arquivo parquet ou lê o arquivo parquet se ele já existir.
def get_matches_fifa_world_cup():
    if 'matches_fifa_world_cup.parquet' in os.listdir("./data/"):
            return pd.read_parquet('./data/matches_fifa_world_cup.parquet')

    competition_name = 'FIFA World Cup'
    df = sb.competitions()
    season_id = df[df['competition_name'] == competition_name]['season_id'].to_list()
    competition_id = df[df['competition_name'] == 'FIFA World Cup']['competition_id'].to_list()[0]
    matches = []
    for id in season_id:
            df = sb.matches(competition_id, id)
            df['competition_id'] = competition_id
            df['season_id'] = id
            matches.append(df) # [['match_id','home_team', 'away_team', 'home_score', 'away_score']])

    df_matches = pd.concat(matches)
    
    df_matches.to_parquet('./data/matches_fifa_world_cup.parquet')
    
    return df_matches


# Retorna os detalhes de uma partida específica, utilizando o match_id.
def get_raw_data_match(match_id):
    # df = pd.read_parquet('matches_ids.parquet')
    df = get_matches_fifa_world_cup()
    competition_id, season_id, matches_id = df[df['match_id'] == match_id][['competition_id', 'season_id', 'match_id']].values[0]
    dict_match = sb.matches(competition_id, season_id, matches_id)
    return dict_match[match_id]

def get_match_overview(match_id):
    df = get_matches_fifa_world_cup()
    df = df[df['match_id'] == match_id]
    general_data_match = df[['match_id', 'home_team', 'away_team', 'home_score', 'away_score', 'competition_id', 'season_id']]
    # return df_eventos_cartoes, cards_list
    for _, row in general_data_match.iterrows():
        match_dict = {
            'home_team': row['home_team'],
            'away_team': row['away_team'],
            'home_score': row['home_score'],
            'away_score': row['away_score'],
        }
    return general_data_match, match_dict

# Processa o JSON de lineups, extraindo apenas os jogadores titulares.
def filter_starting_xi(line_ups: str) -> dict:
    """
    Filter the starting XI players from the provided lineups.
    
    Args:
        line_ups (str): The JSON string containing the lineups of the teams.
        
    Returns:
    
    """
    line_ups_dict = json.loads(line_ups)
    filter_starting_xi =  {}
    for team, team_line_up in line_ups_dict.items():
        filter_starting_xi[team] = []
        for player in sorted(team_line_up, key= lambda x: x["jersey_number"]):
            try:
                positions = player["positions"]["positions"]
                if positions[0].get("start_reason") == "Starting XI":
                    filter_starting_xi[team].append({
                        "player": player["player_name"],
                        "position": positions[0].get('position'),
                        "jersey_number": player["jersey_number"]
                    })
            except (KeyError, IndexError):
                continue
    return filter_starting_xi


# Gera comentários especializados sobre a partida, utilizando LLMChain com o modelo GoogleGenerativeAI
def get_sport_specialist_comments_about_match(match_details: str, line_ups: str, prompt_style) -> str:
    """
    Returns the comments of a sports specialist about a specific match.
    The comments are generated based on match details and lineups.
    """
    
    line_ups = filter_starting_xi(line_ups)
    
    # agent_prompt = """
    # You are a sports commentator with expertise in football (soccer). Respond as
    # if you are delivering an engaging analysis for a TV audience. Here is the
    # information to include:

    # Instructions:
    # 1. Game Overview:
    #     - Describe the importance of the game (league match, knockout, rivalry, etc.).
    #     - Specify when and where the game took place.
    #     - Provide the final result.
    # 3. Analysis of the Starting XI:
    #     - Evaluate the starting lineups for both teams.
    #     - Highlight key players and their roles.
    #     - Mention any surprising decisions or notable absences.
    # 3.  Contextual Insights:
    #     - Explain the broader implications of the match (rivalry, league standings, or storylines).
    # 4. Engaging Delivery:
    #     - Use a lively, professional, and insightful tone, making the commentary
    #     appealing to fans of all knowledge levels.
    
    # The match details are provided by the provided as follow: 
    # {match_details}
    
    # The team lineups are provided here:
    # {lineups}
    
    # Provide the expert commentary on the match as you are in a sports broadcast.
    # Start your analysis now and engage the audience with your insights.
    
    # Say: "Hello everyone, I've watched to the match between [Home Team] and [Away Team]..."
    # """
    agent_prompt = get_prompt(prompt_style)
    
    llm = GoogleGenerativeAI(model="gemini-pro")
    input_variables={"match_details": yaml.dump(match_details),
                    "lineups": yaml.dump(line_ups)}
    prompt = PromptTemplate.from_template(agent_prompt)
    chain = LLMChain(llm=llm, prompt=prompt, verbose=True)
    return chain.run(
        **input_variables
    )


def get_specialist_comments_no_tools(action_input:str, prompt_style) -> str:
    """
    Provide an overview of the match and the match details.
    Provide comments of a sports specialist about a specific match.
    The specialist knows match details and lineups.
    
    Args:
        - action_input(str): The input data containing the competition_id, season_id and match_id.
          format: {
              "competition_id": 123,
              "season_id": 02,
              "match_id": 12345
            }
    """
    match_details = retrieve_match_details(action_input)
    line_ups = get_lineups(match_details["match_id"])
    return get_sport_specialist_comments_about_match(match_details, line_ups, prompt_style)



# Gera o comentário do especialista.
@tool
def get_specialist_comments(action_input:str, prompt_style) -> str:
    """
    Provide an overview of the match and the match details.
    Provide comments of a sports specialist about a specific match.
    The specialist knows match details and lineups.
    
    Args:
        - action_input(str): The input data containing the competition_id, season_id and match_id.
          format: {
              "competition_id": 123,
              "season_id": 02,
              "match_id": 12345
            }
    """
    match_details = retrieve_match_details(action_input)
    line_ups = get_lineups(match_details["match_id"])
    return get_sport_specialist_comments_about_match(match_details, line_ups, prompt_style)


# Filtra a partida desejada (match_id) e retorna os detalhes da partida
def retrieve_match_details(action_input:str) -> str:
    """
    Get the details of a specific match 
    
    Args:
        - action_input(str): The input data containing the match_id.
          format: {
              "match_id": 12345
              "competition_id": 123,
                "season_id": 02
            }
    """
    match_id = json.loads(action_input)["match_id"]
    competition_id = json.loads(action_input)["competition_id"]
    season_id = json.loads(action_input)["season_id"]
    matches = json.loads(get_matches(competition_id, season_id))
    match_details= next(
        (match for match in matches if match["match_id"] == int(match_id)),
        None
    )
    return match_details
