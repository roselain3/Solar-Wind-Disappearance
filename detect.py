import csv
import pandas as pd
import sys
import os

# Add the parent directory to the Python path to import utils
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utils

import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime

data_list = utils.get_files()

# Global list to store all anomalies
all_anomalies = []

def detect_anomalies(data):
    """
    Detect anomalies using Isolation Forest algorithm with stricter parameters
    Returns the data with anomaly labels and anomaly indices
    """
    # Prepare features for anomaly detection
    features = ['proton_density', 'proton_speed']
    
    # Remove rows with missing values and invalid data (-9999.9)
    clean_data = data.dropna(subset=features)
    clean_data = clean_data[(clean_data['proton_density'] != -9999.9) & 
                           (clean_data['proton_speed'] != -9999.9)]
    clean_data = clean_data[(clean_data['proton_density'] > 0) & 
                           (clean_data['proton_speed'] > 0)]
    
    if len(clean_data) < 50:  # Need more data points for better detection
        return data, []
    
    # Remove obvious outliers using IQR method first
    Q1_density = clean_data['proton_density'].quantile(0.25)
    Q3_density = clean_data['proton_density'].quantile(0.75)
    IQR_density = Q3_density - Q1_density
    
    Q1_speed = clean_data['proton_speed'].quantile(0.25)
    Q3_speed = clean_data['proton_speed'].quantile(0.75)
    IQR_speed = Q3_speed - Q1_speed
    
    # Keep data within reasonable bounds (extend IQR range)
    density_lower = Q1_density - 3 * IQR_density  # More lenient than 1.5
    density_upper = Q3_density + 3 * IQR_density
    speed_lower = Q1_speed - 3 * IQR_speed
    speed_upper = Q3_speed + 3 * IQR_speed
    
    filtered_data = clean_data[
        (clean_data['proton_density'] >= density_lower) & 
        (clean_data['proton_density'] <= density_upper) &
        (clean_data['proton_speed'] >= speed_lower) & 
        (clean_data['proton_speed'] <= speed_upper)
    ]
    
    if len(filtered_data) < 20:
        return data, []
    
    # Use much lower contamination rate for stricter anomaly detection
    iso_forest = IsolationForest(
        contamination=0.01,  # Only 1% instead of 5%
        random_state=42,
        n_estimators=200,    # More trees for better detection
        max_samples=min(256, len(filtered_data))  # Limit sample size
    )
    
    anomaly_labels = iso_forest.fit_predict(filtered_data[features])
    
    # Add anomaly labels to the data (-1 = anomaly, 1 = normal)
    filtered_data = filtered_data.copy()
    filtered_data['anomaly'] = anomaly_labels
    
    # Get anomaly indices - only the most extreme ones
    anomalies = filtered_data[filtered_data['anomaly'] == -1]
    
    # Additional filtering: only keep anomalies that are really extreme
    if len(anomalies) > 0:
        # Calculate z-scores for additional filtering
        density_mean = filtered_data['proton_density'].mean()
        density_std = filtered_data['proton_density'].std()
        speed_mean = filtered_data['proton_speed'].mean()
        speed_std = filtered_data['proton_speed'].std()
        
        anomalies['density_zscore'] = np.abs((anomalies['proton_density'] - density_mean) / density_std)
        anomalies['speed_zscore'] = np.abs((anomalies['proton_speed'] - speed_mean) / speed_std)
        
        # Only keep anomalies with z-score > 3 (very extreme)
        extreme_anomalies = anomalies[
            (anomalies['density_zscore'] > 3) | (anomalies['speed_zscore'] > 3)
        ]
        
        return filtered_data, extreme_anomalies
    
    return filtered_data, anomalies

def collect_anomalies(anomalies, year, month):
    """
    Collect anomalies to be written to the master log file later
    """
    if len(anomalies) == 0:
        return
    
    for idx, row in anomalies.iterrows():
        anomaly_record = {
            'year': year,
            'month': month + 1,
            'datetime': row['datetime'],
            'proton_density': row['proton_density'],
            'proton_speed': row['proton_speed'],
            'density_zscore': row.get('density_zscore', 0),
            'speed_zscore': row.get('speed_zscore', 0)
        }
        all_anomalies.append(anomaly_record)

