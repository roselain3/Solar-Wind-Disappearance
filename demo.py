import csv
import pandas as pd
import utils
import os
import seaborn as sns
import matplotlib.pyplot as plt  


def get_monthly_data(file_name):
    willabyte = pd.read_csv(file_name)
    willabyte['datetime'] = pd.to_datetime(willabyte[['Year', 'Day', 'Hour', 'Minute']].astype(str).agg('-'.join, axis=1), format='%Y-%j-%H-%M')
    willabyte['month'] = willabyte['datetime'].dt.month
    months = willabyte['month'].unique()
    months.sort()
    print(willabyte.head())
    return months.tolist()

    

print(get_monthly_data("C:\\Users\\rcvil\\Heliospheric Anomaly\\ACE CSV\\Graphs\\CSV\\ACE_SW_Proton_Data_2008.csv"))