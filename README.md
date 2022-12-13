Healint OpenDota take home assignment - Darius

How to use (running as a docker container):
First build the image using the first command in "commands.txt"
Next run a container instance of the images using the second command in "commands.txt"

Example queries for leaderboard:
http://localhost:42744/leaderboard/250544263, 190258756, 237578577, 302429528/2021-12-04
http://localhost:42744/leaderboard/250544263,190258756,237578577,302429528/last_week
http://localhost:42744/leaderboard/250544263,190258756,237578577,302429528/last_month
http://localhost:42744/leaderboard/250544263,190258756,237578577,302429528/last_year
http://localhost:42744/leaderboard/250544263,190258756,237578577,302429528/all_time

Example queries for hero recommender:
http://localhost:42744/hero_recommender/191312823
http://localhost:42744/hero_recommender/237578577

finally, parse the response as a json

<ul>
  <li>1. Tech stack considered</li>
  <ul>
    <li>1. Django for hosting API (i have a little experience with this and given the timeline, it would be harder to learn something else such as fastapi or flask)</li>
    <li>2. requests to query OpenDota API</li>
    <li>3. scikit-surprise library for recommendation</li>
    <li>4. docker for containerisation</li>
    <li>5. jupyter for intermediate workings and exploration</li>
  </ul>
  <li>2. What are some limitations of your application and how do you plan to work around them in the future?
    <ul>
    <li>1. Right now I do not fully understand the data stored in OpenDota's tables. More testing needs to be done to determine if all match data is processed and stored on their tables, or only matches that meet a specific criteria. From my "snooping" around, I saw that the "explorer" feature is supposed to return data only from pro-matches. A few problems here, I do not know what is the exact definition of pro matches. Next, I editted the SQL query running behind the scenes hoping to extract all match data and not just pro matches, more investigation needs to be done to see what was returned.</li>
    <li>2. The application requires that users expose their match history and make the data publicly available. If players do not enable their their account data to be publicly available, the recommendation engine and leaderboard will not work as intended. </li>
    <li>3. Currently the recommendation engine would require that the player has played at least 1 match in order to make hero recommendations. This is similar to the cold start problem (point 8). During my testing I encountered certain profiles which did not have any match history and I got an error. Perhaps this could be treated as a new account and hero recommendations would be made in another way.</li>
    <li>4. Right now, the recommendation engine looks for heroes played by other similar accounts to that account in order to make a hero recommendation for that account, which is a hero that that</li>
    <li>5. The recommendation engine also does not take into account the skill level. If an account is low-skilled, it does not make sense to recommend heroes that are difficult to play such as invoker/meepo.</li>
    <li>6. Explore other methods to prepare the recommendation engine data. The first thing I tried was to try GET /publicMatches, but I realised that in those matches sampled, a lot of the account_ids in the match samples returned was None. The next method tried was to query from /heroes/{hero_id}/players. But I think that one problem with this is that we are not able to specify the match time, as I felt that it would be better to get more recent matches to reflect the heroes that are more played recently. More work need to be done to determine the better way to query historical match data.</li>
    <li>7. Explore other methods to make hero recommendations. Right now we are looking for similar accounts to the provided account for hero recommendations. Instead of looking for other similar accounts, we can look for heroes similar to the ones most played by that account, but not played by that account in the past XX days.</li>
    <li>8. Cold start (related to point 3). If the account is new or does not have any match history in the past XX days, we are not able to make a recommendation. Perhaps for such cases, we could make recommendations based on the top few most popular heroes.</li>
    <li>9. Retrieval of match data from OpenDota each time hero recommendations are requested. Since we are only currently taking matches that started before the current data, it make sense to schedule a cron job (or even airflow for better reliability) to extract match data on a daily basis.</li>
    <li>10. I am not too sure of how to make the api parameters optional (this is for the leaderboard, when we want to find the all-time win-loss of the accounts), some work has to be done there.</li>
    </ul>
  </li>
  <li>3. How would you ensure data required for the application stays up to date?</li>
  <ul>
    <li>Theoretically, the data uitlised should be the latest as each time hero recommendations are requested, data is queried from OpenDota. Within the same day, the query should return the same results, hence it should be a scheduled batch query instead of being executed adhoc each time hero recommendations are requested. However, I also realised that the OpenDota API only works 99% of the time, sometimes the queries just fail but work fine after retrying. It might be necessary to consider querying match data from steam directly.</li>
  </ul>
  <li>4. Why is your recommendation engine a good solution?</li>
  <ul>
    <li>Honestly I feel that the recommendations currently returned could be improved. From my observations, there usually tends to be an overlap of 1/2 heroes between hero recommendations for different account_ids. I think that more experimentation has to be done to determine the optimal parameters when extracting data from open dota - number of days of data to be considered, as well as minimum number of matches. Furthermore, other techniques for making recommendations should be considered also. Popular heros/similar heroes to heroes played by that account.</li>
  </ul>
  <li>5. What are some features you would like to add to the application?</li>
  <ul>
    <li>1. Considered account skill levels when making recommendations.</li>
    <li>2. Option to make hero recommendations based on a certain attribute (i.e. make recommendations based on pro-matches only, ake recommendations based on public matches only)</li>
    <li>3. A feature to check if, this would serve as an indication of how good the recommendations made by the engine are.</li>
    <li>4. Hero recommendation on cosmetics available, if an account has 'expensive' cosmectics for a hero that has not been played in the past XX days, maybe that could be a feature we can consider.</li>
    <li>5. Real-time hero recommendations. Make hero recommendations based on the picks already made on both the home team and enemy team, as well as which side the player is playing on (this matters to a certain extent). The objective of this is to make better recommendations that take into account the context of the match.</li>
    <li>6. Make recommendations based on game patch_id. Changes between patches might make certain heroes more popular and it might be better to make recommendations based on that, currently we are only taking 30 days worth of data.</li>
    <li>7. Take into account the role typically played by that account, that has a large impact on what heroes should be recommended as certain heroes are better suited for certain lanes/roles.</li>
  </ul>
</ul>
