
# Anything in square brackets [] replace with value

# Step 1: Create a Repository in Artefact Registry (use the same repo for the data pipeline)

# Step 2: Build the Docker Image with Podman and Push to Artifact Registry
# Authenticate

# Build image
docker buildx build -t data-enrichment --platform linux/amd64 .

# Tag image 
docker tag data-enrichment europe-west2-docker.pkg.dev/dt-maxa-sandbox-dev/cloud-run-repo/data-enrichment:latest

# Push to arefact registry
docker push europe-west2-docker.pkg.dev/dt-maxa-sandbox-dev/cloud-run-repo/data-enrichment

# Step 3: Deploy image to cloud run job
gcloud run jobs deploy data-enrichment \
    --image=europe-west2-docker.pkg.dev/dt-maxa-sandbox-dev/cloud-run-repo/data-enrichment \
    --region=europe-west2 \
    --command='python','main.py' \
    --project=dt-maxa-sandbox-dev \
    --service-account=max-dev@dt-maxa-sandbox-dev.iam.gserviceaccount.com \
    --tasks=4 \
    --max-retries=6 \

    # --set-env-vars=PROJECT_ID=dt-maxa-sandbox-dev,BUCKET_NAME=[BUCKET_NAME],REGION=europe-west2,DATASET_ID=[DATASET_ID],DESTINATION_TABLE_ID=[DESTINATION_TABLE_ID] \




# To execute the job manually as individual container
gcloud run jobs execute data-enrichment \
    --region=europe-west2 
