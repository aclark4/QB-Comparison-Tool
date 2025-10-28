import nfl_data_py as nfl

print("Fetching play-by-play data for 2024...")
# pbp_data = nfl.import_pbp_data(years=[2024])
ngs_data = nfl.import_ngs_data(stat_type='passing', years=[2024])
# weekly_data = nfl.import_weekly_pfr(years=[2024], s_type='pass')
# ftn_data = nfl.import_ftn_data(years=[2024])

print(ngs_data.columns.tolist())