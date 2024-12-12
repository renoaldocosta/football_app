from statsbombpy import sb  # type: ignore
import json

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



if __name__ == "__main__":
    match_id = 22949
    match_data = get_match_details_match_id(match_id)
    print(match_data)