import sys
import os
import re
import pandas as pd

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))
penalty = 0
utility = 0

for entry in os.listdir(DIR):
    m = re.match("results-(\d+).csv", entry)
    if m is None:
        continue
    users = int(m.groups()[0])
    df = pd.read_csv(os.path.join(DIR, entry))

    with open(os.path.join(DIR, f"utilityResults_{users}.csv"), "w") as uf:
        print("ClassName,Utility,Penalty,NetUtility", file=uf)

        experiment_time = (df.timeStamp.max() - df.timeStamp.min()) / 1000.0
        completed = df[df.responseCode == 200]
        completed_count = completed.responseCode.count()
        default = df[df.QoSClass == "default"]
        premium = df[df.QoSClass == "premium"]

        for request in df.rows:
            if request["QoSClass"] == "default":
                if request["elapsed"] <= float('inf'):
                    utility += 1
                else:
                    penalty += 1
            elif request["QoSClass"] == "premium":
                if request["elapsed"] <= 1:
                    utility += 10
                else:
                    penalty += 10

        net_utility = utility - penalty

        print(f'QoSAware,{utility:.5f},{penalty:.5f},{net_utility:.5f}', file=uf)
