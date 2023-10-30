import matplotlib.pyplot as plt
import os
import re
import sys
import pandas as pd

DIR = sys.argv[1] if len(sys.argv) > 1 else "."

print(os.listdir(DIR))

# Creare un unico set di assi
fig, ax = plt.subplots(figsize=(12, 6))

policies = ['QoSAware - EdgeCloud', 'QoSAware - CloudOnly']
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
    if entry == "QoSAwareEdgeCloud" or entry == "QoSAwareCloud":
        df = read_values(entry)
        completed = df[df.responseCode == 200]
        responseTimes = completed.elapsed
        # Filtra le righe in cui elapsed supera 4000
        rows_above_threshold = df[df['elapsed'] > 4000]

        # Stampa le righe
        print(rows_above_threshold)

    # Sovrapponi i box plot nello stesso grafico
        ax.boxplot(responseTimes.values, positions=[1] if entry == "QoSAwareEdgeCloud" else [2], widths=0.6, labels=[entry])

# Aggiungi una linea orizzontale in corrispondenza del valore 770
ax.axhline(y=770, color='r', linestyle='--', label='Threshold (770)')

# Aggiungi etichette all'asse x
ax.set_xticks([1, 2])
ax.set_xticklabels(["QoSAware - EdgeCloud", "QoSAware - CloudOnly"])
ax.set_xlabel('Policies')

# Aggiungi etichette all'asse y
ax.set_ylabel('Observed values')

# Aggiungi una griglia orizzontale
ax.yaxis.grid(True)

plt.legend()
plt.savefig("comparison_4_plot.svg")
