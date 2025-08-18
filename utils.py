files_list = []
import os
import csv 

def get_files():
    try:
        all_entries = os.listdir("C:\\Users\\rcvil\\Heliospheric Anomaly\\ACE CSV\\Graphs\\CSV")
        files = [entry for entry in all_entries if os.path.isfile(os.path.join(".", entry))]
        print("Files in the folder:")
        for file_name in files:
            print(file_name)
            files_list.append(file_name)
    except FileNotFoundError:
        print("Error: Folder not found at '{""}'")

    return files_list


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
