#!/bin/bash

echo "🎯 Selective Resource Cleanup"
echo "Choose what to keep for portfolio demonstrations"
echo ""

echo "Resources that incur ongoing costs:"
echo "1. Cloud Functions (minimal cost, ~$0.01/day)"
echo "2. BigQuery storage (minimal cost, ~$0.02/month)" 
echo "3. Secret Manager secrets (minimal cost, ~$0.06/month)"
echo ""

echo "Resources that are free:"
echo "- Pub/Sub topics (free tier: 10GB/month)"
echo "- Cloud Logging (free tier: 50GB/month)"
echo "- IAM service accounts (free)"
echo ""

read -p "Delete Cloud Functions to stop compute costs? (y/n): " delete_functions
read -p "Delete BigQuery data to stop storage costs? (y/n): " delete_bigquery
read -p "Delete Secret Manager secrets? (y/n): " delete_secrets

if [ "$delete_functions" = "y" ]; then
    echo "Deleting Cloud Functions..."
    gcloud functions list --format="value(name,region)" | while read name region; do
        gcloud functions delete $name --region=$region --quiet
    done
    echo "✅ Cloud Functions deleted"
fi

if [ "$delete_bigquery" = "y" ]; then
    echo "Deleting BigQuery dataset..."
    bq rm -r -f YOUR_PROJECT_ID:agent_analytics
    echo "✅ BigQuery dataset deleted"
fi

if [ "$delete_secrets" = "y" ]; then
    echo "Deleting secrets..."
    gcloud secrets delete openai-api-key --quiet
    gcloud secrets delete anthropic-api-key --quiet  
    gcloud secrets delete cloudflare-api-token --quiet
    gcloud secrets delete cloudflare-account-id --quiet
    echo "✅ Secrets deleted"
fi

echo ""
echo "🎯 Selective cleanup complete"
echo "Remaining resources can be used for portfolio demonstrations"
