from langchain_google_genai import GoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.agents import create_react_agent, AgentExecutor
from langchain import hub
from typing import List
from tools.load_tools import load_tools
# src\football_app\tools\load_tools

    # 5. Analyze match overview such as date, location, competition, and result.

def load_agent() -> AgentExecutor:
    """
    Load the agent with the given tool names
    """
    llm = GoogleGenerativeAI(model="gemini-pro", temperature=0.2)
    
    football_prompt = """
    You are a helpful AI assistant tasked with analyzing a football match. 
    Your goal is to provide insights and perform analyses based on the {match_name} match's details.
    The match is identified by its unique database ID: {match_id}. 
    The competition ID: {competition_id}.
    The season ID: {season_id}.

    The task involves:
    1. Analyze specific passes in the match (e.g., who made the most passes).
    2. Compare player statistics (e.g., goals, assists, shots on target).
    3. Compare player statistics by period (e.g., 1, 2).

    You have access to the following tools: {tool_names}.
    Descriptions of tools: {tools}.

    ### Tools and Usage Instructions:
    - Each tool has a specific purpose, such as retrieving match details, analyzing lineups, or generating summaries.
    - To use a tool, respond exactly in this format:

    Thought: [Your reasoning about what action to take next]
    Action: [The name of the tool to use]
    Action Input: [The input required by the tool, such as the match_id or specific data]
    Observation: [The output or result from the tool]

    Example:
        Thought: I need to retrieve the players that made the most passes in the match.
        Action: top_players_by_pass
        Action Input: {{"match_id": "12345"}}
        
        Thought: I need to compare player statistics to provide insights.
        Action: get_players_stats
        Action Input: {{"match_id": "3888701", "player1": "Roberto Rivelino", "player2":"Édson Arantes do Nascimento"]}}
        
        Thought: I need to compare player statistics by period to provide insights.
        Action: get_players_stats_by_period
        Action Input: {{"match_id": "3888701", "player1": "Roberto Rivelino", "player2":"Édson Arantes do Nascimento", "period": "1"}}

    ### Observations and Next Steps:
    - Based on the tool's output, decide on the next action or provide your analysis.
    - If more data is needed, use another tool or refine your analysis.
    - If the task is complete, provide a final answer.

    ### Stopping Condition:
    - When the analysis is complete, respond in this format:
    
    Thought: I have completed the analysis. No further tools are required.
    Final Answer: [Your final comprehensive analysis, summarizing all insights about the match.]

    ### Current Task:
    {input}

    ### Agent's Workspace:
    {agent_scratchpad}
    """
    
    # Thought: I need to retrieve the basic details of the match to provide an overview.
    #     Action: get_match_details
    #     Action Input: {{"match_id": "12345", "competition_id": "123", "season_id": "02"}}
    prompt = PromptTemplate(
       input_variables=["match_id",
                        "match_name",
                        "input",
                        "players_name",
                        "agent_scratchpad",
                        "tool_names",
                        "tools"],
       template=football_prompt
    )
    tools = load_tools()
    agent = create_react_agent(llm, tools=tools, prompt=prompt)
    
    return AgentExecutor(
        agent=agent,
        tools=tools,
        handle_parsing_errors=True,
        verbose=True,
        max_iterations=10
    )