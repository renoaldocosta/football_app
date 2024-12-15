import streamlit as st
import pandas as pd
import json
import time
from statsbombpy import sb
from tools.football import  get_raw_data_match, get_match_overview
from football_stats.matches import return_overview_events_goals, get_cards_overview, process_match_lineups, get_player_stats
from mplsoccer import (
    Sbopen,
    Pitch,
)


parser = Sbopen()

@st.cache_data
def load_data():
    competitions = sb.competitions()
    df = competitions[competitions['competition_name'] == 'FIFA World Cup']
    competition_id = df['competition_id'].unique()
    return df, competition_id

@st.cache_data
def get_events(match_id):
    events = sb.events(match_id=match_id, flatten_attrs=True)
    return events

def filter_vision(visao, match_id, home_team, away_team):
    events = get_events(match_id)
    if visao == "Casa":
        events = events[events['team'] == home_team]
    elif visao == "Visitante":
        events = events[events['team'] == away_team]
    elif visao == "Geral":
        pass
    return events

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
        tab1, tab2, tab3, tab4 = st.tabs(["Raw Data Match", "Match Overview", "Events Player", "Advanced Stats"])
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
            st.write(f"     Final Score: **{int(general_data_match['home_score'])}** x **{int(general_data_match['away_score'])}**")

            st.divider()
            
            st.write('**Goals:**')
            # st.write(df_goal[['team','player','key_pass_player']])
            for goal in goal_list:
                st.write(f"**Team:** {goal['team']}- **Player:** {goal['player']} - **Assistence:** ({goal['key_pass_player']})")

            st.divider()
            
            st.write('**Cards**')
            # st.write(df_eventos_cartoes[['minute', 'team', 'player', 'card_name']])
            # st.write(list_cartoes)
            for card in list_cartoes:
                st.write(f"**Card:** {card['card']['card_name']} - **Team:** {card['card']['team']} - **Player:** {card['card']['player']}")
                # st.write(f"**Team:** {card['team']} - **Player:** {card['player']} - **Card:** {card['card_name']}")
        with tab3:
            lineups_df = process_match_lineups(match_id)
            # Formato para selectbox: pleyer: Pais - Jogador
            player = st.selectbox('Selecione o jogador:', lineups_df['player_name'], format_func=lambda x: f"{lineups_df['country'][lineups_df['player_name'] == x].values[0]} - {x}")
            st.header(f"STATS For Player ({player})")
            try:
                col = st.columns(3)
                with col[1]:
                    player_events = get_player_stats(match_id, player)
                    player_events = json.loads(player_events)
                    player_events.pop('player_name')
                    for event in player_events:
                        st.write(f"{event}: {player_events[event]}")
            except:
                st.write(f"No events found for player '{player}'")
        with tab4:
            # get_events(match_id)
            col = st.columns(3)
            with col[1]:
                vision_options = [home_team, away_team] # ["Casa", "Visitante"]
                visao = st.radio("Selecionar jogador da seleção:", vision_options, horizontal=True, index=0, key='visao_player')
                if visao == home_team:
                    visao = "Casa"
                elif visao == away_team:
                    visao = "Visitante"
                status_text.text("Carregando eventos da partida...")
                events = filter_vision(visao, match_id, home_team, away_team)
                
                # st.write(events)
                
                progress_bar.progress(100)
                time.sleep(tempo_carregamento*1.6)
                progress_bar.empty()
                status_text.text("")
                
                home_lineup = sb.lineups(match_id=match_id)[home_team].sort_values('jersey_number')
                away_lineup = sb.lineups(match_id=match_id)[away_team].sort_values('jersey_number')
                lineups = sb.lineups(match_id=match_id)
                
                lineups, yellow_cards, red_cards = lineups_metrics(lineups, visao, home_lineup, away_lineup)
                events, player = filter_players(events, todos=False)
                position = events['position'].value_counts().idxmax()
                event_columns = [
                'minute',          # Minuto do evento
                'second',          # Segundo do evento
                'team',            # Nome do time
                'type',            # Tipo de evento (Pass, Shot, Duel, etc.)
                'position',        # Posição do jogador no campo
                'player',          # Nome do jogador
                'pass_body_part',  # Parte do corpo usada para o passe (se for um passe)
                'pass_recipient',  # Nome do jogador que recebeu o passe (se for um passe)
                'pass_height',     # Altura do passe (se for um passe)
                'pass_length',     # Comprimento do passe (se for um passe)
                'pass_outcome',    # Resultado do passe (se for um passe)
                'under_pressure',  # Se o jogador estava sob pressão
                'location',        # Localização do evento no campo
                'pass_end_location',  # Fim do passe (se for um passe)
                'shot_outcome',    # Resultado do chute (se for um chute)
                'shot_statsbomb_xg',  # xG do chute (se for um chute)
                'shot_technique',  # Técnica do chute (se for um chute)
                'duel_outcome',    # Resultado do duelo (se for um desarme)
                ]
            events = events[event_columns]
            # Metricas passes
            passes = events['type'].value_counts().get('Pass', 0)
            passes_completos = passes - events['pass_outcome'].value_counts().get('Incomplete', 0)
            chutes_a_gol = events['type'].value_counts().get('Shot', 0)
            gols = events['shot_outcome'].value_counts().get('Goal', 0)
            
            percent_passes = percent(passes_completos, passes)
            percent_score = percent(gols, chutes_a_gol)
            
            st.write(events)
            # Agrega eventos por typy, count
            events = events.groupby('type').size().reset_index(name='count')
            events = events.sort_values('count', ascending=False)
            events_to_show = events.reset_index(drop=True)
            events_to_show.rename(columns={'type': 'Event Type', 'count': 'Count'}, inplace=True)
            events_to_show.index = events_to_show.index + 1
            with st.expander("Aggregated Events"):
                col = st.columns(3)
                with col[1]:
                    col2 = st.columns(2)
                    for num, event in enumerate(events_to_show.iterrows()):
                        if num % 2 == 0:
                            with col2[0]:
                                st.write(f"{event[1]['Event Type']}: {event[1]['Count']}")
                        else:
                            with col2[1]:
                                st.write(f"{event[1]['Event Type']}: {event[1]['Count']}")
            # Cria gráfico com plotly para Event Type e Count
            # fig = px.bar(events_to_show, x='Event Type', y='Count', title='Event Type and Count')
            # st.plotly_chart(fig)
            
                
                
                
            st.write(f"")
            position = translate_position(position)
            jersey_number = lineups[lineups['player_name'] == player]['jersey_number'].values[0]
            st.subheader(f"Posição: {position} | Camisa: {jersey_number}")
            st.write(f"")
            
            col6 = st.columns([1, 1, 1,1,1,1])
            with col6[0]:
                st.metric("Passes", passes)
            with col6[1]:
                st.metric("Passes Sucedidos", passes_completos)
            with col6[2]:
                st.metric("Precisão de Passe", f'{percent_passes}%')
            with col6[3]:
                st.metric("Chutes a Gol", chutes_a_gol)
            with col6[4]:
                st.metric("Gols", gols)
            with col6[5]:
                st.metric("Conversão(Gols)", f'{percent_score}%')
            
            st.write('')
            st.divider()
            st.subheader('Eventos do jogador')
            
            events, event_type  = filter_events(events, todos=False)
            col8 = st.columns([1,2,1])
            with col8[1]:
                final_data = match_data(match_id)
                fig,soma_linha_zero = plot_passes(final_data, player, event_type)
                event_type = translate_event(event_type)
                if soma_linha_zero != 0:
                    st.subheader(f"Mapa: {event_type}")
                    st.pyplot(fig)
            st.subheader(f"Detalhamento do evento de {event_type}")

            events_to_show = events.reset_index(drop=True)
            events_to_show.index = events_to_show.index + 1
            st.dataframe(events_to_show)
            
            def match_data_2(match_id):
                return parser.event(match_id=match_id)[0]
            
        progress_bar.progress(100)
        time.sleep(tempo_carregamento*1.6)
        progress_bar.empty()
        status_text.text("") 
    


