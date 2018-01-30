#%%
import glob
import pandas as pd
import datetime

#%%
def parse_csv(csv):
    date = datetime.datetime.strptime(csv[:-4], '%Y%m%d').date()
    df = pd.read_csv(csv, sep=',', encoding='utf-8')
    df.drop_duplicates(keep='first', inplace=True)
    return (date, df)

csvs = glob.glob('*.csv')
dfs = [parse_csv(csv) for csv in csvs]
dfs

#%%
def merge_dfs(first, second, date):
    merged = first.merge(second, how='outer', indicator=True)
    to_add_index = merged['_merge'] == 'right_only'
    to_remove_index = merged['_merge'] == 'left_only'
    if 'removed' in merged.columns:
        not_yet_removed_index = merged['removed'].isnull()
        to_remove_index = to_remove_index & not_yet_removed_index
    merged.loc[to_add_index, 'added'] = date
    merged.loc[to_remove_index, 'removed'] = date
    merged.drop('_merge', axis=1, inplace=True)
    return merged

#%%
_, merged = dfs[0]
for i in range(1, len(dfs)):
    date, df = dfs[i]
    merged = merge_dfs(merged, df, date)

merged

#%%
merged.to_excel('merged.xlsx', index=False, encoding='utf-8')