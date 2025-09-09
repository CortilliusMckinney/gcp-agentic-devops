# CLEANUP.md - Resource Teardown Guide

## Overview

This guide helps you properly clean up all cloud resources created during the Agentic DevOps project to avoid ongoing costs while preserving your technical achievement.

## Quick Start

For complete resource removal:

```bash
cd ~/Documents/GitHub/gcp-agentic-devops/teardown
chmod +x cleanup-resources.sh
./cleanup-resources.sh
```

---

## What Gets Cleaned Up

**Cloud Functions:**

- diagnoser-agent, validator-agent, remediator-agent
- log-analytics-processor
- diagnose-event, validate-fix-event, remediate-event

**Pub/Sub Resources:**

- pipeline-events, validation-requests, remediation-tasks topics
- log-analytics topic and test-analytics-sub subscription

**Data Storage:**

- BigQuery agent_analytics dataset and all tables
- Cloud Logging analytics-sink

**Security Resources:**

- Secret Manager secrets (API keys and tokens)
- IAM service accounts created for the project

**Infrastructure:**

- All Terraform-managed resources
- Terraform state files

---

## Setup Cleanup Scripts

Navigate to teardown directory:

```bash
cd ~/Documents/GitHub/gcp-agentic-devops
mkdir -p teardown
cd teardown
```

### Complete Cleanup Script

Create teardown/cleanup-resources.sh:

```bash
cat > cleanup-resources.sh << 'EOF'
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
EOF
```

### Selective Cleanup Script

Create teardown/selective-cleanup.sh:

```bash
cat > selective-cleanup.sh << 'EOF'
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
EOF
```

### Make Scripts Executable

```bash
chmod +x cleanup-resources.sh
chmod +x selective-cleanup.sh
```

---

## Cost Breakdown

**Monthly costs if left running:**

| Resource | Estimated Cost |
|----------|----------------|
| Cloud Functions | ~$1-3/month (depends on invocations) |
| BigQuery Storage | ~$0.02/GB/month |
| Secret Manager | ~$0.06/secret/month |
| Pub/Sub | Free tier covers demo usage |
| Cloud Logging | Free tier covers demo usage |

**Total estimated monthly cost:** $2-5 depending on usage patterns

---

## Preserving Your Work

Before cleanup, consider exporting key data:

```bash
# Export BigQuery analytics data
bq extract --destination_format=CSV agent_analytics.metrics gs://your-bucket/portfolio-data.csv

# Save function configurations
gcloud functions describe diagnose-event --region=YOUR_REGION > diagnose-event-config.yaml
gcloud functions describe validate-fix-event --region=YOUR_REGION > validate-fix-event-config.yaml

# Backup Terraform state
cp terraform/terraform.tfstate teardown/terraform-backup.tfstate

# Export project configuration for documentation
gcloud projects describe $(gcloud config get-value project) > teardown/project-config.yaml
```

---

## Verification Commands

After cleanup, verify resources are removed:

```bash
# Check for remaining functions
gcloud functions list

# Check for remaining topics
gcloud pubsub topics list

# Check for remaining BigQuery datasets
bq ls

# Check for remaining secrets
gcloud secrets list

# Check for remaining service accounts
gcloud iam service-accounts list
```

Expected result: No resources related to the agentic-devops project should remain.

---

## Troubleshooting

**Permission errors:**

```bash
# Ensure you're authenticated
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

**Resource not found errors:**

- These are normal if resources were already deleted
- The cleanup script continues despite individual resource failures

**Terraform destroy failures:**

```bash
# Force remove Terraform state if destroy fails
cd terraform
rm -rf .terraform/
rm terraform.tfstate*
```

**Billing concerns:**

- Check the GCP billing console to confirm all resources are removed
- Some resources may have a 24-48 hour delay before showing as deleted in billing

---

## What This Demonstrates

Proper resource cleanup showcases:

- Professional cloud cost management skills
- Infrastructure lifecycle management understanding
- Security best practices (removing API keys and sensitive data)
- Production operations experience with teardown procedures

These are valuable skills that employers look for in cloud engineering roles.

---

## After Cleanup

Your agentic DevOps project represents significant technical achievement. Consider:

1. **Portfolio Documentation:** Preserve architecture diagrams and technical decisions
2. **Blog Posts:** Write about lessons learned and technical challenges solved
3. **Resume Updates:** Add quantified achievements from this project
4. **Interview Preparation:** Practice explaining the system's business value and technical architecture

The cleanup process itself demonstrates additional professional competencies beyond the initial technical implementation.