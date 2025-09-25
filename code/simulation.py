import argparse, csv, os, numpy as np

def q_factor_for_temp(T, T0=34.0, Q10=2.0):
    return Q10 ** ((T0 - T) / 10.0)

def pH_effect_on_release(pH, pH0=7.4):
    dp = pH0 - pH
    p_release = max(0.1, 0.98 - 0.6 * dp)
    var_mult = 1.0 + 1.5 * dp
    return p_release, var_mult

def run_sim(trials=500, temps=(32.0,34.0,36.0), pHs=(7.4,7.3,7.2), out="data/raw/sim_raw_trials.csv", seed=42):
    np.random.seed(seed)
    conduction_delay = 0.5
    release_mean = 0.5
    release_sd = 0.12
    tau_syn = 1.0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['trial_id','temp','pH','latency_ms','success','seed'])
        tid = 0
        for T in temps:
            q = q_factor_for_temp(T)
            for pH in pHs:
                p_release, var_mult = pH_effect_on_release(pH)
                for i in range(trials):
                    tid += 1
                    if np.random.rand() > p_release:
                        writer.writerow([tid, T, pH, '', 0, seed])
                        continue
                    mean_d = release_mean * q
                    sd_d = release_sd * q * var_mult
                    d = np.random.normal(mean_d, sd_d)
                    if d < 0.02: d = 0.02
                    tau_eff = tau_syn * q
                    onset_offset = 0.12 * tau_eff
                    latency = conduction_delay + d + onset_offset
                    writer.writerow([tid, T, pH, float(latency), 1, seed])
    print(f"Simulation finished. Output: {out}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=500)
    parser.add_argument("--temps", nargs="+", type=float, default=[32.0,34.0,36.0])
    parser.add_argument("--pHs", nargs="+", type=float, default=[7.4,7.3,7.2])
    parser.add_argument("--out", type=str, default="data/raw/sim_raw_trials.csv")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    run_sim(trials=args.trials, temps=args.temps, pHs=args.pHs, out=args.out, seed=args.seed)
