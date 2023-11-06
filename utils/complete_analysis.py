import sys
import os
import re
import pandas as pd

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))
penalty = 0
utility = 0
under_limit = 0

for entry in os.listdir(DIR):
    m = re.match("results_(\d+).csv", entry)
    if m is None:
        continue
    users = int(m.groups()[0])
    df = pd.read_csv(os.path.join(DIR, entry))
    print(df)

    # calculate utility and cost
    with open(os.path.join(DIR, f"utilityCostResults_{users}.csv"), "w") as uf:
        print("TotalRequests,UnderLimit,Utility,Penalty,NetUtility,Cost,DropCount,CompletionPercentage", file=uf)

        experiment_time = (df.timeStamp.max() - df.timeStamp.min()) / 1000.0
        completed = df[df.responseCode == 200]
        completed_count = completed.responseCode.count()
        total_requests = len(df)
        drop_count = total_requests - completed_count
        arrivalRate = df.responseCode.count() / experiment_time
        responseTimes = completed.elapsed
        print(responseTimes)

        # calculate mean elapsed
        elapsed_mean = df["elapsed"].mean() / 1000
        latency_mean = df["Latency"].mean()
        print(f"elapsed mean (s): {elapsed_mean}")
        print(f"arrival rate (r/s): {arrivalRate}")
        print(f"latency mean (ms): {latency_mean}")


        # calculate utility
        default = df[df.qosClass == "default"]
        premium = df[df.qosClass == "premium"]
        for i in range(len(df)):
            if df.loc[i, "responseCode"] == 200:
                if df.loc[i, "qosClass"] == "default":
                    if df.loc[i, "elapsed"] <= float('inf'):
                        under_limit += 1
                        utility += 0.01
                    else:
                        penalty += 0
                elif df.loc[i, "qosClass"] == "premium":
                    if df.loc[i, "elapsed"] <= 750:
                        under_limit += 1
                        utility += 1.0
                    else:
                        penalty += 0

        net_utility = utility - penalty

        # Calculate completion percentage
        completion_perc = completed_count / total_requests

        # Calculate cost
        cost = sum(completed.cost)
        print(f"cost: {cost}")

        print(
            f'{total_requests:.5f},{under_limit:.5f},{utility:.5f},{penalty:.5f},{net_utility:.5f},{cost:.5f},{drop_count:.5f},{completion_perc:.5f}',
            file=uf)

    # calculate class distribution
    with open(os.path.join(DIR, f"classDistribution_{users}.csv"), "w") as distFile:
        print("STO QUI")
        print("Node,Default(%),Premium(%)", file=distFile)

        # Filter data based on conditions and calculate percentages
        default_l = (df[(df['responseCode'] == 200) & (df['qosClass'] == "default") & (
            df['schedulingAction'].isna())].shape[0] / df[df['qosClass'] == "default"].shape[0]) * 100
        default_e = (df[(df['responseCode'] == 200) & (df['qosClass'] == "default") & (
                    df['schedulingAction'] == "O_E")].shape[0] / df[df['qosClass'] == "default"].shape[0]) * 100
        default_c = (df[(df['responseCode'] == 200) & (df['qosClass'] == "default") & (
                    df['schedulingAction'] == "O_C")].shape[0] / df[df['qosClass'] == "default"].shape[0]) * 100
        default_d = (df[(df['responseCode'] != 200) & (df['qosClass'] == "default")].shape[0] /
                     df[df['qosClass'] == "default"].shape[0]) * 100

        premium_l = (df[(df['responseCode'] == 200) & (df['qosClass'] == "premium") & (
            df['schedulingAction'].isna())].shape[0] / df[df['qosClass'] == "premium"].shape[0]) * 100
        premium_e = (df[(df['responseCode'] == 200) & (df['qosClass'] == "premium") & (
                    df['schedulingAction'] == "O_E")].shape[0] / df[df['qosClass'] == "premium"].shape[0]) * 100
        premium_c = (df[(df['responseCode'] == 200) & (df['qosClass'] == "premium") & (
                    df['schedulingAction'] == "O_C")].shape[0] / df[df['qosClass'] == "premium"].shape[0]) * 100
        premium_d = (df[(df['responseCode'] != 200) & (df['qosClass'] == "premium")].shape[0] /
                     df[df['qosClass'] == "premium"].shape[0]) * 100

        print(f'Local,{default_l:.5f},{premium_l:.5f}', file=distFile)
        print(f'Edge,{default_e:.5f},{premium_e:.5f}', file=distFile)
        print(f'Cloud,{default_c:.5f},{premium_c:.5f}', file=distFile)
        print(f'Dropped,{default_d:.5f},{premium_d:.5f}', file=distFile)

    # calculate mean response times
    with open(os.path.join(DIR, f"meanResponsesForFibonacci_{users}.csv"), "w") as respFile1:
        print("Node,Response Time (ms)", file=respFile1)

        fibonacci_l = df[
            (df.responseCode == 200) & (df.URL == "http://192.168.122.2:1323/invoke/Fibonacci") & (
                df['schedulingAction'].isna())]
        fibonacci_e = df[
            (df.responseCode == 200) & (df.URL == "http://192.168.122.2:1323/invoke/Fibonacci") & (
                        df['schedulingAction'] == "O_E")]
        fibonacci_c = df[
            (df.responseCode == 200) & (df.URL == "http://192.168.122.2:1323/invoke/Fibonacci") & (
                        df['schedulingAction'] == "O_C")]

        fibonacci_meanResp_l = fibonacci_l["elapsed"].mean()
        fibonacci_meanResp_e = fibonacci_e["elapsed"].mean()
        fibonacci_meanResp_c = fibonacci_c["elapsed"].mean()

        print(f'Local,{fibonacci_meanResp_l:.5f}', file=respFile1)
        print(f'Edge,{fibonacci_meanResp_e:.5f}', file=respFile1)
        print(f'Cloud,{fibonacci_meanResp_c:.5f}', file=respFile1)

    with open(os.path.join(DIR, f"meanResponsesForImageClass_{users}.csv"), "w") as respFile2:
        print("Node,Response Time (ms)", file=respFile2)

        image_l = df[
            (df.responseCode == 200) & (df.URL == "http://192.168.122.2:1323/invoke/ImageClass") & (
                df['schedulingAction'].isna())]
        image_e = df[
            (df.responseCode == 200) & (df.URL == "http://192.168.122.2:1323/invoke/ImageClass") & (
                    df['schedulingAction'] == "O_E")]
        image_c = df[
            (df.responseCode == 200) & (df.URL == "http://192.168.122.2:1323/invoke/ImageClass") & (
                    df['schedulingAction'] == "O_C")]

        image_meanResp_l = image_l["elapsed"].mean()
        image_meanResp_e = image_e["elapsed"].mean()
        image_meanResp_c = image_c["elapsed"].mean()

        print(f'Local,{image_meanResp_l:.5f}', file=respFile2)
        print(f'Edge,{image_meanResp_e:.5f}', file=respFile2)
        print(f'Cloud,{image_meanResp_c:.5f}', file=respFile2)