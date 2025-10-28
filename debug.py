import nfl_data_py as nfl

print("Fetching play-by-play data...")
pbp_data = nfl.import_pbp_data(years=[2024])

print("=== Sample passer names in PBP data ===")
for col in pbp_data.columns:
    if 'season' in col.lower() or 'game' in col.lower():
        print(f" - {col}")

if 'season_type' in pbp_data.columns:
    print("\nUnique season_type values:")
    print(pbp_data['season_type'].unique())