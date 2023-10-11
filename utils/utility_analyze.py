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

    pL = [[0, 0], [0, 0]]  # row = function f, column = class k
    pC = [[0, 0], [0, 0]]
    pE = [[0, 0], [0, 0]]
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

    with open(os.path.join(DIR, f"utilityResults_{users}.csv"), "w") as uf:
        print("ClassName,Utility,Penalty,NetUtility", file=uf)
        for member in tar.getmembers():
            f = tar.extractfile(member)
            if f is not None:
                content = f.read().decode("utf-8").strip()
                if len(content) == 0:
                    continue
                d = json.loads(content)

                total_requests += 1

                if d["Class"] == "default" and d["Name"] == "Fibonacci":
                    i = 0
                    j = 0
                    number_default_fibo += 1
                    if d["ResponseTime"] < float('inf'):
                        utility_default += 1
                        if d["SchedAction"] == "":
                            # Esecuzione locale
                            pL[i][j] += 1
                        elif d["SchedAction"] == "O_E":
                            # Offloading Edge
                            pE[i][j] += 1
                        elif d["SchedAction"] == "O_C":
                            # Offloading Cloud
                            pC[i][j] += 1
                    else:
                        penalty_default += 1
                elif d["Class"] == "default" and d["Name"] == "ImageClass":
                    i = 1
                    j = 0
                    number_default_image += 1
                    if d["ResponseTime"] < float('inf'):
                        utility_default += 1
                        if d["SchedAction"] == "":
                            # Esecuzione locale
                            pL[i][j] += 1
                        elif d["SchedAction"] == "O_E":
                            # Offloading Edge
                            pE[i][j] += 1
                        elif d["SchedAction"] == "O_C":
                            # Offloading Cloud
                            pC[i][j] += 1
                    else:
                        penalty_default += 1
                elif d["Class"] == "premium" and d["Name"] == "Fibonacci":
                    i = 0
                    j = 1
                    number_premium_fibo += 1
                    if d["ResponseTime"] <= 1:
                        utility_premium += 10
                        if d["SchedAction"] == "":
                            # Esecuzione locale
                            pL[i][j] += 1
                        elif d["SchedAction"] == "O_E":
                            # Offloading Edge
                            pE[i][j] += 1
                        elif d["SchedAction"] == "O_C":
                            # Offloading Cloud
                            pC[i][j] += 1
                    else:
                        penalty_premium += 10
                elif d["Class"] == "premium" and d["Name"] == "ImageClass":
                    i = 1
                    j = 1
                    number_premium_image += 1
                    if d["ResponseTime"] <= 1:
                        utility_premium += 10
                        if d["SchedAction"] == "":
                            # Esecuzione locale
                            pL[i][j] += 1
                        elif d["SchedAction"] == "O_E":
                            # Offloading Edge
                            pE[i][j] += 1
                        elif d["SchedAction"] == "O_C":
                            # Offloading Cloud
                            pC[i][j] += 1
                    else:
                        penalty_premium += 10

        for i in range(0, 2):
            for j in range(0, 2):
                pL[i][j] = float(pL[i][j]) / float(total_requests)
                pE[i][j] = float(pE[i][j]) / float(total_requests)
                pC[i][j] = float(pC[i][j]) / float(total_requests)

        print(f"pL: {pL}")
        print(f"pE: {pE}")
        print(f"pC: {pC}")

        lambda_default_fibo = number_default_fibo / 600
        lambda_default_image = number_default_image / 600
        lambda_premium_fibo = number_premium_fibo / 600
        lambda_premium_image = number_premium_image / 600
        print(f"lambda_default_fibo: {lambda_default_fibo}")
        print(f"lambda_default_image: {lambda_default_image}")
        print(f"lambda_premium_fibo: {lambda_premium_fibo}")
        print(f"lambda_premium_image: {lambda_premium_image}")

        total_utility = (utility_default * (lambda_default_fibo * (pL[0][0] + pC[0][0] + pE[0][0])
                                            + lambda_default_image * (pL[1][0] + pC[1][0] + pE[1][0])) +
                         utility_premium * (lambda_premium_fibo * (pL[0][1] + pC[0][1] + pE[0][1])
                                            + lambda_premium_image * (pL[1][1] + pC[1][1] + pE[1][1])))
        total_penalty = (penalty_default * (lambda_default_fibo * (pL[0][0] + pC[0][0] + pE[0][0])
                                            + lambda_default_image * (pL[1][0] + pC[1][0] + pE[1][0])) +
                         penalty_premium * (lambda_premium_fibo * (pL[0][1] + pC[0][1] + pE[0][1])
                                            + lambda_premium_image * (pL[1][1] + pC[1][1] + pE[1][1])))
        print(f"total_utility: {total_utility}")
        print(f"total_penalty: {total_penalty}")
        net_utility = total_utility - total_penalty

        print(f'QoSAware,{total_utility:.5f},{total_penalty:.5f},{net_utility:.5f}', file=uf)
