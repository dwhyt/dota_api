import sys
sys.path.insert(0,'..')

import streamlit as st
import dota_functions

# st.session_state.account_list = []

account_ids = st.text_input('Enter account ids to compare win-loss rate', value='', placeholder = 'Enter account ids, seperated by commas (example - 191312823, 1627496, 739473)')

query_period = st.radio(
'Query matches in the past?',
('Last Week', 'Last Month', 'Last Year', 'All-Time', 'Custom Period'))

if query_period == 'Custom Period':
    text_input = st.text_input(label='Enter number of days of matches to consider')

accounts_query = [(account_id.strip()) for account_id in account_ids.split(',')]

if st.button('Get Leaderboard!'):
    if query_period == 'All-Time':
        board = dota_functions.rank_players_by_wl(accounts_list=accounts_query, num_days_back=None)
    elif query_period == 'Last Week':
        board = dota_functions.rank_players_by_wl(accounts_list=accounts_query, num_days_back=7)
    elif query_period == 'Last Month':
        board = dota_functions.rank_players_by_wl(accounts_list=accounts_query, num_days_back=30)
    elif query_period == 'Last Year':
        board = dota_functions.rank_players_by_wl(accounts_list=accounts_query, num_days_back=365)
    else:
        board = dota_functions.rank_players_by_wl(accounts_list=accounts_query, num_days_back=int(float(text_input)))

    st.dataframe(board)
# submit_button = st.form_submit_button(label='Get leaderboard!')

# else:
#     st.write("You didn't select comedy.")