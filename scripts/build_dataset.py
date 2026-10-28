"""Build data/traffic_204_zones.csv from the raw daily Telecom Italia files.

The raw files (sms-call-internet-mi-2013-11-DD.txt) are tab-separated without a
header. We keep only the zone id, the timestamp and the internet-activity column,
select a reproducible random sample of zones, sum rows that share the same zone
and timestamp (one row per country code in the raw data), and convert the
timestamp to Europe/Rome local time.

Usage:
    python scripts/build_dataset.py
    python scripts/build_dataset.py --raw-dir data --out data/traffic_204_zones.csv
"""
import argparse
from pathlib import Path

import numpy as np
import pandas as pd

EXTRA_ZONES = {1983, 5161, 6437, 7386}  # zones inspected during exploration


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--raw-dir", default="data", help="folder with the raw daily files")
    parser.add_argument("--out", default="data/traffic_204_zones.csv", help="output CSV path")
    parser.add_argument("--n-zones", type=int, default=200, help="number of random zones")
    parser.add_argument("--seed", type=int, default=42, help="random seed for the zone sample")
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    selected = set(rng.choice(np.arange(1, 10001), size=args.n_zones, replace=False)) | EXTRA_ZONES

    files = sorted(Path(args.raw_dir).glob("sms-call-internet-mi-2013-11-*.txt"))
    if not files:
        raise SystemExit(f"No raw files found in {args.raw_dir!r}. See the README for the download link.")
    print(len(files), "raw files")

    parts = []
    for f in files:
        d = pd.read_csv(f, sep="\t", header=None, usecols=[0, 1, 7],
                        names=["cell", "ts", "internet"])
        d = d[d["cell"].isin(selected)]
        d = d.groupby(["cell", "ts"], as_index=False)["internet"].sum()
        parts.append(d)
        print(f.name, len(d))

    traffic = pd.concat(parts, ignore_index=True)
    traffic["time"] = (pd.to_datetime(traffic["ts"], unit="ms", utc=True)
                       .dt.tz_convert("Europe/Rome").dt.tz_localize(None))
    traffic = traffic.drop(columns="ts")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    traffic.to_csv(out, index=False)
    print(traffic["cell"].nunique(), "zones,", traffic["time"].min(), "-", traffic["time"].max())
    print("saved", len(traffic), "rows to", out)


if __name__ == "__main__":
    main()
