import matplotlib.pyplot as plt
import os
import re
import sys
import pandas as pd
import numpy as np

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))

# Creare un unico set di assi
fig, ax = plt.subplots(figsize=(12, 6))
plt.title("Response Time Comparison")

policies = ['QoSAware - EdgeCloud', 'QoSAware - CloudOnly', 'Basic', 'MinR']
mean_elapsed = {}
original_values = {}
min_vals = {}
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
            m = re.match(r"results_(\d+).csv", file)
            if m is None:
                continue
            f = pd.read_csv(os.path.join(path, file))
            ok = f[f.responseCode == 200]

            if name not in original_values.keys():
                original_values.update({name: [ok.elapsed]})
            else:
                old_values = original_values.get(name)
                old_values.append(ok.elapsed)
                original_values.update({name: old_values})

            mean = np.mean(ok.elapsed)
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


# Create boxplot
keys = list(min_vals.keys())
data = list(min_vals.values())

# Crea un box plot per ogni chiave
plt.boxplot(data, labels=keys, showfliers=False)

# Add labels and title to the plot
plt.xlabel('Policies')
plt.ylabel('Elapsed (ms)')
plt.title('Response time comparison between different policies')

# Add a horizontal line to define the response time limit
plt.axhline(y=750, color='r', linestyle='--', label='Threshold (750)')
plt.legend()
plt.savefig("elapsed_box_plot.svg")
