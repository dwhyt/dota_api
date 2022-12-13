import dota_functions

from datetime import datetime, date

from django.http import JsonResponse


def leaderboard(request, accounts_list_str, query_period):
    
    accounts_query = [(account_id.strip()) for account_id in accounts_list_str.split(',')]
    
    if "-" in query_period: 
        date_object = datetime.strptime(query_period, "%Y-%m-%d").date()
        leader_board = dota_functions.rank_players_by_wl(accounts_query, abs((date.today() - date_object).days))
    elif query_period == 'last_week':
        leader_board = dota_functions.rank_players_by_wl(accounts_query, 7)
    elif query_period == 'last_month':
        leader_board = dota_functions.rank_players_by_wl(accounts_query, 30)
    elif query_period == 'last_year':
        leader_board = dota_functions.rank_players_by_wl(accounts_query, 365)
    elif query_period == 'all_time':
        leader_board = dota_functions.rank_players_by_wl(accounts_query)

    return(JsonResponse({"leaderboard":leader_board}))

def hero_recommender(request, account_id):

    resp = JsonResponse({"recommendations":dota_functions.recommendation_wrapper(account_id=account_id, query_period=30, min_num_matches=30, num_reccs=3)})
    
    return(resp)