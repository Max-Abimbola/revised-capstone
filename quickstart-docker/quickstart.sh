echo "Hello world! The time is $(date)."



gcloud builds triggers create github \                                            
--region=europe-west2 \
--repo-name=revised-capstone \
--repo-owner=maxabimbola \
--branch-pattern=data_enrichment \
--build-config=quickstart-docker/cloudbuild.yaml \
--service-account=max-dev@dt-maxa-sandbox-dev.iam.gserviceaccount.com

gcloud builds triggers create github \                    
--region=europe-west2 \                                          
--repo-name=revised-capstone \
--repo-owner=maxabimbola \
--branch-pattern=data_enrichment \
--build-config=quickstart-docker/cloudbuild.yaml \
--service-account=max-dev@dt-maxa-sandbox-dev.iam.gserviceaccount.com \


    gcloud builds triggers create github \
    --region=europe-west2 \
    --repo-name=https://github.com/Max-Abimbola/revised-capstone \
    --repo-owner=maxabimbola \
    --branch-pattern=data_enrichment \
    --build-config=quickstart-docker/cloudbuild.yaml \
    --service-account=projects/dt-maxa-sandbox-dev/serviceAccounts/max-dev@dt-maxa-sandbox-dev.iam.gserviceaccount.com
