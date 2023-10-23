import sys
import os
import re
import pandas as pd

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))
penalty = 0
utility = 0

for entry in os.listdir(DIR):
    m = re.match("results_(\d+).csv", entry)
    if m is None:
        continue
    users = int(m.groups()[0])
    df = pd.read_csv(os.path.join(DIR, entry))
    print(df)

    with open(os.path.join(DIR, f"utilityResults_{users}.csv"), "w") as uf:
        print("ClassName,Utility,Penalty,NetUtility", file=uf)

        experiment_time = (df.timeStamp.max() - df.timeStamp.min()) / 1000.0
        completed = df[df.responseCode == 200]
        completed_count = completed.responseCode.count()
        arrivalRate = df.responseCode.count()/experiment_time

        # calculate mean elapsed
        elapsed_mean = df["elapsed"].mean()/1000
        print(f"elapsed mean (s): {elapsed_mean}")
        print(f"arrival rate (r/s): {arrivalRate}")

        # calculate utility

        default = df[df.qosClass == "default"]
        premium = df[df.qosClass == "premium"]
        for i in range(len(df)):
            if df.loc[i, "responseCode"] == 200:
                if df.loc[i, "qosClass"] == "default":
                    if df.loc[i, "elapsed"] <= float('inf'):
                        utility += 1
                    else:
                        penalty += 1
                elif df.loc[i, "qosClass"] == "premium":
                    if df.loc[i, "elapsed"] <= 660:
                        utility += 10
                    else:
                        penalty += 10

        net_utility = utility - penalty

        print(f'QoSAware,{utility:.5f},{penalty:.5f},{net_utility:.5f}', file=uf)
