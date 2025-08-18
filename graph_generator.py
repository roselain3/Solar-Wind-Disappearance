import csv
import pandas as pd
import utils
import os
import seaborn as sns
import matplotlib.pyplot as plt

data_list = utils.get_files()

for each in data_list:
    willabyte = pd.read_csv(each)
    willabyte['datetime'] = pd.to_datetime(willabyte[['Year', 'Day', 'Hour', 'Minute']].astype(str).agg('-'.join, axis=1), format='%Y-%j-%H-%M')
    willabyte['year'] = willabyte['datetime'].dt.year
    willabyte['day'] = willabyte['datetime'].dt.day
    willabyte['hour'] = willabyte['datetime'].dt.hour
    willabyte['minute'] = willabyte['datetime'].dt.minute
    
    plt.figure(figsize=(10,6))
    sns.scatterplot(
        data=willabyte,
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
    plt.savefig(f"C:\\Users\\rcvil\\Heliospheric Anomaly\\ACE CSV\\Graphs\\Yearly_graphs\\{each}.png")




