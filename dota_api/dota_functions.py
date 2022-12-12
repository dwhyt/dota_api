import requests
import pandas
from tqdm.notebook import tqdm
from scipy.sparse import csr_matrix
from scipy import sparse
from datetime import date, timedelta
import numpy as np

from surprise import NormalPredictor, Dataset, Reader, SVD, KNNBasic
from surprise.model_selection import cross_validate


def accounts_from_match(match_id: int) -> list:
    """
        Returns the list of player account_ids from specified match
        
        Params:
        match_id (int) - match_id to check
        
        Returns:
        A list of ints, containing the account_ids of players
    """
    
    # request = requests.get(f"https://api.opendota.com/api/matches/{match_id}?api_key={API_KEY}")
    request = requests.get(f"https://api.opendota.com/api/matches/{match_id}").json()
    accounts_list = [player["account_id"] for player in request["players"]]
    return(accounts_list)

def check_player_wl(account_id: int, num_days_back: int=None) -> tuple:
    """
        Calculates win-loss rate for a player given player's account_id, 
        given as ratio calculated using the following formula - number of wins divided by number of losses
        
        Params:
        account_id (int) - player's account_id to check, passed in as int
        
        Returns:
        A tuple with player's account_id and float representing win loss ratio of specified player, 3 decimal places
    """
    if num_days_back:
        player_wl_request = requests.get(f"https://api.opendota.com/api/players/{account_id}/wl?date={num_days_back}").json()
    else:
        player_wl_request = requests.get(f"https://api.opendota.com/api/players/{account_id}/wl?").json()
    
    return((account_id, round(player_wl_request["win"]/player_wl_request["lose"], 3)))

def rank_players_by_wl(accounts_list: list, num_days_back: int=None) -> list:
    """
        Calculates win-loss rate for a list of players given players' account_id's, 
        given as ratio calculated using the following formula - number of wins divided by number of losses, 
        ranked by ratio in descending order
        
        Params:
        account_ids (list) - list of players account_id to check, passed in as int
        
        Returns:
        List of account_ids and win-loss ratio, counted only using matches from "num_days_back" days ago till now,
        sorted by win-loss ratio in descending order
    """
    
    players_ranked_by_wl = []
    
    for account in accounts_list:
        players_ranked_by_wl.append(check_player_wl(account, num_days_back))
    
    return(sorted(players_ranked_by_wl, key=lambda x:x[1], reverse=True))

def list_heroes_game() -> list:
    """
        checks the heroes available in game
        
        Returns:
        list of hero_ids in available in game
    """
    
    heroes = requests.get(f"https://api.opendota.com/api/heroes").json()
    
    return({hero["id"]: hero["localized_name"] for hero in heroes})

def prepare_new_player_dict(list_heroes_game: list):
    """
        Prepare a new empty dictionary to track hero counts for an account
        
        Params:
        list_heroes_game (list) - list of hero_ids available in game
        
        Returns:
        Empty dictionary for newly processed player, with the keys as a distinct hero
    """
    
    return({_:0 for _ in list_heroes_game})

def get_hero_info(hero_id: int) -> list:
    """
        Get two pieces information about a hero, 
        account_id that has played that hero and number of times that account_id has played that hero
        
        Params:
        hero_id (int) - specific hero_id
        
        Returns:
        Returns a list of lists, with each element of the main list being an account_id
        and how many times that account has played that hero
    """
    
    match_info = requests.get(f"https://api.opendota.com/api/heroes/{hero_id}/players").json()
    
    return([[player["account_id"], player["games_played"]] for player in match_info])

# def prepare_data_dict():
#     """
#         Prepare dataset for recommendation system
        
#         Returns:
#         Dictionary with account_id as key, and for each account_id is an inner dictionary with hero_ids as keys
#         , this keeps track of the number of times that account_id has played that hero
#     """
    
#     dataset_dict = {}
#     # all_matches = get_public_matches_samples(num_samples)
    
#     all_heroes_list = list_heroes_game()
    
#     for hero_id in tqdm(all_heroes_list):
#         for account_id, games_played in get_hero_info(hero_id):
#             if account_id not in dataset_dict:
#                 dataset_dict[account_id] = prepare_new_player_dict(all_heroes_list)
#             dataset_dict[account_id][hero_id] += games_played
        
#     return(dataset_dict)

def get_public_matches_samples(query_end_date: date, query_period: int) -> list:
    """
        searches for matches for the past XX days
        
        Params:
        query_date (datetime.date) - date
        
        Returns:
        List of dictionaries, with each dictionary specifying how many times an account has played a hero
    """
    
    query_start_date = query_end_date - timedelta(days=query_period)
    
    query_str = f"""
    SELECT
    player_matches.account_id,
    player_matches.hero_id,
    COUNT(DISTINCT player_matches.match_id)
    FROM matches
    JOIN player_matches using(match_id)
    WHERE matches.start_time > extract(epoch from timestamp '{query_start_date.year}-{query_start_date.month}-{query_start_date.day}T00:00:00.000Z')
    AND matches.start_time <= extract(epoch from timestamp '{query_end_date.year}-{query_end_date.month}-{query_end_date.day}T00:00:00.000Z')
    GROUP BY player_matches.account_id, player_matches.hero_id
    """
    
    sample = requests.get(f"https://api.opendota.com/api/explorer?sql={query_str}").json()
    
    return(sample["rows"])

