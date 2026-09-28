import pandas as pd

df = pd.read_parquet("data/DDoS-Friday-no-metadata.parquet")
sample = df.sample(min(len(df), 500), random_state=1)
sample.to_csv("test_upload.csv", index=False)
print("Saved test_upload.csv with", len(sample), "rows")
