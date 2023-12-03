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
drops = {}
drop_means = {}
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
            drop = f.loc[0, "DropCount"] / f.loc[0, "TotalRequests"]
            if name not in drops.keys():
                drops.update({name: [drop]})
            else:
                vals = drops.get(name)
                vals.append(drop)
                drops.update({name: vals})
            print(drops)
            path = DIR + "/" + name


def switch(name):
    if name == "QoSAwareEdgeCloud":
        read_values(name)
        if name in drops.keys():
            drop_means.update({name: np.mean(drops.get(name))})
    elif name == "QoSAwareCloud":
        read_values(name)
        if name in drops.keys():
            drop_means.update({name: np.mean(drops.get(name))})
    elif name == "Baseline":
        read_values(name)
        if name in drops.keys():
            drop_means.update({name: np.mean(drops.get(name))})
    elif name == "MinR":
        read_values(name)
        if name in drops.keys():
            drop_means.update({name: np.mean(drops.get(name))})


# populate utilities
for entry in os.listdir(DIR):
    print(f"entry: {entry}")
    switch(entry)
    print(f"costs: {drops}")
    print(f"cost means: {drop_means}")

# Extract keys and values from the dictionary
keys = list(drops.keys())
data = list(drops.values())

# Create a boxplot for each key
plt.boxplot(data, labels=keys, showfliers=False)

# Add labels to the axis and a title for the plot
plt.xlabel('Politiche')
plt.ylabel('Richieste scartate (%)')
plt.title('Confronto della percentuale di richieste scartate tra le diverse politiche')
plt.savefig("drop_box_plot.svg")

# Plot means in bar chart
plt.clf()
plt.grid(axis='y', zorder=0, color='gray', linestyle='dashed')
keys = list(drop_means.keys())
values = list(drop_means.values())

# Crea il grafico a barre
plt.bar(keys, values, color=bar_labels, zorder=3)

# Aggiungi etichette agli assi e un titolo al grafico
plt.xlabel('Politiche')
plt.ylabel('Numero medio di richieste scartate')
plt.title('Confronto della percentuale di richieste scartate tra le diverse politiche')
plt.savefig("drop_bar_plot.svg")