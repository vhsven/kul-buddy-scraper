#%%
import glob
from scraper import scrape_buddies

files = glob.glob('*.html')
dfs = [(file[:-5], scrape_buddies(file)) for file in files]

for date, df in dfs:
    df.to_csv(date + '.csv', index=False, encoding='utf-8')