def prepare_accounts_hero_data(query_period: int=90):
    """
        retrieves match data from matches which started after 'query_period' days ago, but started before today 0000hrs 
        
        Params:
        query_period (int) - number of days back to start collecting match data from
        
        Returns:
        List of dictionaries, with each dictionary specifying how many times an account has played a hero, 
        based on match data retreived
    """
    # dataset_list = []
    all_heroes_list = list_heroes_game()
    hero_played_counts_by_account = get_public_matches_samples(date.today(), query_period)
    
    return(pandas.DataFrame(hero_played_counts_by_account), all_heroes_list)

def get_account_hero_hist(account_id: int, num_days_back: int=90) -> tuple:
    """
        Retrieves 'num_days_back' days worth of match history for given 'account_id', 
        defaults to 90 days
        
        Params:
        account_id (int) - player's account_id to check, passed in as int
        num_days_back (int) - number of days of match data to retrieve
        
        Returns:
        
    """
    
    account_hist_matches = requests.get(f"https://api.opendota.com/api/players/{account_id}/matches?date={num_days_back}").json()
    
    account_dict = {}
    
    for match in account_hist_matches:
        if match["hero_id"] not in account_dict:
            account_dict[match["hero_id"]] = 0
        account_dict[match["hero_id"]] += 1
    
    account_df = pandas.DataFrame([{"account_id":account_id, "hero_id":key , 'count':value} for key, value in account_dict.items()])
    
    account_df["prop_of_matches"] = account_df["count"] / sum(account_df["count"])
    
    return(account_df[["account_id", "hero_id", "prop_of_matches"]])

def recommendation_wrapper(account_id: int, query_period: int=90, min_num_matches: int=30, num_reccs: int=3):
    """
        main wrapper method for hero recommendations
        
        Params:
        account_id (int) - player's account_id to check for historical match data and subsequently recommend heroes for
        query_period (int) - number of days of match data to retrieve
        min_num_matches (int) - will only consider profiles with this minimum number of matches in recommendation matrix
        num_reccs (int) - number of hero recommendations
        
        Returns:
        A list of recommended heroes based on player match history and other player's match history. Will only recommend 
        heroes that have not been played.
    """
    
    
    matches_dataset, hero_list = prepare_accounts_hero_data(query_period)
    
    #removes the account_id to recommend for if it already exists
    matches_dataset = matches_dataset[matches_dataset["account_id"] != account_id]
    
    #removes other account with less than min_num_matches
    removal_set = matches_dataset.groupby("account_id").sum()["count"].reset_index()
    matches_dataset = matches_dataset.merge(removal_set, on='account_id', how='left')
    matches_dataset = matches_dataset[matches_dataset["count_y"] >= min_num_matches]
    
    #calculate proportion of matches that a player selects that hero
    matches_dataset["prop_of_matches"] = matches_dataset["count_x"] / matches_dataset["count_y"]
    matches_dataset = matches_dataset.drop(["count_x", "count_y"], axis=1)
    
    #gets match history of account to predict for
    one_account_hist = get_account_hero_hist(account_id, num_days_back=query_period)
    
    matches_dataset = pandas.concat([matches_dataset, one_account_hist]).reset_index(drop=True)
    
    reader = Reader(rating_scale=(0, 1))
    data = Dataset.load_from_df(matches_dataset, reader)
    final_set = data.build_full_trainset()
    
    sim_options = {'name': 'cosine',
               'user_based': True  # compute  similarities between users
               }

    algo = KNNBasic(sim_options=sim_options)
    algo.fit(final_set)
    
    anti_testset_user = []
    # account to predict for is always the last
    targetUser = max(final_set.all_users())
    #initialise with global mean of matrix
    fillValue = final_set.global_mean
    
    #checks which heroes already played, we only want to recommend heroes that have not been played in that period
    user_item_ratings = final_set.ur[targetUser]
    user_items = [item for (item,_) in (user_item_ratings)]
    
    ratings = final_set.all_ratings()
    for iid in final_set.all_items():
        if(iid not in user_items):
            anti_testset_user.append((final_set.to_raw_uid(targetUser),final_set.to_raw_iid(iid),fillValue))
    
    #get predictions
    predictions = algo.test(anti_testset_user)
    recommendations = sorted([[pred.iid, pred.est] for pred in predictions], key=lambda x:x[1], reverse=True)
    final_reccs = [hero_list[hero[0]] for hero in recommendations[:num_reccs]]
    
    return(final_reccs)