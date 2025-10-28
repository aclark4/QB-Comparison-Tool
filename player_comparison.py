import nfl_data_py as nfl
import pandas as pd


print("Loading NFL QB Data...")
ngs_data = nfl.import_ngs_data(stat_type='passing', years=[2024])
seasonal_data = nfl.import_seasonal_data(years=[2024])
weekly_data = nfl.import_weekly_pfr(years=[2024], s_type='pass')
pbp_data = nfl.import_pbp_data(years=[2024])

print("Data Loaded!")

def format_name_pbp_passer(qb_name):
    # Turns a qb full name in the valid input for pbp data comparison Ex: P.Mahomes if Patrick Mahomes was input
    parts = qb_name.strip().split()
    if len(parts) < 2:
        return None # Invalid input given
    
    first_initial = parts[0][0]
    last_name = parts[-1]

    return f"{first_initial}.{last_name}"

def calculate_qb_epa_play(qb_name, pbp_data):
    # Calculate the average EPA per play for the given QB over the 2024 NFL season from the play-by-play data
    qb_passing_plays = pbp_data[pbp_data['season_type'] == 'REG']
    qb_rushing_plays = pbp_data[pbp_data['season_type'] == 'REG']
    
    all_plays = pd.concat([qb_passing_plays, qb_rushing_plays])
    
    if all_plays.empty:
        return None

    # Calculate average EPA here (Exclude the plays with no EPA value)
    return all_plays['qb_epa'].dropna().mean()

def pressure_to_sack_percentage(qb_name, weekly_qb):
    # Calculates the pressure to sack ratio for a qb
    qb_weekly = weekly_data[(weekly_data['game_type'] == 'REG')]
    times_sacked = qb_weekly['times_sacked'].sum()
    times_pressured = qb_weekly['times_pressured'].sum()

    if times_pressured == 0:
        return 0

    return (times_sacked/times_pressured) * 100

def get_qb_throwaways_and_spikes(qb_name, pbp_qb):
    spikes = len(pbp_qb['qb_spike'] == 1)

    print("Here is the spikes!")
    print(spikes)
    return spikes

def calculate_bad_throw_pct(qb_name, weekly_data, ngs_qb, pbp_qb):
    # Calculates the season long bad throw percentage from each individual week (Excluding postseason stats)
    qb_weekly = weekly_data[(weekly_data['game_type'] == 'REG')]

    if qb_weekly.empty: 
        return None

    bad_throws = 0
    for value in qb_weekly['passing_bad_throws']:
        bad_throws += value
    
    attempts = ngs_qb['attempts'].values[0]
    print("HEREEE")
    throwaways_spikes = get_qb_throwaways_and_spikes(qb_name, pbp_qb)
    return "Done"


def get_qb_stats(qb_name):

    ngs_qb = ngs_data[ngs_data['player_display_name'].str.lower() == qb_name.lower()]

    if ngs_qb.empty:
        return f"{qb_name} is not a valid player."

    weekly_qb = weekly_data[weekly_data['pfr_player_name'].str.lower() == qb_name.lower()]

    if weekly_qb.empty:
        return None

    pbp_qb = pbp_data[pbp_data['passer_player_name'].str.lower() == qb_name.lower()]
    
    if pbp_qb.empty:
        print("EMPTY")
        return None

    stats = {
        'passer_rating': ngs_qb['passer_rating'].values[0],
        'pass_yards': ngs_qb['pass_yards'].values[0],
        'pass_touchdowns': ngs_qb['pass_touchdowns'].values[0],
        'interceptions': ngs_qb['interceptions'].values[0],
        'completion_percentage': ngs_qb['completion_percentage'].values[0],
        'completion_percentage_above_expectation': ngs_qb['completion_percentage_above_expectation'].values[0],
        'aggressiveness': ngs_qb['aggressiveness'].values[0],
        'pressure_to_sack_percentage': pressure_to_sack_percentage(qb_name, weekly_qb),
        'epa_play': calculate_qb_epa_play(qb_name, pbp_data),
        'bad_throw_pct': calculate_bad_throw_pct(qb_name, weekly_qb, ngs_qb)

    }

    #print(f"2024 Stats for {qb_name}")
    """for stat, value in stats.items():
        print(f"{stat}: {value}")"""
    
    return print(stats['bad_throw_pct'])

#qb1 = input("Enter the first Quarterback: ") 
print(get_qb_stats("Justin Fields"))