import nfl_data_py as nfl


ngs_data = nfl.import_ngs_data(stat_type='passing', years=[2024])
weekly_data = nfl.import_weekly_pfr(years=[2024], s_type='pass')

for col in ngs_data.columns:
    print(f"  - {col}")

if 'spike' in weekly_data.columns:
    print("\nUnique pass values:")
    print(weekly_data['pass'].unique())
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
