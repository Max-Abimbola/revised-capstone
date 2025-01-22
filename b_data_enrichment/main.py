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

    delimitted_vin_list = ';'.join(batch_vin_list)

    url = f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/'
    post_fields = {'format': 'json', 'data':delimitted_vin_list}
    r = requests.post(url, data=post_fields)
    response_dict = dict(r.json())['Results']
    
    new_values_dict = []
    for vin in response_dict:
        curr_val = {}
        curr_val['VIN'] = vin.get('VIN')
        curr_val['cylinders'] = vin.get('EngineCylinders','')
        curr_val['drive'] = vin.get('DriveType',''),
        curr_val['fuel_type'] = vin.get('FuelTypePrimary','')
        curr_val['make'] = vin.get('Make','')
        curr_val['vehicle_type'] = vin.get('VehicleType','')
        
        new_values_dict.append(curr_val)
    return(new_values_dict)

def write_updated_values_to_csv(total_tasks, task_id):
    storage_client = storage.Client()
    bucket = storage_client.bucket('landing-zone-used-car-data')
    blob = bucket.blob('used-card-data-enriched.csv')

    print(task_id)
    vin_list = return_extracted_vins()[:301]

    curr_job_vin_batch_size = math.ceil(len(vin_list)/total_tasks)

    start = (task_id)*curr_job_vin_batch_size
    end = min(len(vin_list),start+curr_job_vin_batch_size) 

    curr_job_vin_list = vin_list[start:end]

    print(f"Length of vin list is {len(vin_list)}")
    print(f"I'm processing from {start}-{end}")
    print(f"I'm processing {len(curr_job_vin_list)} VINs")

    # curr_job_vin_list = vin_list[task_id*curr_job_vin_batch_size:(task_id*curr_job_vin_batch_size)+(curr_job_vin_batch_size-1)]

    while len(curr_job_vin_list) != 0:
        batch_vin_list = curr_job_vin_list[0:min(50,len(curr_job_vin_list))]

        updated_values = return_updated_values(batch_vin_list)

        curr_job_vin_list = curr_job_vin_list[min(50,len(curr_job_vin_list)):]

        print(f"curr_job_vin_list size {len(curr_job_vin_list)}")

        updated_values_df = pd.DataFrame(updated_values)
        updated_values_csv = updated_values_df.to_csv()

        try:
            # First, try to download existing content
            try:
                existing_content = blob.download_as_text()
            except google.cloud.exceptions.NotFound:
                existing_content = ""
        

            # Combine existing and new content
            combined_content = existing_content
            if existing_content and not existing_content.endswith('\n'):
                combined_content += '\n'
            
            # Convert new rows to CSV string

            # output = io.StringIO()
            # csv_writer = csv.writer(output)
            # print(updated_values)
            # csv_writer.writerows(updated_values_csv)
            # combined_content += output.getvalue()
            
            # Upload with atomic write using generation and metageneration
            generation_match_precondition = 0 if not existing_content else None
            blob.upload_from_string(
                updated_values_csv, 
                if_generation_match=generation_match_precondition
            )
            return
        
        except google.cloud.exceptions.Conflict:
            # This occurs if the file was modified between read and write
            logging.warning(f"Concurrent write detected for task {task_id}. Skipping this batch.")
        except Exception as e:
            logging.error(f"Error in task {task_id}: {str(e)}")
            raise


def main():
    total_tasks = 3
    # task_id = int(os.environ.get('CLOUD_RUN_TASK_INDEX'))
    write_updated_values_to_csv(total_tasks,task_id=1)

    

if __name__ == "__main__":
    main()
