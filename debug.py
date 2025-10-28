import nfl_data_py as nfl

print("Fetching play-by-play data...")
pbp_data = nfl.import_pbp_data(years=[2024])
ngs_data = nfl.import_ngs_data(stat_type='passing', years=[2024])
weekly_data = nfl.import_weekly_pfr(years=[2024], s_type='pass')
ftn_data = nfl.import_ftn_data(years=[2024])

def format_name_pbp_passer(qb_name):
    # Turns a qb full name in the valid input for pbp data comparison Ex: P.Mahomes if Patrick Mahomes was input
    parts = qb_name.strip().split()
    if len(parts) < 2:
        return None # Invalid input given
    
    first_initial = parts[0][0]
    last_name = parts[-1]

    return f"{first_initial}.{last_name}"

def get_qb_stats(qb_name):

    ngs_qb = ngs_data[ngs_data['player_display_name'].str.lower() == qb_name.lower()]

    if ngs_qb.empty:
        return f"{qb_name} is not a valid player."

    weekly_qb = weekly_data[weekly_data['pfr_player_name'].str.lower() == qb_name.lower()]

    if weekly_qb.empty:
        return None

    pbp_name = format_name_pbp_passer(qb_name)
    
    if pbp_name is None:
        print("Invalid name format")
        return None
    
    pbp_qb = pbp_data[pbp_data['passer_player_name'] == pbp_name]
    
    if pbp_qb.empty:
        print(f"EMPTY - Looking for: {pbp_name}")
        return None
    
    # Try merging on nflverse_game_id + play_id
    print("\n=== ATTEMPTING MERGE ===")
    
    # Check if both have the play_id column
    print(f"PBP has 'play_id': {'play_id' in pbp_qb.columns}")
    print(f"FTN has 'ftn_play_id': {'ftn_play_id' in ftn_data.columns}")
    print(f"Both have 'nflverse_game_id': {'nflverse_game_id' in pbp_qb.columns and 'nflverse_game_id' in ftn_data.columns}")
    
    # Attempt merge
    ftn_qb = ftn_data.merge(
        pbp_qb[['nflverse_game_id', 'play_id']], 
        left_on=['nflverse_game_id', 'ftn_play_id'],
        right_on=['nflverse_game_id', 'play_id'],
        how='inner'
    )
    
    print(f"Merge result: {len(ftn_qb)} plays matched")
    print(f"PBP had {len(pbp_qb)} plays")
    print(f"Match rate: {len(ftn_qb)/len(pbp_qb)*100:.1f}%")
    
    if len(ftn_qb) == 0:
        print("WARNING: No plays matched! Checking why...")
        print("\nSample PBP values:")
        print(pbp_qb[['nflverse_game_id', 'play_id']].head(3))
        print("\nSample FTN values:")
        print(ftn_data[['nflverse_play_id', 'ftn_play_id']].head(3))
        return "Debug - no merge matches"
    
    print("=== MERGE SUCCESSFUL ===\n")
    
    # Continue with stats...
    stats = {
        'passer_rating': ngs_qb['passer_rating'].values[0],
        'pass_yards': ngs_qb['pass_yards'].values[0],
        'pass_touchdowns': ngs_qb['pass_touchdowns'].values[0],
        'interceptions': ngs_qb['interceptions'].values[0],
        'completion_percentage': ngs_qb['completion_percentage'].values[0],
        'completion_percentage_above_expectation': ngs_qb['completion_percentage_above_expectation'].values[0],
        'aggressiveness': ngs_qb['aggressiveness'].values[0],
    }

    print(f"2024 Stats for {qb_name}")
    for stat, value in stats.items():
        print(f"{stat}: {value}")
    
    return stats

get_qb_stats("Justin Fields")