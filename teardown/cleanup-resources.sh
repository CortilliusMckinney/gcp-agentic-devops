#!/bin/bash

echo "🧹 Agentic DevOps System Teardown"
echo "This will remove all project resources to prevent ongoing charges"
echo ""

read -p "Are you sure you want to delete all resources? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Teardown cancelled"
    exit 0
fi

echo "📋 Cleaning up Cloud Functions..."
gcloud functions delete diagnose-event --region=YOUR_REGION --quiet
gcloud functions delete validate-fix-event --region=YOUR_REGION --quiet
gcloud functions delete remediate-event --region=YOUR_REGION --quiet
gcloud functions delete log-analytics-processor --region=YOUR_REGION --quiet
gcloud functions delete diagnoser-agent --region=YOUR_REGION --quiet
gcloud functions delete validator-agent --region=YOUR_REGION --quiet
gcloud functions delete remediator-agent --region=YOUR_REGION --quiet
echo "✅ Cloud Functions deleted"

echo "📋 Cleaning up Pub/Sub resources..."
gcloud pubsub subscriptions delete test-analytics-sub --quiet
gcloud pubsub topics delete pipeline-events --quiet
gcloud pubsub topics delete validation-requests --quiet
gcloud pubsub topics delete remediation-tasks --quiet
gcloud pubsub topics delete log-analytics --quiet
echo "✅ Pub/Sub resources deleted"

echo "📋 Cleaning up BigQuery resources..."
bq rm -r -f YOUR_PROJECT_ID:agent_analytics
echo "✅ BigQuery dataset deleted"

echo "📋 Cleaning up Cloud Logging sinks..."
gcloud logging sinks delete analytics-sink --quiet
echo "✅ Logging sinks deleted"

echo "📋 Cleaning up Secret Manager secrets..."
gcloud secrets delete openai-api-key --quiet
gcloud secrets delete anthropic-api-key --quiet
gcloud secrets delete cloudflare-api-token --quiet
gcloud secrets delete cloudflare-account-id --quiet
echo "✅ Secrets deleted"

echo "📋 Cleaning up IAM service accounts..."
PROJECT_ID=$(gcloud config get-value project)
gcloud iam service-accounts delete agentic-devops@${PROJECT_ID}.iam.gserviceaccount.com --quiet
echo "✅ Service accounts deleted"

echo "📋 Cleaning up Terraform state..."
cd ../terraform
terraform destroy -auto-approve
rm -f terraform.tfstate*
rm -rf .terraform/
echo "✅ Terraform resources destroyed"

echo ""
echo "🎯 Teardown Summary"
echo "==================="
echo "✅ All Cloud Functions removed"
echo "✅ All Pub/Sub topics and subscriptions deleted"
echo "✅ BigQuery dataset and tables removed"
echo "✅ Cloud Logging sinks deleted"
echo "✅ Secret Manager secrets removed"
echo "✅ IAM service accounts deleted"
echo "✅ Terraform infrastructure destroyed"
echo ""
echo "💰 Expected cost impact: ~$0/month (all billable resources removed)"
echo "🔐 Security impact: All API keys and sensitive data removed"
