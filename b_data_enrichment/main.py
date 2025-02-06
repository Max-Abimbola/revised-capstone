from google.cloud import bigquery
from google.cloud import storage
import requests
import math
import os
import pandas as pd
import io
import google.cloud.exceptions
import logging
import csv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO) 

def return_extracted_vins():
    """
    This function extracts a list of VINs from BigQuery table 'raw_car_data'
    that have null values in specific columns

    Returns:
        list: A list of VINs extracted from the BigQuery table
    """
    client = bigquery.Client(project="dt-maxa-sandbox-dev")
    query = """
                SELECT distinct VIN FROM `dt-maxa-sandbox-dev.uncleaned_data.raw_car_data`
                WHERE cylinders is null or 
                condition is null or 
                drive is null or 
                fuel is null or
                manufacturer is null or 
                model is null or
                size is null or 
                type is null and
                VIN is not null
            """
    query_job = client.query(query)
    results = query_job.result().to_dataframe()
    csv_string = results.to_csv(index=False)
    vin_list = csv_string.split('\n')[2:]
    return vin_list


def return_updated_values(batch_vin_list):
    print("Test: CI")
    """
    This function takes a batch of VINs and retrieves their corresponding
    vehicle data (cylinders, drive type, fuel type, make, vehicle type)
    from the NHTSA vpic api

    Args:
        batch_vin_list: A list of VINs to query the NHTSA vpic api

    Returns:
        list: A list of dictionaries containing VIN and vehicle data
    """
    delimitted_vin_list = ';'.join(batch_vin_list)

    url = f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/'
    post_fields = {'format': 'json', 'data':delimitted_vin_list}
    r = requests.post(url, data=post_fields)
    response_dict = dict(r.json())['Results']
    
    new_values_list = []
    for vin in response_dict:
        curr_val = [
            vin.get('VIN'),
            vin.get('EngineCylinders',''),
            vin.get('DriveType',''),
            vin.get('FuelTypePrimary',''),
            vin.get('Make',''),
            vin.get('VehicleType','')
        ]
        
        new_values_list.append(curr_val)
    return(new_values_list)

def write_updated_values_to_csv(total_tasks, task_id):
    """
    This function writes enriched car data (VIN, cylinders, drive type, fuel type, make, vehicle type)
    to a CSV file in Google Cloud Storage in a batched manner with chunking and error handling.

    Args:
        total_tasks: The total number of tasks that will be processing the data in parallel
        task_id: The ID of the current task

    Raises:
        Exception: An exception if there is an error during the processing
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket('landing-zone-used-car-data')
    blob = bucket.blob('used-card-data-enriched.csv')

    vin_list = return_extracted_vins()

    curr_job_vin_batch_size = math.ceil(len(vin_list)/total_tasks)

    start = (task_id)*curr_job_vin_batch_size
    end = min(len(vin_list),start+curr_job_vin_batch_size) 

    curr_job_vin_list = vin_list[start:end]

    print(f"Length of vin list is {len(vin_list)}")
    print(f"task {task_id} processing from {start}-{end}")
    print(f"I'm processing {len(curr_job_vin_list)} VINs")


    output = io.StringIO()

    while len(curr_job_vin_list) != 0:
        batch_vin_list = curr_job_vin_list[0:min(50,len(curr_job_vin_list))]

        updated_values = return_updated_values(batch_vin_list)

        curr_job_vin_list = curr_job_vin_list[min(50,len(curr_job_vin_list)):]

        print(f"curr_job_vin_list size {len(curr_job_vin_list)}")
        
        csv_writer = csv.writer(output)
        csv_writer.writerows(updated_values)

    try:
        # First, try to download existing content
        try:
            existing_content = blob.download_as_string().decode('utf-8')
            logging.info('Existing content found.')
            logging.info('Concatenating new content...')
            
        except google.cloud.exceptions.NotFound:
            logging.info('No existing content was found')

            existing_content = ""

        combined_content = existing_content + output.getvalue()


        # Upload with atomic write using generation and metageneration

        generation_match_precondition = 0 if not existing_content else None 
        blob.upload_from_string(
            combined_content, 
            if_generation_match=generation_match_precondition,
            content_type='text/csv'
        )
        # print("df_shape: ",combined_content.shape)   
    except google.cloud.exceptions.Conflict:
        # This occurs if the file was modified between read and write
        logging.warning(f"Concurrent write detected for task {task_id}. Skipping this batch.")
    except Exception as e:
        logging.error(f"Error in task {task_id}: {str(e)}")
        raise


def create_materialised_view(dataset_id, view_name, table1, table2, project_ID ="dt-grad-emea1-cap-dev"):
    try:
        client = bigquery.Client(project=project_ID)

        sql_t = f"""
        CREATE OR REPLACE MATERIALIZED VIEW `{dataset_id}.{view_name}` AS
        SELECT 
        t1.id,
        t2.model AS model,
        t1.url, t1.region, t1.region_url, t1.price, t1.year, t1.manufacturer, t1.cylinders, 
        t1.condition, t1.fuel, t1.odometer, t1.title_status, t1.transmission, t1.VIN,
        t1.drive, t1.size, t1.type, t1.paint_color, t1.image_url, t1.description, 
        t1.county, t1.state, t1.lat, t1.long, t1.posting_date
        FROM `{table1}` t1
        LEFT JOIN `{table2}` t2
        ON t1.VIN = t2.VIN  
        """

        query_job = client.query(sql_t)
        query_job.result()

        print(f"Materialized view `{view_name}` created successfully.")

    except Exception as e:
        print(f"Error creating materialized view: {e}")

def main():
    """
    The main function that orchestrates the data enrichment process.
    It kicks off the write_updated_values_to_csv function with 
    the total number of tasks and the current task ID.

    Raises:
        Exception: An exception if there is an error during the processing
    """
    total_tasks = 25
    task_id = int(os.environ.get('CLOUD_RUN_TASK_INDEX'))
    write_updated_values_to_csv(total_tasks,task_id)

if __name__ == "__main__":
    print('Hello world this is another big fat test')
