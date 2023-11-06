import matplotlib.pyplot as plt
import os
import re
import sys
import pandas as pd

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))

fig, axs = plt.subplots()

policies = ['QoSAware - EdgeCloud', 'Basic']
utilities = []
bar_labels = ['red', 'blue']
bar_colors = ['tab:red', 'tab:blue']


def read_values(name) -> pd.DataFrame:
    path = DIR + "/" + name
    for usersDir in os.listdir(path):
        print(f"usersDir: {usersDir}")
        m = re.match(r"users_(\d+)", usersDir)
        if m is None:
            continue
        path = path + "/" + usersDir
        for file in os.listdir(path):
            print(f"file: {file}")
            m = re.match(r"utilityCostResults_(\d+)", file)
            if m is None:
                continue
            f = pd.read_csv(os.path.join(path, file))
            print(f)
            return f




def switch(name):
    if name == "QoSAwareEdgeCloud":
        ur = read_values(name)
        utility = ur.loc[0, "Utility"]
        penalty = ur.loc[0, "Penalty"]
        net = ur.loc[0, "NetUtility"]
        utilities.insert(0, net)
    elif name == "Baseline":
        ur = read_values(name)
        utility = ur.loc[0, "Utility"]
        penalty = ur.loc[0, "Penalty"]
        net = ur.loc[0, "NetUtility"]
        utilities.insert(1, net)


# populate utilities
for entry in os.listdir(DIR):
    print(entry)
    switch(entry)
    print(utilities)

axs.bar(policies, utilities, label=bar_labels, color=bar_colors)

axs.set_ylabel('Net utility')
axs.set_title('Policies')

plt.savefig("comparison_1_plot.svg")