if __name__ == "__main__":
    run()


@st.cache_data
def lineups_metrics(lineups, visao, home_lineup, away_lineup):
    if "Casa" in visao:
        lineups = process_lineup(home_lineup)
        
    elif "Visitante" in visao:
        lineups = process_lineup(away_lineup)
    elif visao == "Geral":
        home_lineup = process_lineup(home_lineup)
        away_lineup = process_lineup(away_lineup)
        lineups = pd.concat([home_lineup, away_lineup])
    try:
        yellow_cards = lineups['card_0_card_type'].value_counts().get('Yellow Card', 0)
    except:
        yellow_cards = 0
    try:
        red_cards = lineups['card_0_card_type'].value_counts().get('Red Card', 0)
    except:
        red_cards = 0
    
    return lineups, yellow_cards, red_cards

def process_lineup(lineup_df):
    """
    Processa o DataFrame de lineup expandindo as colunas necessárias.
    
    Args:
        lineup_df (pd.DataFrame): DataFrame de lineup da equipe.
        
    Returns:
        pd.DataFrame: DataFrame processado com colunas expandidas.
    """
    # Expandir a coluna 'positions'
    lineup_df = expand_column(lineup_df, 'positions', 'position')
    
    # Expandir 'position_0' e 'position_1' se existirem
    for pos in ['position_0', 'position_1']:
        if pos in lineup_df.columns:
            lineup_df = expand_column(lineup_df, pos, pos)
    
    # Expandir a coluna 'cards'
    lineup_df = expand_column(lineup_df, 'cards', 'card')
    
    # Expandir 'card_0' se existir
    if 'card_0' in lineup_df.columns:
        lineup_df = expand_column(lineup_df, 'card_0', 'card_0')
    
    return lineup_df


