import pandas as pd
import glob

files = glob.glob("data/*.parquet")

for f in files:
    df = pd.read_parquet(f)
    print(f, df.shape)

print()
print("COLUMNS:")
print(list(df.columns))
print()
print(df.head(3).T)
