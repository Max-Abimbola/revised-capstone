"""
A script to load the raw 'used-car-dataset' data into a cloud storage bucket and then into a big query dataset
"""

import kagglehub
import pandas as pd
import numpy as np
import os
import os.path
import logging
from google.cloud import storage

def download_kaggle_dataset():
    existing_csv_file_path = '/Users/max.abimbola/.cache/kagglehub/datasets/austinreese/craigslist-carstrucks-data/versions/10'  
    if os.path.isfile(existing_csv_file_path):
        logging.info('file already exists...')
        return


    kaggle_dataset_path = kagglehub.dataset_download("austinreese/craigslist-carstrucks-data")
    logging.info('dataest succesfully downloaded from kaggle')
    print("Path to dataset files:", kaggle_dataset_path)


def upload_csv_to_storage_blob():
    path = '/Users/max.abimbola/.cache/kagglehub/datasets/austinreese/craigslist-carstrucks-data/versions/10'  
    df = pd.read_csv(path)
    print(df.head())

def main():
    download_kaggle_dataset()
    upload_csv_to_storage_blob()

if __name__ == '__main__':
    main()
