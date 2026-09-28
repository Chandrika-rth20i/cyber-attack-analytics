import pandas as pd, numpy as np, glob, os, json

cols = ["Protocol", "Flow Duration", "Total Fwd Packets",
        "Total Backward Packets", "Label"]

frames = []
for f in glob.glob("data/*.parquet"):
    d = pd.read_parquet(f, columns=cols)
    d["Day"] = os.path.basename(f).split("-")[1]
    frames.append(d)
    print("loaded", f)

df = pd.concat(frames, ignore_index=True)
raw_rows = len(df)

# ---- cleaning ----
df["Label"] = df["Label"].astype(str).str.strip(); df["Label"] = df["Label"].str.encode("latin1", errors="ignore").str.decode("utf-8", errors="ignore"); df["Label"] = df["Label"].str.replace(r"\s*\W\s*", " - ", regex=True).str.strip()
df = df.replace([np.inf, -np.inf], np.nan)
missing = int(df.isna().any(axis=1).sum())
df = df.dropna()
dups = int(df.duplicated().sum())
df = df.drop_duplicates()

df["Total Packets"] = df["Total Fwd Packets"] + df["Total Backward Packets"]
names = {0: "HOPOPT", 1: "ICMP", 6: "TCP", 17: "UDP"}
df["Proto"] = df["Protocol"].map(names).fillna("Other")

attacks = df[df["Label"] != "Benign"]

out = {
    "kpis": {
        "total_flows": len(df),
        "attack_flows": len(attacks),
        "benign_flows": len(df) - len(attacks),
        "attack_types": int(attacks["Label"].nunique()),
    },
    "cleaning": {"raw_rows": raw_rows, "missing_or_inf_removed": missing,
                 "duplicates_removed": dups, "final_rows": len(df)},
    "labels": df["Label"].value_counts().to_dict(),
    "by_day": pd.crosstab(df["Day"], df["Label"]).to_dict("index"),
    "by_protocol": pd.crosstab(df["Proto"], df["Label"]).to_dict("index"),
    "avg_duration": df.groupby("Label")["Flow Duration"].mean().round(0).to_dict(),
    "avg_packets": df.groupby("Label")["Total Packets"].mean().round(1).to_dict(),
}

sample = df.groupby("Label", group_keys=False)[df.columns].apply(lambda g: g.sample(min(len(g), 25), random_state=1)).reset_index(drop=True)
out["records"] = sample[["Day","Proto","Total Packets","Flow Duration","Label"]].rename(
    columns={"Proto":"Protocol","Total Packets":"Packets","Flow Duration":"Duration"}
).to_dict("records")

with open("data.json", "w") as fp:
    json.dump(out, fp, indent=2,
              default=lambda o: o.item() if hasattr(o, "item") else str(o))

print()
print("DONE. data.json created")
print(out["kpis"])
print(out["cleaning"])
print(out["labels"])


