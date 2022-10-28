import pandas as pd

badatel = pd.read_csv("src/parsers/badatel/data.csv")
zahadnysvet = pd.read_csv("src/parsers/zahadnysvet/data.csv")
slobodnyvyber = pd.read_csv("src/parsers/slobodnyvyber/data.csv")
skspravy = pd.read_csv("src/parsers/skspravy/data.csv")
extraplus = pd.read_csv("src/parsers/extraplus/data.csv")
inenoviny = pd.read_csv("src/parsers/inenoviny/data.csv")
protiprudu = pd.read_csv("src/parsers/protiprudu/data.csv")
rtvs = pd.read_csv("src/parsers/rtvs/data.csv")
slovenskeslovo = pd.read_csv("src/parsers/slovenskeslovo/data.csv")
ta3 = pd.read_csv("src/parsers/ta3/data.csv")


combined = pd.concat([extraplus, inenoviny, protiprudu, rtvs, slovenskeslovo, ta3, zahadnysvet, slobodnyvyber, skspravy], axis=0, ignore_index=True)
combined.to_csv("LUHAR.csv", index=False)
