# CLEANUP.md - Resource Teardown Guide

## Overview

This guide helps you properly clean up all cloud resources created during the Agentic DevOps project to avoid ongoing costs while preserving your technical achievement.

## Quick Start

The cleanup scripts are intelligent and user-friendly - they'll automatically prompt for any required configuration:

```bash
cd teardown
chmod +x cleanup-resources.sh
./cleanup-resources.sh
```

---

## Smart Cleanup Scripts

### Automatic Configuration

Both cleanup scripts are enhanced with automatic configuration detection:

- **First run**: Scripts detect placeholder values and prompt you for your actual GCP region and project ID
- **Subsequent runs**: Scripts remember your configuration and run without prompting
- **Clear feedback**: Scripts show exactly what's being deleted vs. what's already gone

### Intelligent Error Handling

Instead of confusing error messages, you'll see clean status updates:

- ✅ "Deleted resource: [name]" - Successfully removed
- ℹ️ "Resource already deleted or does not exist" - Nothing to do
- Clear section-by-section progress with organized output

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

## Cleanup Options

### Option 1: Complete Cleanup (Recommended)

Removes all resources to eliminate ongoing costs:

```bash
cd teardown
chmod +x cleanup-resources.sh
./cleanup-resources.sh
```

**First run example:**
```
🧹 Agentic DevOps System Teardown
⚠️  Configuration required before running cleanup

Enter your GCP region (e.g., us-central1, europe-west1):
Region: us-central1
✅ Region updated to: us-central1

Enter your GCP project ID:
Project ID: my-project-123
✅ Project ID updated to: my-project-123

Configuration complete. Continuing with cleanup...
```

### Option 2: Selective Cleanup

Keep some resources for portfolio demonstrations:

```bash
cd teardown
chmod +x selective-cleanup.sh
./selective-cleanup.sh
```

Choose which resource types to delete while preserving others for demos.

---

## Expected Output

With the enhanced scripts, you'll see organized, clear output:

```
📋 Cleaning up Cloud Functions...
   ✅ Deleted function: diagnose-event
   ✅ Deleted function: log-analytics-processor
   ℹ️  Function validator-agent already deleted or does not exist
✅ Cloud Functions cleanup complete

📋 Cleaning up Pub/Sub resources...
   ℹ️  Topic pipeline-events already deleted or does not exist
   ℹ️  Topic log-analytics already deleted or does not exist
✅ Pub/Sub resources cleanup complete
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
gcloud functions describe diagnose-event --region=us-central1 > diagnose-event-config.yaml
gcloud functions describe validate-fix-event --region=us-central1 > validate-fix-event-config.yaml

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

**Script doesn't prompt for configuration:**
- The scripts automatically detect if configuration is needed
- If placeholders were already replaced, no prompting occurs
- To reconfigure, manually edit the script files to restore placeholder values

**Multiple cleanup runs:**
- It's safe to run cleanup scripts multiple times
- Scripts intelligently handle already-deleted resources
- No errors or confusion from repeated runs

---

## What This Demonstrates

Proper resource cleanup showcases:
- Professional cloud cost management skills
- Infrastructure lifecycle management understanding
- Security best practices (removing API keys and sensitive data)
- Production operations experience with teardown procedures
- User-friendly automation and error handling

These are valuable skills that employers look for in cloud engineering roles.

---

## After Cleanup

Your agentic DevOps project represents significant technical achievement. Consider:

1. **Portfolio Documentation:** Preserve architecture diagrams and technical decisions
2. **Blog Posts:** Write about lessons learned and technical challenges solved
3. **Resume Updates:** Add quantified achievements from this project
4. **Interview Preparation:** Practice explaining the system's business value and technical architecture

The cleanup process itself demonstrates additional professional competencies beyond the initial technical implementation.
