import streamlit as st
import pandas as pd
import time
from statsbombpy import sb
from tools.football import  get_raw_data_match, get_match_overview
from football_stats.matches import return_overview_events_goals, get_cards_overview


@st.cache_data
def load_data():
    competitions = sb.competitions()
    df = competitions[competitions['competition_name'] == 'FIFA World Cup']
    competition_id = df['competition_id'].unique()
    return df, competition_id

def filter_season(df):
    with st.sidebar:
        st.subheader("Filtros")
        df, season_id = year_filter(df)
    return df, season_id 

def filter_match(df, season_id, competition_id):
    with st.sidebar:
        df_matches, match_id = match_filter(df, season_id, competition_id)
    return df_matches, match_id

@st.cache_data
def load_matches(competition_id, season_id):
    return sb.matches(competition_id=competition_id, season_id=season_id)

def valid_index(options, index):
    pass
    if len(options) < index:
        return 0
    else:
        return index

def match_filter(df, season_id, competition_id):
    if 'id_index_match_id' not in st.session_state:
        st.session_state.id_index_match_id = 0
        id_index_match_id = 0
    else:
        id_index_match_id = st.session_state.id_index_match_id
    
    df_matches = load_matches(competition_id=competition_id[0], season_id=season_id)
    options_match = df_matches['match_id'].unique()
    
    id_index_match_id = valid_index(options_match, id_index_match_id)
    
    # Add the 'key' parameter to store the selection in st.session_state
    
    
    match_id = st.selectbox('Selecione o jogo:', options_match,
                            format_func=lambda idx: get_match_label(df_matches, idx),
                            key='match_id',
                            index=id_index_match_id
                            )
    
    
    id_index_match_id = list(df_matches['match_id']).index(match_id)
    st.session_state.id_index_match_id = id_index_match_id
    
    
    df_matches = df_matches[df_matches['match_id'] == match_id]
    return df_matches, match_id

def get_match_label(matches, match_id):
    row = matches[matches['match_id'] == match_id].iloc[0]
    return f"{row['match_date']} - {row['home_team']} x {row['away_team']}"

def year_filter(df):
    if 'id_index_season_name' not in st.session_state:
        st.session_state.clear()
        st.session_state.id_index_season_name = 0
        id_index_season_name = 0
    else:
        id_index_season_name = st.session_state.id_index_season_name
    
    st.write("")
    season_options = df['season_name'].unique()
    id_index_season_name = valid_index(season_options, id_index_season_name)
    # Carregar Matches com Spinner
    
    season_name = st.selectbox('Selecione a copa do mundo:', season_options, key='season_name', index=id_index_season_name, on_change=restart_session_state('season_name'))
        
        
    id_index_season_name = list(season_options).index(season_name)
    st.session_state.id_index_season_name = id_index_season_name
    
    season_id = df[df['season_name'] == season_name].season_id.values[0]
    df = df[df['season_id'] == season_id]
    return df, season_id

def restart_session_state(nivel):
    if nivel == "event_type":
        try:
            del st.session_state.id_index_player
        except:
            pass
    if nivel == "season_name":
        try:
            del st.session_state.id_index_match_id
            del st.session_state.id_index_event_type
            del st.session_state.id_index_player
        except:
            pass
        
def run():
    st.title("Copas do Mundo")
    tempo_carregamento = 0.1
    #carregar_dados()
    #st.title("Jogo da Copa do Mundo")
    with st.sidebar:
        with st.spinner('Processando. Por favor, aguarde...'):
            time.sleep(1)
            progress_bar = st.progress(0)
            status_text = st.empty()
    status_text.text("Carregando competições...")
    progress_bar.progress(33)    
    time.sleep(tempo_carregamento)
    
    df, competition_id = load_data()
    
    tipo_filtro = st.sidebar.radio("Filtrar por:", ["Ano e Jogo", "ID da Partida"], index=1)
    
    if tipo_filtro == "Ano e Jogo":
    
        df, season_id = filter_season(df)
        
        status_text.text("Carregando partidas...")
        df_match, match_id = filter_match(df, season_id, competition_id)
        progress_bar.progress(66)
        time.sleep(tempo_carregamento)
        
        match = df_match[df_match['match_id'] == match_id].iloc[0]
        with st.sidebar:
            st.write(f"ID da partida: {match_id}")
            
        # converte data para o formato dd/mm/yyyy
        match_date  = pd.to_datetime(match['match_date'])
        match_date = match_date.strftime('%d/%m/%Y')
        
        hora = pd.to_datetime(match['kick_off'])
        hora = hora.strftime('%H:%M')
        
        progress_bar.progress(100)
        time.sleep(tempo_carregamento*1.6)
        progress_bar.empty()
        status_text.text("")    
    
    else:
        with st.sidebar:
            match_id = st.sidebar.number_input("ID da partida:", min_value=0, max_value=1000000000, value=3888701)
        raw_data_match = get_raw_data_match(match_id)
        tab1, tab2 = st.tabs(["Raw Data Match", "Match Overview"])
        with tab1:
            home_team = raw_data_match["home_team"]["home_team_name"]
            away_team = raw_data_match["away_team"]["away_team_name"]
            st.subheader(f"{home_team} x {away_team}")
            st.write(raw_data_match)
        with tab2:
            st.subheader(f"{home_team} x {away_team}")
            general_data_match, match_overview = get_match_overview(match_id)
            # Obtém os principais eventos da partida
            df_goal, goal_list = return_overview_events_goals(match_id)
            # Obtém os cartões da partida
            df_eventos_cartoes,list_cartoes = get_cards_overview(match_id)

            st.write('**Overview:**')
            # st.write(general_data_match[["home_team", "away_team", "home_score", "away_score"]]) # 
            st.write(f"     Final Score: {int(general_data_match['home_score'])} x {int(general_data_match['away_score'])}")

            st.divider()
            
            st.write('**Goals:**')
            # st.write(df_goal[['team','player','key_pass_player']])
            for goal in goal_list:
                st.write(goal['team'])

            print('==================== Cartões ====================')
            st.write(df_eventos_cartoes[['minute', 'team', 'player', 'card_name']])
        
        
        progress_bar.progress(100)
        time.sleep(tempo_carregamento*1.6)
        progress_bar.empty()
        status_text.text("") 
    


if __name__ == "__main__":
    run()