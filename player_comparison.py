import sys
import subprocess


def install_if_missing(package):
    # Install package if not found
    try:
        __import__(package)
    except ImportError:
        print(f"\n{package} not found. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
        print(f"{package} installed successfully!\n")

required_packages = ['nfl_data_py', 'pandas']
for package in required_packages:
    install_if_missing(package)

import nfl_data_py as nfl
import pandas as pd


print("Loading NFL QB Data...")
ngs_data = nfl.import_ngs_data(stat_type='passing', years=[2024])
ngs_rushing_data = nfl.import_ngs_data(stat_type='rushing', years=[2024])
seasonal_pfr = nfl.import_seasonal_pfr(years=[2024], s_type='pass')
weekly_data = nfl.import_weekly_pfr(years=[2024], s_type='pass')
pbp_data = nfl.import_pbp_data(years=[2024])
ftn_data = nfl.import_ftn_data(years=[2024])
seasonal_data = nfl.import_seasonal_data(years=[2024])

player_ids = nfl.import_ids()

seasonal_data = seasonal_data.merge(
    player_ids[['gsis_id', 'name']],
    left_on='player_id',
    right_on='gsis_id',
    how='left'
)



print("Data Loaded!")

def format_name_pbp_passer(qb_name):
    # Turns a qb full name in the valid input for pbp data comparison Ex: P.Mahomes if Patrick Mahomes was input
    parts = qb_name.strip().split()
    if len(parts) < 2:
        return None # Invalid input given
    
    first_initial = parts[0][0].upper()
    last_name = parts[-1].title()

    return f"{first_initial}.{last_name}"

def calculate_qb_epa_play(seasonal_qb):
    # Calculate the average EPA per play for the given QB over the 2024 NFL season from the play-by-play data
    total_epa = seasonal_qb['rushing_epa'].values[0] + seasonal_qb['passing_epa'].values[0]
    total_plays = seasonal_qb['attempts'].values[0] + seasonal_qb['carries'].values[0]
    # Calculate average EPA here
    return (total_epa / total_plays)

def pressure_to_sack_percentage(qb_name, weekly_qb):
    # Calculates the pressure to sack ratio for a qb
    qb_weekly = weekly_qb[(weekly_qb['game_type'] == 'REG')]
    times_sacked = qb_weekly['times_sacked'].sum()
    times_pressured = qb_weekly['times_pressured'].sum()

    if times_pressured == 0:
        return 0

    return (times_sacked/times_pressured) * 100

def get_qb_throwaways_and_spikes(pbp_qb, ftn_qb):

    spikes = len(pbp_qb[pbp_qb['qb_spike'] == 1])
    throwaways = len(ftn_qb[ftn_qb['is_throw_away'] == 1])

    return spikes + throwaways

# I realized that pfr seasonal data had this stat built in, and I never even had to spend time on this. Keeping for reference in case I need ftn stat pulling format.
def calculate_bad_throw_pct(weekly_qb, ngs_qb, pbp_qb, ftn_qb):
    # Calculates the season long bad throw percentage from each individual week (Excluding postseason stats)

    bad_throws = 0
    for value in weekly_qb['passing_bad_throws']:
        bad_throws += value
    
    
    attempts = ngs_qb['attempts'].values[0]
    throwaways_spikes = get_qb_throwaways_and_spikes(pbp_qb, ftn_qb)
    return (bad_throws/(attempts - throwaways_spikes)) * 100


def get_qb_stats(qb_name, pbp_data):

    ngs_qb = ngs_data[(ngs_data['player_display_name'].str.lower() == qb_name.lower()) &
        (ngs_data['season_type'] == 'REG')
    ]

    if ngs_qb.empty:
        print(f"{qb_name} is not a valid player.(ngs)")
        return -1

    seasonal_pfr_qb = seasonal_pfr[(seasonal_pfr['player'].str.lower() == qb_name.lower())]

    if seasonal_pfr_qb.empty:
        print(f"{qb_name} is not a valid player.(seasonal_pfr)")
        return -1

    seasonal_qb = seasonal_data[(seasonal_data['name'].str.lower() == qb_name.lower()) &
        (seasonal_data['season_type'] == 'REG')
    ]

    if seasonal_qb.empty:
        print(f"{qb_name} is not a valid player.(seasonal)")
        return -1

    weekly_qb = weekly_data[(weekly_data['pfr_player_name'].str.lower() == qb_name.lower()) &
        (weekly_data['game_type'] == 'REG')
    ]

    if weekly_qb.empty:
        print(f"{qb_name} is not a valid player.(weekly)")
        return -1


    pbp_qb = pbp_data[(pbp_data['passer_player_name'] == format_name_pbp_passer(qb_name)) &
        (pbp_data['season_type'] == 'REG')
    ]

    
    if pbp_qb.empty:
        print(f"{qb_name} is not a valid player.(pbp)")
        return -1

    

    ftn_qb = ftn_data.merge(
        pbp_qb[['nflverse_game_id', 'play_id']], 
        left_on=['nflverse_game_id', 'nflverse_play_id'],
        right_on=['nflverse_game_id', 'play_id'],
        how='inner'
    )

    times_sacked = weekly_qb['times_sacked'].sum()
    times_pressured = weekly_qb['times_pressured'].sum()

    stats = {
        'name': qb_name,
        'games_played': len(weekly_qb),
        'passer_rating': ngs_qb['passer_rating'].values[0],
        'pass_attempts': ngs_qb['attempts'].values[0],
        'pass_yards': ngs_qb['pass_yards'].values[0],
        'rush_yards': seasonal_qb['rushing_yards'].values[0],
        'rush_attempts': seasonal_qb['carries'].values[0],
        'pass_touchdowns': ngs_qb['pass_touchdowns'].values[0],
        'rush_touchdowns': seasonal_qb['rushing_tds'].values[0],
        'interceptions': ngs_qb['interceptions'].values[0],
        'completion_percentage': round(ngs_qb['completion_percentage'].values[0],1),
        'completion_percentage_above_expectation': round(ngs_qb['completion_percentage_above_expectation'].values[0], 1),
        'aggressiveness': round(ngs_qb['aggressiveness'].values[0], 1),
        'pressure_to_sack_percentage': round((times_sacked/times_pressured) * 100, 1),
        'epa_play': round(calculate_qb_epa_play(seasonal_qb), 2),
        'bad_throw_pct_average': round(seasonal_pfr_qb['bad_throw_pct'].values[0], 3),
        'sacks_taken': seasonal_qb['sacks'].values[0],
        'turnover_worthy_passes': ftn_qb['is_interception_worthy'].sum(),
        'turnover_worthy_throw_rate': round((ftn_qb['is_interception_worthy'].sum()/ngs_qb['attempts'].values[0]) * 100, 1),
        'avg_depth_of_target': round(seasonal_pfr_qb['intended_air_yards_per_pass_attempt'].values[0], 1),
        'yards_per_attempt': round(ngs_qb['pass_yards'].values[0]/ngs_qb['attempts'].values[0], 1),
        'avg_time_to_throw': round(ngs_qb['avg_time_to_throw'].values[0], 2),
        'fumbles_lost': seasonal_qb['rushing_fumbles_lost'].values[0] + seasonal_qb['sack_fumbles_lost'].values[0],
        'dakota': seasonal_qb['dakota'].values[0]

    }

    return stats

def generate_qb_score(stats):
    score = 0
    yards_score = (((stats['pass_yards'] + stats['rush_yards'])/stats['games_played']) - 250) / 2 # 250 yards is an 'average' game in 2024.
    touchdown_score = (stats['pass_touchdowns'] + stats['rush_touchdowns'])/(stats['pass_attempts'] + stats['rush_attempts']) * 200 # Rate of a touchdown scored on a given rush or pass from the QB, then weighted for importance with * 500, since the rate will be a very lower number relative to other scores
    turnover_score = (stats['turnover_worthy_passes'] / stats['interceptions']) / stats['bad_throw_pct_average'] - stats['fumbles_lost'] - stats['interceptions']
    aggressiveness_score = (stats['avg_depth_of_target'] - 7.5) * stats['aggressiveness']
    time_to_throw_score = (stats['avg_time_to_throw'] - 2.5)
    if time_to_throw_score > 0:
        (time_to_throw_score * 10) ** 2
    else:
        time_to_throw_score = -((time_to_throw_score * 10) ** 2)
    pressure_to_sack_score = stats['pressure_to_sack_percentage'] / stats['avg_time_to_throw']
    ''' scoring algorithm print information
    print(f"yards score: {yards_score}")
    print(f"td score: {touchdown_score}")
    print(f"turnover score: {turnover_score}")
    print(f"agg score: {aggressiveness_score}")
    print(f"ttt score: {time_to_throw_score}")
    print(f"pts score: {pressure_to_sack_score}")
    print(f"cpoe: {stats['completion_percentage_above_expectation']}")
    print(f"epa/play: {stats['epa_play']}")
    '''
    score = (yards_score * .15) + (touchdown_score * .2) + (turnover_score * .15) + (aggressiveness_score * .05) + ((stats['epa_play'] * 30) * .25) + (time_to_throw_score * .05) + (pressure_to_sack_score * .15) - (stats['sacks_taken'] * .1) + (stats['completion_percentage_above_expectation'] * .1)
    return round(score, 2)

def output_stats(qb1_stats, qb2_stats):
    print(f"QB Stat Comparison: ")
    print(f"{'Name:':<35}{qb1_stats['name']:<25}{qb2_stats['name']} ")
    print(f"{'Passing Yards:':<35}{qb1_stats['pass_yards']:<25}{qb2_stats['pass_yards']} ")
    print(f"{'Passing Touchdowns:':<35}{qb1_stats['pass_touchdowns']:<25}{qb2_stats['pass_touchdowns']} ")
    print(f"{'Interceptions:':<35}{qb1_stats['interceptions']:<25}{qb2_stats['interceptions']} ")
    print(f"{'Completion Percentage:':<35}{qb1_stats['completion_percentage']:<25}{qb2_stats['completion_percentage']} ")
    print(f"{'EPA/Play:':<35}{qb1_stats['epa_play']:<25}{qb2_stats['epa_play']} ")
    print(f"{'Rushing Yards:':<35}{qb1_stats['rush_yards']:<25}{qb2_stats['rush_yards']} ")
    print(f"{'Rushing Touchdowns:':<35}{qb1_stats['rush_touchdowns']:<25}{qb2_stats['rush_touchdowns']} ")
    print(f"{'Turnover Worthy Throws:':<35}{qb1_stats['turnover_worthy_passes']:<25}{qb2_stats['turnover_worthy_passes']} ")
    print(f"{'Bad Throw Rate:':<35}{qb1_stats['bad_throw_pct_average']:<25}{qb2_stats['bad_throw_pct_average']} ")
    print(f"{'Average Depth of Target:':<35}{qb1_stats['avg_depth_of_target']:<25}{qb2_stats['avg_depth_of_target']} ")
    print(f"{'Sacks:':<35}{qb1_stats['sacks_taken']:<25}{qb2_stats['sacks_taken']} ")
    print(f"{'Pressure to Sack Percentage:':<35}{qb1_stats['pressure_to_sack_percentage']:<25}{qb2_stats['pressure_to_sack_percentage']} ")
    print(f"{'Average Time to Throw:':<35}{qb1_stats['avg_time_to_throw']:<25}{qb2_stats['avg_time_to_throw']} ")
    print()

    
    return 1

qb1, qb2, qb1_stats, qb2_stats = "", "", -1, -1 # Default values

while (qb1_stats == -1):
    qb1 = input("Enter the first Quarterback: ").title()
    qb1_stats = get_qb_stats(qb1, pbp_data)

while (qb2_stats == -1):
    qb2 = input("Enter the second Quarterback: ").title()
    if (qb1.lower() == qb2.lower()):
        print("You entered the same quarterback twice!")
        continue
    qb2_stats = get_qb_stats(qb2, pbp_data)


print(f"Generating {qb1}'s score...")
qb1_score = generate_qb_score(qb1_stats)
print(f"Generating {qb2}'s score...")
qb2_score = generate_qb_score(qb2_stats)

if qb1_score > qb2_score:
    print(f"{qb1} scores higher than {qb2} according to my algorithm!")
    print(f"{qb1} had a score of {qb1_score}, and {qb2} had a score of {qb2_score}")
elif qb2_score > qb1_score:
    print(f"{qb2} scores higher than {qb1} according to my algorithm!")
    print(f"{qb1} had a score of {qb1_score}, and {qb2} had a score of {qb2_score}")
else:
    print(f"WOW! They both got the same score of {qb2_score}")

input = input(f"Type 'y' if you would like to see a stat comparison between the {qb1} and {qb2}: ").lower()
if input == 'y':
    print("made it")
    output_stats(qb1_stats, qb2_stats)

print("Thanks for using my 2024 QB Comparison Tool!")

    