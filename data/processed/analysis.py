import argparse
import pandas as pd
from scipy import stats
import os

def analyze(infile, outfile, statsfile):
    df = pd.read_csv(infile)
    # Drop invalids
    df_valid = df[df['valid'] == 1]

    # Compute group means
    summary = df_valid.groupby(['temp', 'pH'])['latency_ms'].agg(['mean', 'std', 'count']).reset_index()

    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    summary.to_csv(outfile, index=False)

    # simple ANOVA across temps for each pH
    with open(statsfile, "w") as f:
        for pH in sorted(df['pH'].unique()):
            group = [df_valid[(df_valid['pH']==pH) & (df_valid['temp']==T)]['latency_ms'].dropna()
                     for T in sorted(df['temp'].unique())]
            if all(len(g) > 1 for g in group):
                F, p = stats.f_oneway(*group)
                f.write(f"pH={pH}: ANOVA F={F:.3f}, p={p:.3e}\n")

    print(f"Analysis complete. Summary -> {outfile}, Stats -> {statsfile}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", type=str, default="data/raw/sim_raw_trials.csv")
    parser.add_argument("--outfile", type=str, default="data/processed/summary_stats.csv")
    parser.add_argument("--statsfile", type=str, default="stats/anova_results.txt")
    args = parser.parse_args()
    analyze(infile=args.infile, outfile=args.outfile, statsfile=args.statsfile)

cat > code/analysis.py <<'PY'
import argparse, pandas as pd, numpy as np, os
from scipy import stats

def analyze(infile="data/raw/sim_raw_trials.csv",
            outfile="data/processed/summary_stats.csv",
            statsfile="stats/anova_results.txt"):

    os.makedirs(os.path.dirname(outfile), exist_ok=True)
    os.makedirs(os.path.dirname(statsfile), exist_ok=True)

    df = pd.read_csv(infile)
    df_valid = df[df['success'] == 1].copy()

    summary = df_valid.groupby(['temp','pH']).agg(
        n_trials=('latency_ms','count'),
        mean_latency=('latency_ms','mean'),
        sd_latency=('latency_ms','std'),
        median_latency=('latency_ms','median')
    ).reset_index()

    # also success rate
    sr = df.groupby(['temp','pH'])['success'].mean().reset_index()
    sr.rename(columns={'success':'success_rate'}, inplace=True)
    summary = pd.merge(summary, sr, on=['temp','pH'])
    summary.to_csv(outfile, index=False)

    # simple ANOVA across temps for each pH
    with open(statsfile, "w") as f:
        for pH in sorted(df['pH'].unique()):
            group = [df_valid[(df_valid['pH']==pH) & (df_valid['temp']==T)]['latency_ms'].dropna()
                     for T in sorted(df['temp'].unique())]
            if all(len(g) > 1 for g in group):
                F, p = stats.f_oneway(*group)
                f.write(f"pH={pH}: ANOVA F={F:.3f}, p={p:.3e}\n")
    print(f"Analysis complete. Summary -> {outfile}, Stats -> {statsfile}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--infile", type=str, default="data/raw/sim_raw_trials.csv")
    parser.add_argument("--outfile", type=str, default="data/processed/summary_stats.csv")
    parser.add_argument("--statsfile", type=str, default="stats/anova_results.txt")
    args = parser.parse_args()
    analyze(infile=args.infile, outfile=args.outfile, statsfile=args.statsfile)
