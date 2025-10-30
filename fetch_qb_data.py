import nfl_data_py as nfl


ngs_data = nfl.import_ngs_data(stat_type='passing', years=[2024])
weekly_data = nfl.import_weekly_pfr(years=[2024], s_type='pass')
ftn_data = nfl.import_ftn_data(years=[2024])
seasonal_data_pfr = nfl.import_seasonal_pfr(years=[2024], s_type='pass')
ngs_rushing_data = nfl.import_ngs_data(stat_type='rushing', years=[2024])
seasonal_data = nfl.import_seasonal_data(years=[2024])
player_ids = nfl.import_ids()

print(seasonal_data_pfr.columns.tolist())

'''
players = nfl.import_players()

print(players.columns.tolist())


#Grabs the QB stats from the 2025 season
print("Fetching 2024 Season QB Data....")
seasonal_data = nfl.import_seasonal_data(years=[2024])


print("2025 seasonal data:")
print(seasonal_data.columns.tolist())


print(seasonal_data.head())
print(seasonal_data[['player_id', 'passing_yards', 'passing_tds', 'interceptions', 'passing_epa']].head(5))
'''
