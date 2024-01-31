import matplotlib.pyplot as plt
import os
import re
import sys
import pandas as pd
import numpy as np

DIR = sys.argv[1] if len(sys.argv) > 1 else "."
LANG = sys.argv[2] if len(sys.argv) > 2 else "ENG"
# ITA = italiano
# ENG = english

print(os.listdir(DIR))

# Creare un unico set di assi
fig, ax = plt.subplots(figsize=(8, 4))

policies = ['QoSAware - EdgeCloud', 'QoSAware - CloudOnly', 'Basic', 'MinR']
policy_order = ["Baseline", "MinR", "QoSAwareCloud", "QoSAwareEdgeCloud"]
mean_elapsed = {}
original_values = {}
min_vals = {}
bar_labels = ['red', 'blue']
bar_colors = ['tab:red', 'tab:blue']
COLOR2 = "#b0ceff"
COLOR2b = "#003180"


def policies_tiny_names(dict_policy_keys):
    policy_list = list(dict_policy_keys)
    ret = []
    for policy in policy_list:
        if policy == "Baseline":
            ret.append("Bc")
        elif policy == "MinR":
            ret.append("minR")
        elif policy == "QoSAwareCloud":
            ret.append("QoSC")
        elif policy == "QoSAwareEdgeCloud":
            ret.append("QoS")
    return ret


def read_values(name):
    path = DIR + "/" + name
    for usersDir in os.listdir(path):
        print(f"usersDir: {usersDir}")
        m = re.match(r"users_(\d+)", usersDir)
        if m is None:
            continue
        path = path + "/" + usersDir
        for file in os.listdir(path):
            m = re.match(r"results_(\d+).csv", file)
            if m is None:
                continue
            f = pd.read_csv(os.path.join(path, file))
            ok = f[(f.responseCode == 200) & (f.qosClass == "premium")]

            if name not in original_values.keys():
                original_values.update({name: [ok.elapsed / 1000]})
            else:
                old_values = original_values.get(name)
                old_values.append(ok.elapsed / 1000)
                original_values.update({name: old_values})

            mean = np.mean(ok.elapsed / 1000)
            if name not in mean_elapsed.keys():
                mean_elapsed.update({name: [mean]})
            else:
                means = mean_elapsed.get(name)
                means.append(mean)
                mean_elapsed.update({name: means})
            path = DIR + "/" + name


for entry in os.listdir(DIR):
    print(entry)
    read_values(entry)
    if len(os.listdir(DIR + "/" + entry)) == 0:
        # dir is empty
        continue
    print(f"mean_elapsed: {mean_elapsed}")
    print(f"original_values: {original_values}")
    min_elapsed = np.min(mean_elapsed.get(entry))
    print(f"min_elapsed: {min_elapsed}")
    index = mean_elapsed.get(entry).index(min_elapsed)
    vals = original_values.get(entry)[index]
    min_vals.update({entry: list(vals.values)})
    print(f"min_vals: {min_vals}")


def get_plot_data(d: dict):
    ordered_data = {k: d[k] for k in policy_order if k in d}
    return ordered_data


# Create boxplot
dict_data = get_plot_data(min_vals)
print(dict_data.keys())
keys = list(dict_data.keys())
data = list(dict_data.values())

# Crea un box plot per ogni chiave
bp = ax.boxplot(data, labels=policies_tiny_names(keys), showfliers=False)

# Add labels and title to the plot
if LANG == "ITA":
    plt.xlabel('Politica')
    plt.ylabel('Tempo di Risposta (s)')
else:
    plt.xlabel('Policy')
    plt.ylabel('Response Time (s)')

# Add a horizontal line to define the response time limit
if LANG == "ITA":
    plt.axhline(y=0.8, color='r', linestyle='--', label='Tempo Max. Risposta (utenti Premium)')
else:
    plt.axhline(y=0.8, color='r', linestyle='--', label='Max. Resp. Time (Premium users)')
# adding horizontal grid lines
ax.yaxis.grid(True)
plt.legend()
plt.savefig("elapsed_box_plot.svg")

print(f"mean elapsed: {mean_elapsed}")
