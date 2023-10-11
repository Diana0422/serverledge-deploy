import sys
import os
import re
import tarfile
import json

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))

for entry in os.listdir(DIR):
    m = re.match("responses_(\d+).tar.gz", entry)
    if m is None:
        continue
    users = int(m.groups()[0])
    tar = tarfile.open(os.path.join(DIR,entry), "r:gz")

    with open(os.path.join(DIR,f"processedResults_{users}.csv"), "w") as of:
        print("FuncName,ClassName,ResponseTime,QoSIsSatisfied", file=of)
        for member in tar.getmembers():
            f = tar.extractfile(member)
            if f is not None:
                content = f.read().decode("utf-8").strip()
                if len(content) == 0:
                    continue
                d = json.loads(content)

                qosOk = True if d["ResponseTime"] <= 1 else False
                print(f'{d["Name"]},{d["Class"]},{d["ResponseTime"]:.5f},{qosOk}', file=of)

    total_utility = 0
    total_penalty = 0

    with open(os.path.join(DIR,f"utilityResults_{users}.csv"), "w") as uf:
        print("ClassName,Utility,Penalty,NetUtility", file=uf)
        for member in tar.getmembers():
            f = tar.extractfile(member)
            if f is not None:
                content = f.read().decode("utf-8").strip()
                if len(content) == 0:
                    continue
                d = json.loads(content)

                if d["Class"] == "default":
                    total_utility += 1
                else:
                    if d["ResponseTime"] <= 1:
                        total_utility += 10
                    else:
                        total_penalty += 10

        net_utility = total_utility - total_penalty

        print(f'QoSAware,{total_utility:.5f},{total_penalty:.5f},{net_utility:.5f}', file=uf)