def write_master_log():
    """
    Write all collected anomalies to one master log file
    """
    if len(all_anomalies) == 0:
        print("No anomalies detected across all data.")
        return
    
    log_file = "C:\\Users\\rites\\Downloads\\Solar-Wind-Disappearance\\MASTER_ANOMALIES_LOG.txt"
    
    # Sort anomalies by datetime
    sorted_anomalies = sorted(all_anomalies, key=lambda x: x['datetime'])
    
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("MASTER ANOMALY LOG - SOLAR WIND DATA\n")
        f.write("="*60 + "\n")
        f.write(f"Total anomalies detected: {len(sorted_anomalies)}\n")
        f.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*60 + "\n\n")
        
        # Group by year for better organization
        current_year = None
        year_count = 0
        
        for anomaly in sorted_anomalies:
            if current_year != anomaly['year']:
                if current_year is not None:
                    f.write(f"\nYear {current_year} total: {year_count} anomalies\n")
                    f.write("-" * 40 + "\n\n")
                
                current_year = anomaly['year']
                year_count = 0
                f.write(f"YEAR {current_year}\n")
                f.write("=" * 20 + "\n")
            
            year_count += 1
            
            f.write(f"#{len([a for a in sorted_anomalies[:sorted_anomalies.index(anomaly)+1] if a['year'] == current_year]):03d} | ")
            f.write(f"Month {anomaly['month']:02d} | {anomaly['datetime']}\n")
            f.write(f"     Proton Density: {anomaly['proton_density']:.2f} cm^-3 (Z-score: {anomaly['density_zscore']:.2f})\n")
            f.write(f"     Proton Speed: {anomaly['proton_speed']:.2f} km/s (Z-score: {anomaly['speed_zscore']:.2f})\n")
            f.write("\n")
        
        # Final year count
        if current_year is not None:
            f.write(f"Year {current_year} total: {year_count} anomalies\n")
            f.write("-" * 40 + "\n\n")
        
        # Summary statistics
        f.write("SUMMARY STATISTICS\n")
        f.write("="*30 + "\n")
        years = list(set([a['year'] for a in sorted_anomalies]))
        for year in sorted(years):
            year_anomalies = [a for a in sorted_anomalies if a['year'] == year]
            f.write(f"{year}: {len(year_anomalies)} anomalies\n")
    
    print(f"\nMaster anomaly log written to: {log_file}")
    print(f"Total anomalies logged: {len(sorted_anomalies)}")

def generate_graph(data, file_name, month):
    """
    Generate scatter plot with anomalies highlighted
    """
    # Filter out invalid data first
    valid_data = data[(data['proton_density'] != -9999.9) & 
                     (data['proton_speed'] != -9999.9) &
                     (data['proton_density'] > 0) & 
                     (data['proton_speed'] > 0)]
    
    if len(valid_data) < 50:
        print(f"Insufficient valid data for {file_name} month {month+1:02d}")
        return
    
    # Detect anomalies
    data_with_anomalies, anomalies = detect_anomalies(valid_data)
    
    # Create output folders - extract just the year from filename
    year_only = file_name.replace('ACE_SW_Proton_Data_', '').replace('.csv', '')
    graph_folder = f"C:\\Users\\rites\\Downloads\\Solar-Wind-Disappearance\\Monthly_graphs\\{year_only}"
    
    os.makedirs(graph_folder, exist_ok=True)
    
    # Collect anomalies for master log
    collect_anomalies(anomalies, year_only, month)
    
    # Create the plot
    plt.figure(figsize=(12, 8))
    
    # Plot normal data points
    normal_data = data_with_anomalies[data_with_anomalies['anomaly'] == 1] if 'anomaly' in data_with_anomalies.columns else data_with_anomalies
    
    if len(normal_data) > 0:
        scatter = sns.scatterplot(
            data=normal_data,
            x="datetime",
            y="proton_density",
            hue="proton_speed",
            palette="viridis",
            s=30,
            alpha=0.7
        )
    
    # Highlight anomalies in red
    if len(anomalies) > 0:
        plt.scatter(
            anomalies["datetime"],
            anomalies["proton_density"],
            color='red',
            s=150,  # Larger markers for better visibility
            alpha=0.9,
            marker='x',
            linewidths=3
        )
        # Add anomaly legend manually
        plt.legend(handles=[plt.Line2D([0], [0], marker='x', color='red', 
                                      linestyle='None', markersize=12, markeredgewidth=3,
                                      label=f'Extreme Anomalies ({len(anomalies)})')],
                  loc='upper right')
    
    plt.title(f"Proton Density vs. Timestamp - {year_only} Month {month+1:02d}\n(Extreme anomalies highlighted in red)")
    plt.xlabel("Timestamp")
    plt.ylabel("Proton Density (cm^-3)")
    
    # Set reasonable y-axis limits based on valid data
    if len(valid_data) > 0:
        y_min = max(0.1, valid_data['proton_density'].quantile(0.01))
        y_max = valid_data['proton_density'].quantile(0.99)
        plt.ylim(y_min, y_max)
    
    plt.tight_layout()
    
    # Save the graph
    plt.savefig(os.path.join(graph_folder, f"{year_only}_month_{month+1:02d}.png"), dpi=300, bbox_inches='tight')
    plt.close()  # Close the figure to free memory
    
    print(f"Generated graph for {year_only} month {month+1:02d} with {len(anomalies)} extreme anomalies detected")

# Create main output directories
os.makedirs("C:\\Users\\rites\\Downloads\\Solar-Wind-Disappearance\\Monthly_graphs", exist_ok=True)

print("Available years:", data_list)
print("Starting graph generation with strict anomaly detection...")

for year in data_list:
    try:
        yearly_data = utils.get_monthly_data(f"C:\\Users\\rites\\Downloads\\Solar-Wind-Disappearance\\CSV\\{year}")
        print(f"\nProcessing year: {year}")
        
        for month in range(len(yearly_data)):
            generate_graph(yearly_data[month], year, month)
                
    except Exception as e:
        print(f"Error processing year {year}: {str(e)}")

# Write the master log file after processing all data
write_master_log()

print("\nGraph generation completed!")
print("Graphs saved in: Monthly_graphs/<year>/")
print("Master anomaly log saved as: MASTER_ANOMALIES_LOG.txt")