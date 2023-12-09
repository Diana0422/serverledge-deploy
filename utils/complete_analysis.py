import sys
import os
import re
import pandas as pd

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))
penalty = 0
utility = 0
under_limit_default = 0
under_limit_premium = 0
out_edge = 0
out_cloud = 0
out_local = 0

for entry in os.listdir(DIR):
    m = re.match("results_(\d+).csv", entry)
    if m is None:
        continue
    users = int(m.groups()[0])
    df = pd.read_csv(os.path.join(DIR, entry))
    print(df)

    # calculate utility and cost
    with open(os.path.join(DIR, f"utilityCostResults_{users}.csv"), "w") as uf:
        print(
            "TotalRequests,UnderLimitDefault,UnderLimitPremium,Utility,Penalty,NetUtility,PerRequestUtility,Cost,DropCount,CompletionPercentage",
            file=uf)

        experiment_time = (df.timeStamp.max() - df.timeStamp.min()) / 1000.0
        completed = df[df.responseCode == 200]
        completed_count = completed.responseCode.count()
        total_requests = len(df)
        drop_count = total_requests - completed_count
        arrivalRate = df.responseCode.count() / experiment_time
        responseTimes = completed.elapsed

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
                        under_limit_default += 1
                        utility += 0.01
                    else:
                        penalty += 0
                elif df.loc[i, "qosClass"] == "premium":
                    if df.loc[i, "elapsed"] <= 3000:
                        under_limit_premium += 1
                        utility += 1.0
                    else:
                        penalty += 0
                        if df.loc[i, "schedulingAction"] == "O_E":
                            out_edge += 1
                        elif df.loc[i, "schedulingAction"] == "O_C":
                            out_cloud += 1
                        else:
                            out_local += 1

        if (out_cloud+out_local+out_edge) != 0:
            perc_edge = out_edge / (out_cloud+out_local+out_edge)
            perc_cloud = out_cloud / (out_cloud+out_local+out_edge)
            perc_local = out_local / (out_cloud+out_local+out_edge)
            print(f"out edge: {perc_edge}")
            print(f"out cloud: {perc_cloud}")
            print(f"out local: {perc_local}")
        net_utility = utility - penalty
        per_request_utility = net_utility / total_requests
        print(f"net utility: {net_utility}")

        # Calculate completion percentage
        completion_perc = completed_count / total_requests

        # Calculate cost
        total_cost = sum(completed.cost) / experiment_time * 3600
        print(f"$/h: {total_cost}")
        print(f"budget $/h: {0.40}")

        print(
            f'{total_requests:.5f},{under_limit_default:.5f},{under_limit_premium:.5f},{utility:.5f},{penalty:.5f},{net_utility:.5f},{per_request_utility:.5f},{total_cost:.5f},{drop_count:.5f},{completion_perc:.5f}',
            file=uf)

    # calculate function infos
    with open(os.path.join(DIR, f"functionsResults_{users}.csv"), "w") as funcFile:
        print("FunctionName, DefaultResponseTime, PremiumResponseTime, DefaultCompleted, PremiumCompleted", file=funcFile)

        completed_fib = completed[completed.URL == "http://192.168.122.101:1323/invoke/Fibonacci"]
        completed_image = completed[completed.URL == "http://192.168.122.101:1323/invoke/ImageClass"]
        completed_fib_def = completed_fib.qosClass.value_counts()["default"]
        completed_fib_prem = completed_fib.qosClass.value_counts()["premium"]
        completed_image_def = completed_image.qosClass.value_counts()["default"]
        completed_image_prem = completed_image.qosClass.value_counts()["premium"]
        completed_fib_def_perc = completed_fib_def / completed_count
        completed_image_def_perc = completed_image_def / completed_count
        completed_fib_prem_perc = completed_fib_prem / completed_count
        completed_image_prem_perc = completed_image_prem / completed_count
        function_response_times = completed[["elapsed", "URL", "qosClass"]]
        response_time_fib_prem = function_response_times[(function_response_times.URL == "http://192.168.122.101:1323/invoke/Fibonacci") & (function_response_times.qosClass == "premium")]
        response_time_fib_def = function_response_times[(function_response_times.URL == "http://192.168.122.101:1323/invoke/Fibonacci") & (function_response_times.qosClass == "default")]
        response_time_image_prem = function_response_times[(function_response_times.URL == "http://192.168.122.101:1323/invoke/ImageClass") & (function_response_times.qosClass == "premium")]
        response_time_image_def = response_time_fib = function_response_times[(function_response_times.URL == "http://192.168.122.101:1323/invoke/ImageClass") & (function_response_times.qosClass == "default")]
        mean_time_fib_def = response_time_fib_def["elapsed"].mean()
        mean_time_fib_prem = response_time_fib_prem["elapsed"].mean()
        mean_time_image_def = response_time_image_def["elapsed"].mean()
        mean_time_image_prem = response_time_image_prem["elapsed"].mean()

        print(f'Fibonacci,{mean_time_fib_def:.5f},{mean_time_fib_prem:.5f},{completed_fib_def_perc:.5f},{completed_fib_prem_perc:.5f}', file=funcFile)
        print(f'ImageClass,{mean_time_image_def:.5f},{mean_time_image_prem:.5f},{completed_image_def_perc:.5f},{completed_image_prem_perc:.5f}', file=funcFile)

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
            (df.responseCode == 200) & (df.URL == "http://192.168.122.101:1323/invoke/Fibonacci") & (
                df['schedulingAction'].isna())]
        fibonacci_e = df[
            (df.responseCode == 200) & (df.URL == "http://192.168.122.101:1323/invoke/Fibonacci") & (
                    df['schedulingAction'] == "O_E")]
        fibonacci_c = df[
            (df.responseCode == 200) & (df.URL == "http://192.168.122.101:1323/invoke/Fibonacci") & (
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
            (df.responseCode == 200) & (df.URL == "http://192.168.122.101:1323/invoke/ImageClass") & (
                df['schedulingAction'].isna())]
        image_e = df[
            (df.responseCode == 200) & (df.URL == "http://192.168.122.101:1323/invoke/ImageClass") & (
                    df['schedulingAction'] == "O_E")]
        image_c = df[
            (df.responseCode == 200) & (df.URL == "http://192.168.122.101:1323/invoke/ImageClass") & (
                    df['schedulingAction'] == "O_C")]

        image_meanResp_l = image_l["elapsed"].mean()
        image_meanResp_e = image_e["elapsed"].mean()
        image_meanResp_c = image_c["elapsed"].mean()

        print(f'Local,{image_meanResp_l:.5f}', file=respFile2)
        print(f'Edge,{image_meanResp_e:.5f}', file=respFile2)
        print(f'Cloud,{image_meanResp_c:.5f}', file=respFile2)
