import csv
import pandas as pd
import utils
import os
import seaborn as sns
import matplotlib.pyplot as plt

data_list = utils.get_files()

def generate_graph(data, file_name, month):
    plt.figure(figsize=(10,6))
    sns.scatterplot(
        data=data,
        x="datetime",
        y="proton_density",
        hue="proton_speed",
        palette="viridis",
        s=30,              # marker size (increase if too small)
        alpha=0.7          # transparency so overlapping points are visible
    )
    plt.title("Proton Density vs. Timestamp (colored by Proton Speed)")
    plt.xlabel("Timestamp")
    plt.ylabel("Proton Density (cm⁻³)")
    # set y-axis limits
    plt.ylim(0.1, 15)
    plt.legend(title="Proton Speed (km/s)")
    plt.savefig(f"C:\\Users\\cpa50\\.vscode\\Heliospheric\\Solar-Wind-Disappearance\\Monthly_graphs\\{file_name}_{month}.png")

# Function to generate yearly graph
# for each in data_list:
#     willabyte = pd.read_csv(each)
#     willabyte['datetime'] = pd.to_datetime(willabyte[['Year', 'Day', 'Hour', 'Minute']].astype(str).agg('-'.join, axis=1), format='%Y-%j-%H-%M')
#     willabyte['year'] = willabyte['datetime'].dt.year
#     willabyte['day'] = willabyte['datetime'].dt.day
#     willabyte['hour'] = willabyte['datetime'].dt.hour
#     willabyte['minute'] = willabyte['datetime'].dt.minute

#     generate_graph(willabyte, each)
    


print(data_list)

for year in data_list:
    yearly_data = utils.get_monthly_data(f"C:\\Users\\cpa50\\.vscode\\Heliospheric\\Solar-Wind-Disappearance\\CSV\\{year}")
    for month in range(11):
        generate_graph(yearly_data[month], year, month)
        


