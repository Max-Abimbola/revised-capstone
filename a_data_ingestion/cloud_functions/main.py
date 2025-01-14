import functions_framework
import logging
from google.cloud import bigquery
logging.basicConfig(level = logging.INFO)
client = bigquery.Client()

table_schema = [ 
    bigquery.SchemaField("id", "INTEGER"),
    bigquery.SchemaField("url", "STRING"),
    bigquery.SchemaField("region", "STRING"),
    bigquery.SchemaField("region_url", "STRING"),
    bigquery.SchemaField("price", "FLOAT64"),
    bigquery.SchemaField("year", "STRING"),
    bigquery.SchemaField("manufacturer", "STRING"),
    bigquery.SchemaField("model", "STRING"),
    bigquery.SchemaField("condition", "STRING"),
    bigquery.SchemaField("cylinders", "STRING"),
    bigquery.SchemaField("fuel", "STRING"),
    bigquery.SchemaField("odometer", "FLOAT64"),
    bigquery.SchemaField("title_status", "STRING"),
    bigquery.SchemaField("transmission", "STRING"),
    bigquery.SchemaField("VIN", "STRING"),
    bigquery.SchemaField("drive", "STRING"),
    bigquery.SchemaField("size", "STRING"),
    bigquery.SchemaField("type", "STRING"),
    bigquery.SchemaField("paint_color", "STRING"),
    bigquery.SchemaField("image_url", "STRING"),
    bigquery.SchemaField("description", "STRING"),
    bigquery.SchemaField("county", "STRING"),
    bigquery.SchemaField("state", "STRING"),
    bigquery.SchemaField("lat", "STRING"),
    bigquery.SchemaField("long", "STRING"),
    bigquery.SchemaField("posting_date", "STRING")
]

table_id = "dt-maxa-sandbox-dev.uncleaned_data.raw_car_data"

# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def load_to_bq(cloud_event):
    print('SANITY CHECKKK')
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]

    print(f"THIS IS THE NAME:{name}")

    metageneration = data["metageneration"]
    timeCreated = data["timeCreated"]
    updated = data["updated"]

    job_config = bigquery.LoadJobConfig(
        schema = table_schema,
        skip_leading_rows = 1,
        source_format = bigquery.SourceFormat.CSV,
        allow_quoted_newlines = True,
        write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    gcs_uri = f"gs://{bucket}/{name}"

    logging.info('Loading csv to bigquery...')
    
    load_job = client.load_table_from_uri(
        gcs_uri, table_id, job_config=job_config
    ) # Make an API request.

    load_job.result()

    logging.info('Successfully loaded csv to bigquery')
    print("Succcess???")
