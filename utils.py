files_list = []
import os
import csv
import pandas as pd

def get_files():
    try:
        all_entries = os.listdir("C:\\Users\\cpa50\\.vscode\\Heliospheric\\Solar-Wind-Disappearance\\CSV")
        # files = [entry for entry in all_entries if os.path.isfile(os.path.join(".", entry))]
        files = all_entries
        print("Files in the folder:")
        for file_name in files:
            print(file_name)
            files_list.append(file_name)
    except FileNotFoundError:
        print("Error: Folder not found at '{""}'")

    return files_list

# print(get_files())
def grab_file_data(file_name):
  with open(f"{file_name}", "r", encoding="utf-8") as file:
      reader = csv.reader(file)
      return list(reader)


def add_headers(file_name):
    file_data = grab_file_data(file_name)
    header = ["Year", "Day", "Hour", "Minute", "proton_density", "proton_speed"]
    final_file_data = [header] + file_data
    with open(f"{file_name}", "w", encoding="utf-8") as file:
      writer = csv.writer(file)
      writer.writerows(final_file_data)


def get_monthly_data(file_name):
    willabyte = pd.read_csv(file_name)
    willabyte['datetime'] = pd.to_datetime(willabyte[['Year', 'Day', 'Hour', 'Minute']].astype(str).agg('-'.join, axis=1), format='%Y-%j-%H-%M')
    willabyte['month'] = willabyte['datetime'].dt.month
    months = willabyte['month'].unique()
    months.sort()
    print(willabyte.head())
    monthly_data = []
    print(len(months))
    for month in months:
        monthly_data.append(willabyte[willabyte['month'] == month])
    return monthly_data

