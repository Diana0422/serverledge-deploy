import matplotlib.pyplot as plt
import os
import re
import sys
import pandas as pd

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))

fig, ax = plt.subplots()

policies = ['QoSAware - EdgeCloud', 'QoSAware - Cloud', 'Basic']
utilities = []
bar_labels = ['red', 'blue', 'orange']
bar_colors = ['tab:red', 'tab:blue', 'tab:orange']


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
            m = re.match(r"utilityResults_(\d+)", file)
            if m is None:
                continue
            f = pd.read_csv(os.path.join(path, file))
            print(f)
            return f




def switch(name):
    if name == "QoSAwareCloud":
        ur = read_values(name)
        utility = ur.loc[0, "Utility"]
        penalty = ur.loc[0, "Penalty"]
        net = ur.loc[0, "NetUtility"]
        utilities.insert(1, net)
    elif name == "QoSAwareEdgeCloud":
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
        utilities.insert(2, net)


# populate utilities
for entry in os.listdir(DIR):
    print(entry)
    switch(entry)
    print(utilities)

ax.bar(policies, utilities, label=bar_labels, color=bar_colors)

ax.set_ylabel('Net utility')
ax.set_title('Policies')

plt.savefig("comparison_1_plot.svg")
