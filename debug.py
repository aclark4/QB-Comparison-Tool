import nfl_data_py as nfl

print("Fetching play-by-play data...")
pbp_data = nfl.import_pbp_data(years=[2024])

print("=== Sample passer names in PBP data ===")
passers = pbp_data['passer'].dropna().unique()
print(f"Total unique passers: {len(passers)}")
print("First 15 passer names:")
for name in list(passers)[:15]:
    print(f"  - {name}")

print("\n=== Check if qb_epa column exists ===")
print("'qb_epa' in columns:", 'qb_epa' in pbp_data.columns)

print("\n=== Check for Patrick Mahomes specifically ===")
mahomes_plays = pbp_data[pbp_data['passer'].str.contains('Mahomes', case=False, na=False)]
print(f"Plays with 'Mahomes': {len(mahomes_plays)}")
if len(mahomes_plays) > 0:
    print("Sample passer names from Mahomes plays:")
    print(mahomes_plays['passer'].unique()[:5])