def expand_column(df, column_name, prefix):
    """
    Expande uma coluna que contém dicionários ou listas de dicionários em múltiplas colunas.
    
    Args:
        df (pd.DataFrame): DataFrame original.
        column_name (str): Nome da coluna a ser expandida.
        prefix (str): Prefixo para as novas colunas.
        
    Returns:
        pd.DataFrame: DataFrame com a coluna expandida.
    """
    expanded_df = df[column_name].apply(pd.Series)
    expanded_df.columns = [f'{prefix}_{col}' for col in expanded_df.columns]
    return pd.concat([df.drop(column_name, axis=1), expanded_df], axis=1)


def filter_players(events, todos=True):
    if 'id_index_player' not in st.session_state:
        st.session_state.id_index_player = 0
        id_index_player = 0
    else:
        id_index_player = st.session_state.id_index_player
    if todos:
        options_player = ["Todos"] + events['player'].unique().tolist()
    else:
        options_player = events['player'].unique().tolist()
    # remove nan values
    options_player = [x for x in options_player if str(x) != 'nan']
    id_index_player = valid_index(options_player, id_index_player)
    player = st.selectbox(
            "Selecione o jogador", 
            options_player,
            index=id_index_player,
        )
    try:
        id_index_player = options_player.index(player)
    except:
        pass
    st.session_state.id_index_player = id_index_player
    
    if player == "Todos":
        return events, player
        
    else:
        return events[events['player'] == player], player

def percent(value, total):
    if total == 0:
        return 0
    else:
        return round((value / total) * 100,2)

def translate_position(position):
    # Dicionário para mapear posições de futebol em inglês para português
    position_translation = {
        'Right Wing Back': 'Ala Direito',
        'Right Defensive Midfield': 'Volante Direito',
        'Right Center Back': 'Zagueiro Direito',
        'Left Defensive Midfield': 'Volante Esquerdo',
        'Left Wing Back': 'Ala Esquerdo',
        'Left Center Back': 'Zagueiro Esquerdo',
        'Center Back': 'Zagueiro Central',
        'Goalkeeper': 'Goleiro',
        'Center Attacking Midfield': 'Meia Ofensivo Central',
        'Left Center Forward': 'Atacante Esquerdo',
        'Right Center Forward': 'Atacante Direito',
        'Substitute': 'Substituto',
        'Center Forward': 'Atacante Central',
        'nan': 'Indefinido'  # Para lidar com valores NaN
    }
    return position_translation.get(position, position)

def filter_events(events, todos=True):
    if 'id_index_event_type' not in st.session_state:
        st.session_state.id_index_event_type = 0
        id_index_event_type = 0
    else:
        id_index_event_type = st.session_state.id_index_event_type
    
    # Adicionar "Todos" à lista de opções, se necessário
    if todos:
        options_event_type = ["Todos"] + events['type'].unique().tolist()
    else:
        options_event_type = events['type'].unique().tolist()

    if todos:
        # Traduzir os eventos para exibição no selectbox
        translated_options_event_type = ["Todos"] + [translate_event(event) for event in events['type'].unique().tolist()]

        id_index_event_type = valid_index(translated_options_event_type, id_index_event_type)
    else:
        # Traduzir os eventos para exibição no selectbox
        translated_options_event_type = [translate_event(event) for event in events['type'].unique().tolist()]

        id_index_event_type = valid_index(translated_options_event_type, id_index_event_type)

    # Exibir os eventos traduzidos no selectbox
    event_type_translated = st.selectbox(
        "Selecione o tipo de evento", 
        translated_options_event_type,
        index=id_index_event_type,
    )

    # Encontrar o índice do evento traduzido na lista original
    if event_type_translated == "Todos":
        event_type = "Todos"
    else:
        event_type = options_event_type[translated_options_event_type.index(event_type_translated)]
    
    id_index_event_type = translated_options_event_type.index(event_type_translated)
    st.session_state.id_index_event_type = id_index_event_type
    
    # Filtrar eventos, se necessário
    if event_type == "Todos":
        return events, event_type
    else:
        return events[events['type'] == event_type], event_type

