import nfl_data_py as nfl

print("Fetching play-by-play data for 2024...")
pbp_data = nfl.import_pbp_data(years=[2024])

print("=== LOOKING FOR EPA ===")
epa_cols = [col for col in pbp_data.columns if 'passer' in col.lower()]
print(f"Found {len(epa_cols)} EPA-relate columns:")
for col in epa_cols:
    print(f" - {col}")