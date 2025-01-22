from google.cloud import bigquery
from google.cloud import storage
import requests
import math
import os

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
    print(task_id)
    vin_list = return_extracted_vins()[:301]

    curr_job_vin_batch_size = math.ceil(len(vin_list)/total_tasks)

    start = (task_id)*curr_job_vin_batch_size
    end = min(len(vin_list),start+curr_job_vin_batch_size) 

    curr_job_vin_list = vin_list[start:end]

    print(f"Length of vin list is {len(vin_list)}")
    print(f"I'm processing from {start}-{end}")
    print(f"I'm processing {len(curr_job_vin_list)} VINs")

    return

    # curr_job_vin_list = vin_list[task_id*curr_job_vin_batch_size:(task_id*curr_job_vin_batch_size)+(curr_job_vin_batch_size-1)]

    while len(vin_list) != 0:
        batch_vin_list = curr_job_vin_list[0:min(50,len(vin_list))]

        curr_job_vin_list = curr_job_vin_list[min(50,len(vin_list)):]

        updated_values = return_updated_values(batch_vin_list)

        print(updated_values)


def main():
    total_tasks = 3
    task_id = int(os.environ.get('CLOUD_RUN_TASK_INDEX'))
    write_updated_values_to_csv(total_tasks,task_id)

    

if __name__ == "__main__":
    main()
