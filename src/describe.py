import pandas as pd

luhar = pd.read_csv("LUHAR.csv")

print(f"Total rows: {luhar.shape[0]}")

print("Label information")
print(luhar["label"].value_counts())