def translate_event(event_type):
    event_translation = {
        '50/50': '50/50',
        'Bad Behaviour': 'Comportamento Antidesportivo',
        'Ball Receipt*': 'Bola Recebida',
        'Ball Recovery': 'Bola Recuperada ',
        'Block': 'Bloqueio',
        'Camera off: Deprecated': 'Câmera Desligada (Depreciado)',
        'Camera On: Deprecated': 'Câmera Ligada (Depreciado)',
        'Carry': 'Condução de Bola',
        'Clearance': 'Desarme',
        'Dispossessed': 'Perdeu a Bola',
        'Dribble': 'Drible',
        'Dribbled Past': 'Driblado pelo Adversário',
        'Duel': 'Duelo',
        'Error': 'Erro',
        'Foul Committed': 'Falta Cometida',
        'Foul Won': 'Falta Sofrida',
        'Goal Keeper': 'Goleiro',
        'Half End': 'Fim do Tempo',
        'Half Start': 'Início do Tempo',
        'Injury Stoppage': 'Parada por Lesão',
        'Interception': 'Interceptação',
        'Miscontrol': 'Perda de Controle',
        'Offside': 'Impedimento',
        'Own Goal Against': 'Gol Contra',
        'Own Goal For': 'Gol Para',
        'Pass': 'Passe',
        'Player Off': 'Jogador Saiu',
        'Player On': 'Jogador Entrou',
        'Pressure': 'Pressão',
        'Referee Ball-Drop': 'Bola Caída',
        'Shield': 'Proteção de Bola',
        'Shot': 'Chute ao Gol',
        'Starting XI': 'Escalação Inicial',
        'Substitution': 'Substituição',
        'Tactical Shift': 'Mudança Tática'
    }
    return event_translation.get(event_type, event_type)

def match_data(match_id):
    return parser.event(match_id=match_id)[0]

def plot_passes(match_data, player_name, event_type='Pass'):
    # Filtrar os dados para o tipo de evento e jogador especificado
    player_filter = (match_data['type_name'] == event_type) & (match_data['player_name'] == player_name)
    df_events = match_data.loc[player_filter, ['x', 'y', 'end_x', 'end_y']].copy()
    
    # Substituir strings vazias por NaN
    df_events[['end_x', 'end_y']] = df_events[['end_x', 'end_y']].replace('', pd.NA)
    
    # Converter para float (se necessário)
    df_events[['x', 'y', 'end_x', 'end_y']] = df_events[['x', 'y', 'end_x', 'end_y']].astype(float)
    # soma os valores da linha 0
    try:
        soma_linha_zero = df_events.iloc[0].sum()
    except:
        soma_linha_zero = 0
    # Separar eventos com e sem end_x/end_y
    df_valid = df_events.dropna(subset=['end_x', 'end_y'])
    df_invalid = df_events[df_events['end_x'].isna() | df_events['end_y'].isna()]
    
    # Configurar o campo
    pitch = Pitch(pitch_type='statsbomb', pitch_color='#aabb97', line_color='white',
                  stripe_color='#c2d59d', stripe=False)  # Ajuste conforme necessário
    
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # Plotar setas para eventos válidos
    if not df_valid.empty:
        pitch.arrows(df_valid['x'], df_valid['y'], df_valid['end_x'], df_valid['end_y'], 
                    width=2, color='white', ax=ax)
    
    event_type_translated = translate_event(event_type)
    # Plotar pontos para eventos inválidos
    if not df_invalid.empty:
        pitch.scatter(df_invalid['x'], df_invalid['y'], s=100, color='red', edgecolors='black', 
                     alpha=0.7, ax=ax, label=event_type_translated)
    
    # Opcional: Adicionar mapa de calor para os eventos válidos
    if not df_valid.empty:
        try:
            pitch.kdeplot(df_valid['x'], df_valid['y'], ax=ax, alpha=0.5, shade=True, cmap='coolwarm')
        except Exception as e:
            st.write("Não foi possível plotar o mapa de calor:", e)
    
    # Legenda (apenas se houver eventos inválidos)
    if not df_invalid.empty:
        ax.legend()
    
    return fig, soma_linha_zero

