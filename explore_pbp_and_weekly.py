import nfl_data_py as nfl

print("Fetching play-by-play data for 2024...")
pbp_data = nfl.import_pbp_data(years=[2024])

print("=== LOOKING AT COLUMNS OF PBP DATA ===")
for col in pbp_data.columns:
    print(f" - {col}")

if 'qb_spike' in pbp_data.columns:
    print("\nUnique play_type values:")
    print(pbp_data['qb_spike'].unique())