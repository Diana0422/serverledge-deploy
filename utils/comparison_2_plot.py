import matplotlib.pyplot as plt
import os
import re
import sys
import pandas as pd

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))

# Creare un unico set di assi
fig, ax = plt.subplots(figsize=(12, 6))
plt.title("Response Time Comparison")

policies = ['QoSAware - EdgeCloud', 'Basic']
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
            m = re.match(r"results_(\d+).csv", file)
            if m is None:
                continue
            f = pd.read_csv(os.path.join(path, file))
            print(f)
            return f

for entry in os.listdir(DIR):
    print(entry)
    if entry == "QoSAwareEdgeCloud" or entry == "Baseline":
        df = read_values(entry)
        completed = df[df.responseCode == 200]
        responseTimes = completed.elapsed

        # Sovrapponi i box plot nello stesso grafico
        ax.boxplot(responseTimes.values, positions=[1] if entry == "QoSAwareEdgeCloud" else [2], widths=0.6, labels=[entry], showfliers=False)

# Aggiungi una linea orizzontale in corrispondenza del valore maxRt
ax.axhline(y=750, color='r', linestyle='--', label='Threshold (750)')

# Aggiungi etichette all'asse x
ax.set_xticks([1, 2])
ax.set_xticklabels(["QoSAware - EdgeCloud", "Basic"])
ax.set_xlabel('Policies')

# Aggiungi etichette all'asse y
ax.set_ylabel('Response Time (ms)')

# Aggiungi una griglia orizzontale
ax.yaxis.grid(True)

plt.legend()
plt.savefig("comparison_2_plot.svg")
