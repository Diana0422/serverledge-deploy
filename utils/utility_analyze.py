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
    tar = tarfile.open(os.path.join(DIR, entry), "r:gz")

    with open(os.path.join(DIR, f"processedResults_{users}.csv"), "w") as of:
        print("FuncName,ClassName,ResponseTime,Action,QoSIsSatisfied", file=of)
        for member in tar.getmembers():
            f = tar.extractfile(member)
            if f is not None:
                content = f.read().decode("utf-8").strip()
                if len(content) == 0:
                    continue
                d = json.loads(content)

                qosOk = True if d["ResponseTime"] <= 1 else False
                print(f'{d["Name"]},{d["Class"]},{d["ResponseTime"]:.5f},{d["SchedAction"]},{qosOk}', file=of)

    total_utility = 0
    total_penalty = 0

    pL_U = [[0, 0], [0, 0]]  # row = function f, column = class k
    pC_U = [[0, 0], [0, 0]]
    pE_U = [[0, 0], [0, 0]]
    pL_P = [[0, 0], [0, 0]]  # row = function f, column = class k
    pC_P = [[0, 0], [0, 0]]
    pE_P = [[0, 0], [0, 0]]
    total_requests = 0

    number_default_fibo = 0
    lambda_default_fibo = 0
    number_default_image = 0
    lambda_default_image = 0
    number_premium_fibo = 0
    number_premium_image = 0

    utility_default = 0
    penalty_default = 0
    utility_premium = 0
    penalty_premium = 0

    utility = 0
    penalty = 0

    with open(os.path.join(DIR, f"utilityResults_{users}.csv"), "w") as uf:
        print("ClassName,Utility,Penalty,NetUtility", file=uf)

        for member in tar.getmembers():
            f = tar.extractfile(member)
            if f is not None:
                content = f.read().decode("utf-8").strip()
                if len(content) == 0:
                    continue
                d = json.loads(content)

                if d["Class"] == "default":
                    if d["ResponseTime"] <= float('inf'):
                        utility += 1
                    else:
                        penalty += 1
                elif d["Class"] == "premium":
                    if d["ResponseTime"] <= 1:
                        utility += 10
                    else:
                        penalty += 10

        net_utility = utility - penalty

        print(f'QoSAware,{utility:.5f},{penalty:.5f},{net_utility:.5f}', file=uf)
