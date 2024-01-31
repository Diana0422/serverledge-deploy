import matplotlib.pyplot as plt
import os
import re
import sys
import pandas as pd
import numpy as np

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))

fig, axs = plt.subplots(figsize=(12, 6))
axs.set_axisbelow(True)
axs.yaxis.grid(color='gray', linestyle='dashed')

policies = ['QoSAware - EdgeCloud', 'QoSAware - CloudOnly', 'Basic', 'MinR']
costs = {}
cost_means = {}
bar_labels = ['red', 'blue', 'orange', 'green']
bar_colors = ['tab:red', 'tab:blue', 'tab:orange', 'tab:green']


def read_values(name) -> pd.DataFrame:
    path = DIR + "/" + name
    print(os.listdir(path))
    for usersDir in os.listdir(path):
        print(f"usersDir: {usersDir}")
        m = re.match(r"users_(\d+)_(\d+)", usersDir)
        if m is None:
            continue
        path = path + "/" + usersDir
        for file in os.listdir(path):
            m = re.match(r"utilityCostResults_(\d+)", file)
            if m is None:
                continue
            f = pd.read_csv(os.path.join(path, file))
            cost_per_hour = f.loc[0, "Cost"]
            if name not in costs.keys():
                costs.update({name: [cost_per_hour]})
            else:
                vals = costs.get(name)
                vals.append(cost_per_hour)
                costs.update({name: vals})
            print(costs)
            path = DIR + "/" + name


def switch(name):
    if name == "QoSAwareEdgeCloud":
        read_values(name)
        if name in costs.keys():
            cost_means.update({"QoS": np.mean(costs.get(name))})
    elif name == "QoSAwareCloud":
        read_values(name)
        if name in costs.keys():
            cost_means.update({"QoSC": np.mean(costs.get(name))})
    elif name == "Baseline":
        read_values(name)
        if name in costs.keys():
            cost_means.update({"Bc": np.mean(costs.get(name))})
    elif name == "MinR":
        read_values(name)
        if name in costs.keys():
            cost_means.update({"minR": np.mean(costs.get(name))})


# populate utilities
for entry in os.listdir(DIR):
    print(f"entry: {entry}")
    switch(entry)
    print(f"costs: {costs}")
    print(f"cost means: {cost_means}")

# Extract keys and values from the dictionary
keys = list(costs.keys())
data = list(costs.values())

# Create a boxplot for each key
plt.boxplot(data, labels=keys, showfliers=False)

# Add labels to the axis and a title for the plot
plt.xlabel('Policies')
plt.ylabel('Cost ($/h)')
plt.title('Cost comparison between different policies')
plt.savefig("cost_box_plot.svg")

# Plot means in bar chart
plt.clf()
plt.grid(axis='y', zorder=0, color='gray', linestyle='dashed')
keys = list(cost_means.keys())
values = list(cost_means.values())

# Crea il grafico a barre
plt.bar(keys, values, color=bar_labels, zorder=3)

# Aggiungi etichette agli assi e un titolo al grafico
plt.xlabel('Policies')
plt.ylabel('Mean cost ($/h)')
plt.title('Mean cost comparison between different policies')
plt.savefig("cost_bar_plot.svg")
