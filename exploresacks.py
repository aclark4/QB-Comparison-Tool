import nfl_data_py as nfl

print("Fetching weekly PFR data...")
weekly_data = nfl.import_weekly_pfr(years=[2024], s_type='pass')

print("=== Looking for sack-related columns ===")
sack_columns = [col for col in weekly_data.columns if 'sack' in col.lower()]
print(f"Found {len(sack_columns)} sack-related columns:")
for col in sack_columns:
    print(f"  - {col}")

print("\n=== Looking for pressure-related columns ===")
pressure_columns = [col for col in weekly_data.columns if 'pressure' in col.lower()]
print(f"Found {len(pressure_columns)} pressure-related columns:")
for col in pressure_columns:
    print(f"  - {col}")

print("\n=== All columns (for reference) ===")
print(weekly_data.columns.tolist())
