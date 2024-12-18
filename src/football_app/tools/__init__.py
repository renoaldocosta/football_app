
from typing import List, Dict
from langchain_core.tools import Tool

from langchain_community.utilities.wikipedia import WikipediaAPIWrapper
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
import yaml

from .self_ask_agent import get_self_ask_agent, search_team_information
from tools.football import get_specialist_comments, retrieve_match_details, top_players_by_pass, get_players_stats
from langchain.tools import tool


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




# src\football_app\tools\football.py 
def load_tools(tool_names: List[str] = []) -> Dict[str, Tool]:
    """
    Load the tools with the given tool names
    """
    TOOLS = [
        # search_team_information,
        # get_match_details,
        # get_specialist_comments, 
        top_players_by_pass,
        get_players_stats,
        Tool.from_function(name='Self-ask agent',
                           func=get_self_ask_agent().invoke,
                           description="A tool to answer complicated questions.  "
                                       "Useful for when you need to answer questions "
                                       "competition events like matches, or team "
                                       "details. Input should be a question."),
        WikipediaQueryRun(
            api_wrapper=WikipediaAPIWrapper(),
            description="A wrapper around Wikipedia. Useful for when you need"
                        " to answer general questions about people, players, teams,"
                        " competitions, stadiums (the stadium history and "
                        " capacity), cities, events or other subjects. "
                        " Input should be a search query."
        )
    ]
    if tool_names == []:
        return TOOLS
    return [t for t in TOOLS if t.name in tool_names]