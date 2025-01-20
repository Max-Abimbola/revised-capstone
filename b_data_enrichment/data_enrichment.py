from google.cloud import bigquery
from google.cloud import storage
import requests
import math


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

def return_updated_values(delimitted_vin_list):
    url = f'https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVINValuesBatch/1C6RR6FG0JS259587;5TFCZ5AN0KX185798'
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




def main():
    vin_list = return_extracted_vins()[:156]

    while len(vin_list) != 0:
        batch_vin_list = vin_list[0:min(50,len(vin_list))]

        vin_list = vin_list[min(50,len(vin_list)):]

        # updated_values = return_updated_values(delimitted_vin_list)

    

if __name__ == "__main__":
    main()
