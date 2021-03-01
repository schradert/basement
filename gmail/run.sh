#!/bin/bash
export $(xargs <.env)

zip -r gmail.zip credentials.json main.py requirements.txt token.pickle
gsutil cp gmail.zip $GMAIL_BUCKET

gcloud projects add-iam-policy-binding $GMAIL_PROJECT_ID --member=serviceAccount:$GMAIL_SERVICE_ACCOUNT --role=roles/cloudscheduler.serviceAgent
gcloud functions deploy $GMAIL_FUNC_NAME --runtime python39 --trigger-http --entry-point=process_new_emails --source="${$GMAIL_BUCKET}gmail.zip"
gcloud functions add-iam-policy-binding $GMAIL_FUNC_NAME --member serviceAccount:$GMAIL_SERVICE_ACCOUNT --role roles/cloudfunctions.invoker
gcloud scheduler jobs create http $GMAIL_JOB_NAME --schedule="0 7 * * *" --uri=$GMAIL_FUNCTION_URL --oidc-service-account-email=$GMAIL_SERVICE_ACCOUNT