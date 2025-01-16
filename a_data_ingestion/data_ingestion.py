"""
A script to load the raw 'used-car-dataset' data into a cloud storage bucket and then into a big query dataset
"""

"""
TODO:
- Fix end-user-credentials thing
- Write script to upload csv to dataset
- Create a cloud function that triggers when the csv lands in the storage bucket

"""


from google.auth import default


import kagglehub
import pandas as pd
import numpy as np
import os
import os.path
import logging
from google.cloud import storage, bigquery
from google.cloud.exceptions import NotFound

logging.basicConfig(level = logging.INFO)

def download_kaggle_dataset():
    logging.info('Downloading file...')
    existing_csv_file_path = '/Users/max.abimbola/.cache/kagglehub/datasets/austinreese/craigslist-carstrucks-data/versions/10/vehicles.csv'  

    if os.path.isfile(existing_csv_file_path):
        logging.info('file already exists cancelling download...')
        return


    kaggle_dataset_path = kagglehub.dataset_download("austinreese/craigslist-carstrucks-data")
    logging.info('dataest succesfully downloaded from kaggle')
    print("Path to dataset files:", kaggle_dataset_path)


def upload_csv_to_storage_blob():
    kaggle_dataset_path = '/Users/max.abimbola/.cache/kagglehub/datasets/austinreese/craigslist-carstrucks-data/versions/10/vehicles.csv'
    
    try:

        storage_client = storage.Client(project='dt-maxa-sandbox-dev')

        bucket = storage_client.bucket('landing-zone-used-car-data')

        storage_client.create_bucket(bucket, location='europe-west2')

        blob = bucket.blob('vehicles.csv')
        blob.upload_from_filename(kaggle_dataset_path, num_retries=3,timeout=1000)

        logging.info('Successfully uploaded csv to storage bucket')

    except Exception as e:
        logging.info(f"Bucket already exists. Loading data...")

        bucket = storage_client.bucket('landing-zone-used-car-data')

        blob = bucket.blob('raw-used-car-data')
        blob.upload_from_filename(kaggle_dataset_path, num_retries=3, timeout=1000)

        logging.info('Successfully uploaded csv to storage bucket')

def create_bigquery_dataset(dataset_id):

    # Construct a BigQuery client object.
    client = bigquery.Client(location = "europe-west2")


    dataset_ref = client.dataset(dataset_id)

    dataset = bigquery.Dataset(dataset_ref)

    dataset.location = "EU"

    # Send the dataset to the API for creation, with an explicit timeout.
    # Raises google.api_core.exceptions.Conflict if the Dataset already
    # exists within the project.
    dataset = client.create_dataset(dataset, timeout=30)  # Make an API request.
    logging.info("Created dataset {}.{}".format(client.project, dataset.dataset_id))

def upload_blob_to_bigquery(project_id, bucket_name, destination_file, table_id, dataset_id):
        bigquery_client = bigquery.Client(project=project_id, location="europe-west2")

        try:
            dataset = bigquery_client.get_dataset(dataset_id)
            logging.info(f"Dataset with dataset_id: {dataset_id} already exists.")

        except NotFound:
            logging.info(f"Dataset with dataset_id: {dataset_id} not found. Creating dataset {dataset_id}...")

            dataset = bigquery.Dataset(dataset_id)
            dataset.location="europe-west2"
            bigquery_client.create_dataset(dataset_id)

            logging.info(f"Dataset {dataset} created successfully.")
        
#        table = bigquery.Table(table_id)
        try:
            bigquery_client.get_table(table_id)
            logging.info(f"Table {table_id} already exists")

        except NotFound:
            logging.info(f"Table with table_id: {table_id} not found. Creating table {table_id}...")
            bigquery_client.create_table(table_id)
            logging.info(f"Table {table_id} created successfully.")

        job_config = bigquery.LoadJobConfig(
                autodetect=True,
                skip_leading_rows=1,
                allow_jagged_rows=True,
                allow_quoted_newlines=True,
                ignore_unknown_values=True,
                source_format=bigquery.SourceFormat.CSV
        )
        uri = f"gs://{bucket_name}/{destination_file}"

        load_job = bigquery_client.load_table_from_uri(uri, table_id, job_config=job_config)
        logging.info('Starting job {}'.format(load_job.job_id))

        load_job.result()
        logging.info("Data loaded successfully to BigQuery")

   


def main():
    download_kaggle_dataset()
    upload_csv_to_storage_blob()

if __name__ == '__main__':
    main()
