import matplotlib.pyplot as plt
import os
import re
import sys
import pandas as pd
import numpy as np

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))

fig, axs = plt.subplots(figsize=(12, 6))

policies = ['QoSAware - EdgeCloud', 'QoSAware - CloudOnly', 'Basic', 'MinR']
violations = {}
violations_means = {}
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
            violation_perc = 1 - f.loc[0, "UnderLimit"] / (f.loc[0, "TotalRequests"]-f.loc[0, "DropCount"])
            if name not in violations.keys():
                violations.update({name: [violation_perc]})
            else:
                vals = violations.get(name)
                vals.append(violation_perc)
                violations.update({name: vals})
            print(violations)
            path = DIR + "/" + name


def switch(name):
    if name == "QoSAwareEdgeCloud":
        read_values(name)
        if name in violations.keys():
            violations_means.update({name: np.mean(violations.get(name))})
    elif name == "QoSAwareCloud":
        read_values(name)
        if name in violations.keys():
            violations_means.update({name: np.mean(violations.get(name))})
    elif name == "Baseline":
        read_values(name)
        if name in violations.keys():
            violations_means.update({name: np.mean(violations.get(name))})
    elif name == "MinR":
        read_values(name)
        if name in violations.keys():
            violations_means.update({name: np.mean(violations.get(name))})


# populate utilities
for entry in os.listdir(DIR):
    print(f"entry: {entry}")
    switch(entry)
    print(f"violations: {violations}")
    print(f"violations means: {violations_means}")

# Extract keys and values from the dictionary
keys = list(violations.keys())
data = list(violations.values())

# Create a boxplot for each key
plt.boxplot(data, labels=keys, showfliers=False)

# Add labels to the axis and a title for the plot
plt.xlabel('Politiche')
plt.ylabel('Percentuale di violazioni')
plt.title('Confronto della percentuale di violazioni su diverse politiche')
plt.savefig("violation_box_plot.svg")

# Plot means in bar chart
plt.clf()
keys = list(violations_means.keys())
values = list(violations_means.values())

# Crea il grafico a barre
plt.bar(keys, values, color=bar_labels)

# Aggiungi etichette agli assi e un titolo al grafico
plt.xlabel('Politiche')
plt.ylabel('Percentuale di violazioni')
plt.title('Confronto della percentuale di violazioni su diverse politiche')
plt.savefig("violation_bar_plot.svg")
