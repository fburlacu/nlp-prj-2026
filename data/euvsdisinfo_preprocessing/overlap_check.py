import pandas as pd, re

eeas = pd.read_csv("euvsdisinfo_debunks.csv").dropna(subset=["Title", "Information"])
tok = lambda s: set(re.findall(r"[a-z]{3,}", s.lower()))
T, D = eeas["Title"].map(tok), eeas["Information"].map(tok)
own = [len(t & d) / max(len(t), 1) for t, d in zip(T, D)]
rnd = [len(t & d) / max(len(t), 1) for t, d in zip(T, D.sample(frac=1, random_state=0))]
print(f"title words found in own disproof: {pd.Series(own).mean():.2f} | in a random disproof: {pd.Series(rnd).mean():.2f}")
eeas["overlap"] = own
eeas["overlap_bin"] = pd.qcut(eeas["overlap"], 3, labels=["low", "mid", "high"])
print(eeas.groupby("overlap_bin", observed=True)["overlap"].agg(["min", "max", "count"]))
eeas["disproof_len"] = eeas["Information"].str.split().str.len()
print(eeas.groupby("overlap_bin", observed=True)["disproof_len"].median())
print("overlap 0:", (eeas["overlap"] == 0).sum(), "| overlap 1:", (eeas["overlap"] == 1).sum())
print(eeas.loc[eeas["overlap"] == 0, ["Title", "Information"]].head(5).to_string())