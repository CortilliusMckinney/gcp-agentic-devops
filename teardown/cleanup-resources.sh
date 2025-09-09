#!/bin/bash

echo "🧹 Agentic DevOps System Teardown"
echo "This will remove all project resources to prevent ongoing charges"
echo ""

# Check for placeholders and prompt for values
if grep -q "YOUR_REGION" "$0" || grep -q "YOUR_PROJECT_ID" "$0"; then
    echo "⚠️  Configuration required before running cleanup"
    echo ""
    
    # Get region
    if grep -q "YOUR_REGION" "$0"; then
        echo "Enter your GCP region (e.g., us-central1, europe-west1):"
        read -p "Region: " USER_REGION
        if [ -z "$USER_REGION" ]; then
            echo "❌ Region is required. Exiting."
            exit 1
        fi
        # Replace placeholder in this script
        sed -i.bak "s/YOUR_REGION/$USER_REGION/g" "$0"
        echo "✅ Region updated to: $USER_REGION"
    fi
    
    # Get project ID
    if grep -q "YOUR_PROJECT_ID" "$0"; then
        echo "Enter your GCP project ID:"
        read -p "Project ID: " USER_PROJECT_ID
        if [ -z "$USER_PROJECT_ID" ]; then
            echo "❌ Project ID is required. Exiting."
            exit 1
        fi
        # Replace placeholder in this script
        sed -i.bak "s/YOUR_PROJECT_ID/$USER_PROJECT_ID/g" "$0"
        echo "✅ Project ID updated to: $USER_PROJECT_ID"
    fi
    
    # Clean up backup file
    rm -f "$0.bak"
    
    echo ""
    echo "Configuration complete. Continuing with cleanup..."
    echo ""
fi

read -p "Are you sure you want to delete all resources? (yes/no): " confirm
if [ "$confirm" != "yes" ]; then
    echo "Teardown cancelled"
    exit 0
fi

echo "📋 Cleaning up Cloud Functions..."
functions=("diagnose-event" "validate-fix-event" "remediate-event" "log-analytics-processor" "diagnoser-agent" "validator-agent" "remediator-agent")
for func in "${functions[@]}"; do
    if gcloud functions describe $func --region=YOUR_REGION &>/dev/null; then
        gcloud functions delete $func --region=YOUR_REGION --quiet
        echo "   ✅ Deleted function: $func"
    else
        echo "   ℹ️  Function $func already deleted or does not exist"
    fi
done
echo "✅ Cloud Functions cleanup complete"

echo "📋 Cleaning up Pub/Sub resources..."
subscriptions=("test-analytics-sub")
topics=("pipeline-events" "validation-requests" "remediation-tasks" "log-analytics")

for sub in "${subscriptions[@]}"; do
    if gcloud pubsub subscriptions describe $sub &>/dev/null; then
        gcloud pubsub subscriptions delete $sub --quiet
        echo "   ✅ Deleted subscription: $sub"
    else
        echo "   ℹ️  Subscription $sub already deleted or does not exist"
    fi
done

for topic in "${topics[@]}"; do
    if gcloud pubsub topics describe $topic &>/dev/null; then
        gcloud pubsub topics delete $topic --quiet
        echo "   ✅ Deleted topic: $topic"
    else
        echo "   ℹ️  Topic $topic already deleted or does not exist"
    fi
done
echo "✅ Pub/Sub resources cleanup complete"

echo "📋 Cleaning up BigQuery resources..."
if bq ls -d YOUR_PROJECT_ID:agent_analytics &>/dev/null; then
    bq rm -r -f YOUR_PROJECT_ID:agent_analytics
    echo "   ✅ Deleted BigQuery dataset: agent_analytics"
else
    echo "   ℹ️  BigQuery dataset agent_analytics already deleted or does not exist"
fi
echo "✅ BigQuery cleanup complete"

echo "📋 Cleaning up Cloud Logging sinks..."
if gcloud logging sinks describe analytics-sink &>/dev/null; then
    gcloud logging sinks delete analytics-sink --quiet
    echo "   ✅ Deleted logging sink: analytics-sink"
else
    echo "   ℹ️  Logging sink analytics-sink already deleted or does not exist"
fi
echo "✅ Logging sinks cleanup complete"

echo "📋 Cleaning up Secret Manager secrets..."
secrets=("openai-api-key" "anthropic-api-key" "cloudflare-api-token" "cloudflare-account-id")
for secret in "${secrets[@]}"; do
    if gcloud secrets describe $secret &>/dev/null; then
        gcloud secrets delete $secret --quiet
        echo "   ✅ Deleted secret: $secret"
    else
        echo "   ℹ️  Secret $secret already deleted or does not exist"
    fi
done
echo "✅ Secret Manager cleanup complete"

echo "📋 Cleaning up IAM service accounts..."
PROJECT_ID=$(gcloud config get-value project)
SA_EMAIL="agentic-devops@${PROJECT_ID}.iam.gserviceaccount.com"
if gcloud iam service-accounts describe $SA_EMAIL &>/dev/null; then
    gcloud iam service-accounts delete $SA_EMAIL --quiet
    echo "   ✅ Deleted service account: $SA_EMAIL"
else
    echo "   ℹ️  Service account already deleted or does not exist"
fi
echo "✅ IAM service accounts cleanup complete"

echo "📋 Cleaning up Terraform state..."
if [ -d "../terraform" ]; then
    cd ../terraform
    terraform destroy -auto-approve
    rm -f terraform.tfstate*
    rm -rf .terraform/
    echo "   ✅ Terraform resources destroyed and state cleaned"
else
    echo "   ℹ️  Terraform directory does not exist"
fi
echo "✅ Terraform cleanup complete"

echo ""
echo "🎯 Teardown Summary"
echo "==================="
echo "✅ All Cloud Functions processed"
echo "✅ All Pub/Sub topics and subscriptions processed"
echo "✅ BigQuery dataset processed"
echo "✅ Cloud Logging sinks processed"
echo "✅ Secret Manager secrets processed"
echo "✅ IAM service accounts processed"
echo "✅ Terraform infrastructure processed"
echo ""
echo "💰 Expected cost impact: ~$0/month (all billable resources removed)"
echo "🔐 Security impact: All API keys and sensitive data removed"
