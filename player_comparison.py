import nfl_data_py as nfl
import pandas as pd


print("Loading NFL QB Data...")
ngs_data = nfl.import_ngs_data(stat_type='passing', years=[2024])
seasonal_data = nfl.import_seasonal_pfr(years=[2024], s_type='pass')
weekly_data = nfl.import_weekly_pfr(years=[2024], s_type='pass')
pbp_data = nfl.import_pbp_data(years=[2024])
ftn_data = nfl.import_ftn_data(years=[2024])

print("Data Loaded!")

def format_name_pbp_passer(qb_name):
    # Turns a qb full name in the valid input for pbp data comparison Ex: P.Mahomes if Patrick Mahomes was input
    parts = qb_name.strip().split()
    if len(parts) < 2:
        return None # Invalid input given
    
    first_initial = parts[0][0].upper()
    last_name = parts[-1].title()

    return f"{first_initial}.{last_name}"

def calculate_qb_epa_play(qb_name, pbp_data):
    # Calculate the average EPA per play for the given QB over the 2024 NFL season from the play-by-play data
    name = format_name_pbp_passer(qb_name)
    qb_plays = pbp_data[
        (
            (pbp_data['passer_player_name'] == name) |
            (pbp_data['rusher_player_name'] == name) # Consider when the QB runs!
        ) &
        (pbp_data['season_type'] == 'REG')
    ]

    total_epa = qb_plays['qb_epa'].sum()
    total_plays = len(qb_plays)
    # Calculate average EPA here
    return total_epa / total_plays

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

    seasonal_qb = seasonal_data[(seasonal_data['player'].str.lower() == qb_name.lower())]

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

    qb_weekly = weekly_qb[(weekly_qb['game_type'] == 'REG')]
    times_sacked = qb_weekly['times_sacked'].sum()
    times_pressured = qb_weekly['times_pressured'].sum()

    stats = {
        'passer_rating': ngs_qb['passer_rating'].values[0],
        'pass_yards': ngs_qb['pass_yards'].values[0],
        'pass_touchdowns': ngs_qb['pass_touchdowns'].values[0],
        'interceptions': ngs_qb['interceptions'].values[0],
        'completion_percentage': ngs_qb['completion_percentage'].values[0],
        'completion_percentage_above_expectation': round(ngs_qb['completion_percentage_above_expectation'].values[0], 1),
        'aggressiveness': round(ngs_qb['aggressiveness'].values[0], 1),
        'pressure_to_sack_percentage': round((times_sacked/times_pressured) * 100, 1),
        'epa_play': round(calculate_qb_epa_play(qb_name, pbp_data), 3),
        'bad_throw_pct_average': round(seasonal_qb['bad_throw_pct'].values[0], 3),
        'sacks_taken': times_sacked,
        'turnover_worthy_passes': ftn_qb['is_interception_worthy'].sum(),
        'turnover_worthy_throw_rate': round((ftn_qb['is_interception_worthy'].sum()/ngs_qb['attempts'].values[0]) * 100, 1),
        'avg_depth_of_target': round(seasonal_qb['intended_air_yards_per_pass_attempt'].values[0], 1),
        'yards_per_attempt': round(ngs_qb['pass_yards'].values[0]/ngs_qb['attempts'].values[0], 1)

    }
    
    return stats

def generate_qb_score(stats):
    return 1;

qb1, qb2, qb1_stats, qb2_stats = "", "", -1, -1 # Default values

while (qb1_stats == -1):
    qb1 = input("Enter the first Quarterback: ") 
    qb1_stats = get_qb_stats(qb1, pbp_data)

while (qb2_stats == -1):
    qb2 = input("Enter the second Quarterback: ") 
    if (qb1.lower() == qb2.lower()):
        print("You entered the same quarterback twice!")
        continue
    qb2_stats = get_qb_stats(qb2, pbp_data)


print(f"Generating {qb1}'s score...")
qb1_score = generate_qb_score(qb1)
print(f"Generating {qb2}'s score...")
qb2_score = generate_qb_score(qb2)

if qb1_score > qb2_score:
    print(f"{qb1} scores higher than {qb2} according to my algorithm!")
elif qb2_score > qb1_score:
    print(f"{qb2} scores higher than {qb1} according to my algorithm!")
else:
    print(f"WOW! They both got the same score of {qb2_score}")

    