import functions_framework
from google.cloud import bigquery

client = bigquery.Client()

table_id = "dt-maxa-sandbox-dev.uncleaned_data.raw_car_data"

# Triggered by a change in a storage bucket
@functions_framework.cloud_event
def load_to_bq(cloud_event):
    data = cloud_event.data

    event_id = cloud_event["id"]
    event_type = cloud_event["type"]

    bucket = data["bucket"]
    name = data["name"]

    print('hello world!')
    # metageneration = data["metageneration"]
    # timeCreated = data["timeCreated"]
    # updated = data["updated"]

    # job_config = bigquery.LoadJobConfig(
    #     skip_leading_rows = 1,
    #     source_format = bigquery.SourceFormat.CSV,
    #     allow_quoted_newlines = True,
    # )

    # gcs_uri = f"gs://{bucket}/{name}"

    # load_job = client.load_table_from_uri(
    #     gcs_uri, table_id, job_config=job_config
    # ) # Make an API request.

    # load_job.result()
