import pandas as pd
df = pd.read_csv("data/LUHAR.csv")

df.replace({u'\xa0': ' '}, regex=True, inplace=True)
df.replace({u'\xad': '-'}, regex=True, inplace=True)
df.drop_duplicates(inplace=True)

df.to_csv("data/LUHAR.csv")
