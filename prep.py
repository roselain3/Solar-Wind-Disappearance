import csv
import pandas as pd
import utils
import os


data_list = utils.get_files()


for each in data_list:
    utils.add_headers(each)





