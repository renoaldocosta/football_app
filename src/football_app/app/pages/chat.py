from football_stats.competitions import get_competitions, get_matches
# src\football_app\football_stats\competitions.py
from football_stats.matches import get_lineups, get_events, get_player_stats
from langchain.memory import ConversationBufferMemory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.schema import AIMessage, HumanMessage

from langchain_community.callbacks.streamlit import StreamlitCallbackHandler
from tools.football import get_sport_specialist_comments_about_match as comments_about_a_match
from tools import load_tools
import json

from agent import load_agent

import streamlit as st

# st.set_page_config(layout="wide",
#                    page_title="Football Match Conversation App",
#                    page_icon="⚽️")

def run():
    msgs = StreamlitChatMessageHistory()


    if "memory" not in st.session_state:
        st.session_state["memory"] = ConversationBufferMemory(messages=msgs, memory_key="chat_history", return_messages=True)

    memory = st.session_state.memory

    def memorize_message():
        user_input = st.session_state["user_input"]
        st.session_state["memory"].chat_memory.add_message(HumanMessage(content=user_input))
        
    def load_competitions():
        """
        Simulates loading competitions from your function.
        Replace this with the actual call to fetch competitions.
        """
        return json.loads(get_competitions())

    def load_matches(competition_id, season_id):
        """
        Simulates loading matches for a specific competition.
        Replace this with the actual call to fetch matches for a competition.
        """
        return  json.loads(get_matches(competition_id, season_id))


    # Streamlit Sidebar
    st.sidebar.title("FIFA World Cup")
    # Step 1: Select a Competition
    selected_competition = None
    selected_season = None
    selected_match = None
    match_id = None
    match_details = None
    specialist_comments = None

    competitions = load_competitions()
    # competition_names = sorted(set([comp['competition_name'] for comp in competitions]))
    # selected_competition = st.sidebar.selectbox("Choose a Competition",
    #                                             competition_names)
    selected_competition = 'FIFA World Cup'

    if selected_competition:
        # Step 2: Select a Season
        st.sidebar.header("Select a Season")
        seasons = set(comp['season_name'] for comp in competitions
                    if comp['competition_name'] == selected_competition)
        selected_season = st.sidebar.selectbox("Choose a Season", sorted(seasons))
        
        
    if selected_season:
        # Get the selected competition ID
        competition_id = next(
            (comp['competition_id'] for comp in competitions 
            if comp['competition_name'] == selected_competition),
            None
        )
        season_id = next(
            (comp['season_id'] for comp in competitions 
                                if comp['season_name'] == selected_season 
                                and comp['competition_name'] == selected_competition),
            None
        )
        # Step 2: Select a Match
        st.sidebar.header("Select a Match")
        matches = load_matches(competition_id, season_id)
        match_names = sorted([f"{match['home_team']} vs {match['away_team']}" for match in matches])
        
        if selected_match:=st.sidebar.selectbox("Choose a Match", match_names):
            # Get the selected match ID
            match_details = next(
                (match for match in matches if f"{match['home_team']} vs {match['away_team']}" == selected_match),
                None
            ) 
            match_id = match_details['match_id']
            
    # Main Page
    if not match_id:
        st.title("Football Match Conversation")
        st.write("Use the sidebar to select a competition, then a match, and start a conversation.")
    else:
        st.markdown(
        """
        <style>
        .title {
            text-align: center;
        }
        </style>
        """,
        unsafe_allow_html=True)
        st.markdown(f'<h1 class="title">{selected_match}</h1><h3 class="title">{selected_competition} - Season {selected_season}</h3>', unsafe_allow_html=True)
        with st.container(border=False):
            st.chat_input(key="user_input", on_submit=memorize_message) 
            if user_input := st.session_state.user_input:
                chat_history = st.session_state["memory"].chat_memory.messages
                for msg in chat_history:
                    if isinstance(msg, HumanMessage):
                        with st.chat_message("user"):
                            st.write(f"{msg.content}")
                    elif isinstance(msg, AIMessage):
                        with st.chat_message("assistant"):
                            st.write(f"{msg.content}")
                            
                with st.spinner("Agent is responding..."):
                    try:
                        # Load agent
                        try:
                            agent = load_agent()
                        except Exception as e:
                            st.error(f"Error loading the agent: {str(e)}")
                            st.stop()
                        
                        # Cache tools to avoid redundant calls
                        tools = load_tools()
                        tool_names = [tool.name for tool in tools]
                        tool_descriptions = [tool.description for tool in tools]
                        # st.write(tool_names)
                        # st.divider()
                        # st.write(tool_descriptions)

                        # Prepare input for the agent
                        input_data = {
                            "match_id": match_id,
                            "match_name": selected_match,
                            "input": user_input,
                            "agent_scratchpad": "",
                            "competition_id": competition_id,
                            "season_id": season_id,
                            "tool_names": tool_names,
                            "tools": tool_descriptions,
                        }

                        # Debug: Print input to verify structure (optional)
                        # st.write(f"Input to agent: {input_data}")

                        # Invoke agent
                        response = agent.invoke(input=input_data, handle_parsing_errors=True)

                        # Validate response
                        if isinstance(response, dict) and "output" in response:
                            output = response.get("output")
                        else:
                            output = "Sorry, I couldn't understand your request. Please try again."

                        # Add response to chat memory
                        st.session_state["memory"].chat_memory.add_message(AIMessage(content=output))

                        # Display response in chat
                        with st.chat_message("assistant"):
                            st.write(output)

                    except Exception as e:
                        # Handle and display errors gracefully
                        st.error(f"Error during agent execution: {str(e)}")
                        st.write("Ensure that your inputs and agent configuration are correct.")


if __name__ == "__main__":
    run()