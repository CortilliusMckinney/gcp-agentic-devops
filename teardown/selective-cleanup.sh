#!/bin/bash

echo "🎯 Selective Resource Cleanup"
echo "Choose what to keep for portfolio demonstrations"
echo ""

# Check for placeholders and prompt for values
if grep -q "YOUR_PROJECT_ID" "$0"; then
    echo "⚠️  Configuration required before running cleanup"
    echo ""
    
    # Get project ID
    echo "Enter your GCP project ID:"
    read -p "Project ID: " USER_PROJECT_ID
    if [ -z "$USER_PROJECT_ID" ]; then
        echo "❌ Project ID is required. Exiting."
        exit 1
    fi
    # Replace placeholder in this script
    sed -i.bak "s/YOUR_PROJECT_ID/$USER_PROJECT_ID/g" "$0"
    echo "✅ Project ID updated to: $USER_PROJECT_ID"
    
    # Clean up backup file
    rm -f "$0.bak"
    
    echo ""
    echo "Configuration complete. Continuing with selective cleanup..."
    echo ""
fi

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
    function_count=0
    while IFS= read -r line; do
        if [ -n "$line" ]; then
            name=$(echo $line | cut -d' ' -f1)
            region=$(echo $line | cut -d' ' -f2)
            gcloud functions delete $name --region=$region --quiet
            echo "   ✅ Deleted function: $name (region: $region)"
            ((function_count++))
        fi
    done < <(gcloud functions list --format="value(name,region)" 2>/dev/null)
    
    if [ $function_count -eq 0 ]; then
        echo "   ℹ️  No Cloud Functions found or all already deleted"
    fi
    echo "✅ Cloud Functions cleanup complete"
fi

if [ "$delete_bigquery" = "y" ]; then
    echo "Deleting BigQuery dataset..."
    if bq ls -d YOUR_PROJECT_ID:agent_analytics &>/dev/null; then
        bq rm -r -f YOUR_PROJECT_ID:agent_analytics
        echo "   ✅ Deleted BigQuery dataset: agent_analytics"
    else
        echo "   ℹ️  BigQuery dataset agent_analytics already deleted or does not exist"
    fi
    echo "✅ BigQuery cleanup complete"
fi

if [ "$delete_secrets" = "y" ]; then
    echo "Deleting secrets..."
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
fi

echo ""
echo "🎯 Selective cleanup complete"
echo "Remaining resources can be used for portfolio demonstrations"
