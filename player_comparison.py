import nfl_data_py as nfl
import pandas as pb


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
    qb_plays = pbp_data[pbp_data['passer'].str.lower() == format_name_pbp_passer(qb_name).lower()]

    if qb_plays.empty:
        return None

    # Calculate average EPA here (Exclude the plays with no EPA value)
    valid_plays = qb_plays[qb_plays['qb_epa'].notna()]
    return valid_plays['qb_epa'].mean()

def pressure_to_sack_percentage(qb_name, weekly_qb):
    # Calculates the pressure to sack ratio for a qb
    times_sacked = weekly_qb['times_sacked'].sum()
    times_pressured = weekly_qb['times_pressured'].sum()

    if times_pressured == 0:
        return 0

    return (times_sacked/times_pressured) * 100

def get_qb_stats(qb_name):
    ngs_qb = ngs_data[ngs_data['player_display_name'].str.lower() == qb_name.lower()]

    if ngs_qb.empty:
        return f"{qb_name} is not a valid player."

    weekly_qb = weekly_data[weekly_data['pfr_player_name'].str.lower() == qb_name.lower()]

    if weekly_qb.empty:
        return None

    stats = {
        'name': qb_name,
        'passer_rating': ngs_qb['passer_rating'].values[0],
        'pass_yards': ngs_qb['pass_yards'].values[0],
        'pass_touchdowns': ngs_qb['pass_touchdowns'].values[0],
        'interceptions': ngs_qb['interceptions'].values[0],
        'completion_percentage': ngs_qb['completion_percentage'].values[0],
        'completion_percentage_above_expectation': ngs_qb['completion_percentage_above_expectation'].values[0],
        'aggressiveness': ngs_qb['aggressiveness'].values[0],
        'pressure_to_sack_percentage': pressure_to_sack_percentage(qb_name, weekly_qb)


    }
    return pressure_to_sack_percentage(qb_name, weekly_qb)

print(get_qb_stats('Lamar Jackson'))