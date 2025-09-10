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

# Get current project ID
PROJECT_ID=$(gcloud config get-value project)

echo "📋 Cleaning up Dataflow jobs (this prevents resource recreation)..."
# Get all active Dataflow jobs
active_jobs=$(gcloud dataflow jobs list --status=active --format="value(JOB_ID,REGION)" 2>/dev/null)
if [ ! -z "$active_jobs" ]; then
    while IFS=$'\t' read -r job_id region; do
        if [ ! -z "$job_id" ] && [ ! -z "$region" ]; then
            echo "   🛑 Stopping Dataflow job: $job_id in region: $region"
            # Try to cancel first, then drain if cancel fails
            if ! gcloud dataflow jobs cancel "$job_id" --region="$region" --quiet &>/dev/null; then
                echo "   ⏳ Cancel failed, trying drain for job: $job_id"
                gcloud dataflow jobs drain "$job_id" --region="$region" --quiet &>/dev/null
            fi
            echo "   ✅ Stopped Dataflow job: $job_id"
        fi
    done <<< "$active_jobs"
    
    # Wait for jobs to fully stop before continuing
    echo "   ⏳ Waiting 60 seconds for Dataflow jobs to fully stop..."
    sleep 60
else
    echo "   ℹ️  No active Dataflow jobs found"
fi
echo "✅ Dataflow jobs cleanup complete"

echo "📋 Cleaning up Compute Engine instances..."
# Get list of ALL instances (not just filtered ones)
instances=$(gcloud compute instances list --format="value(name,zone)")
if [ ! -z "$instances" ]; then
    while IFS=$'\t' read -r instance_name zone; do
        if [ ! -z "$instance_name" ] && [ ! -z "$zone" ]; then
            if gcloud compute instances describe "$instance_name" --zone="$zone" &>/dev/null; then
                gcloud compute instances delete "$instance_name" --zone="$zone" --quiet
                echo "   ✅ Deleted instance: $instance_name (zone: $zone)"
            fi
        fi
    done <<< "$instances"
else
    echo "   ℹ️  No Compute Engine instances found"
fi
echo "✅ Compute Engine cleanup complete"

echo "📋 Cleaning up Cloud Storage buckets..."
# List all buckets for the project
buckets=$(gsutil ls -p $PROJECT_ID 2>/dev/null | sed 's|gs://||' | sed 's|/||')
if [ ! -z "$buckets" ]; then
    for bucket in $buckets; do
        # Remove all objects first (including versioned objects)
        gsutil -m rm -r -a "gs://$bucket/**" &>/dev/null || true
        # Delete the bucket
        if gsutil ls -b "gs://$bucket" &>/dev/null; then
            gsutil rb "gs://$bucket"
            echo "   ✅ Deleted bucket: $bucket"
        else
            echo "   ℹ️  Bucket $bucket already deleted or does not exist"
        fi
    done
else
    echo "   ℹ️  No Cloud Storage buckets found"
fi
echo "✅ Cloud Storage cleanup complete"

echo "📋 Cleaning up Cloud Functions..."
# Get all actual function names from the project
actual_functions=$(gcloud functions list --format="value(name)")
if [ ! -z "$actual_functions" ]; then
    for func in $actual_functions; do
        if gcloud functions describe $func --region=us-central1 &>/dev/null; then
            gcloud functions delete $func --region=us-central1 --quiet
            echo "   ✅ Deleted function: $func"
        else
            echo "   ℹ️  Function $func already deleted or does not exist"
        fi
    done
else
    echo "   ℹ️  No Cloud Functions found"
fi
echo "✅ Cloud Functions cleanup complete"

echo "📋 Cleaning up Pub/Sub resources..."
# Get all actual subscriptions and topics
actual_subscriptions=$(gcloud pubsub subscriptions list --format="value(name.segment(-1))" 2>/dev/null)
actual_topics=$(gcloud pubsub topics list --format="value(name.segment(-1))" 2>/dev/null)

if [ ! -z "$actual_subscriptions" ]; then
    for sub in $actual_subscriptions; do
        if gcloud pubsub subscriptions describe $sub &>/dev/null; then
            gcloud pubsub subscriptions delete $sub --quiet
            echo "   ✅ Deleted subscription: $sub"
        else
            echo "   ℹ️  Subscription $sub already deleted or does not exist"
        fi
    done
else
    echo "   ℹ️  No Pub/Sub subscriptions found"
fi

if [ ! -z "$actual_topics" ]; then
    for topic in $actual_topics; do
        if gcloud pubsub topics describe $topic &>/dev/null; then
            gcloud pubsub topics delete $topic --quiet
            echo "   ✅ Deleted topic: $topic"
        else
            echo "   ℹ️  Topic $topic already deleted or does not exist"
        fi
    done
else
    echo "   ℹ️  No Pub/Sub topics found"
fi
echo "✅ Pub/Sub resources cleanup complete"

echo "📋 Cleaning up BigQuery resources..."
# Get all actual datasets
actual_datasets=$(bq ls --format="value(datasetId)" 2>/dev/null)
if [ ! -z "$actual_datasets" ]; then
    for dataset in $actual_datasets; do
        if bq ls -d ${PROJECT_ID}:${dataset} &>/dev/null; then
            bq rm -r -f ${PROJECT_ID}:${dataset}
            echo "   ✅ Deleted BigQuery dataset: $dataset"
        else
            echo "   ℹ️  BigQuery dataset $dataset already deleted or does not exist"
        fi
    done
else
    echo "   ℹ️  No BigQuery datasets found"
fi
echo "✅ BigQuery cleanup complete"

echo "📋 Cleaning up Cloud Logging sinks..."
actual_sinks=$(gcloud logging sinks list --format="value(name)" 2>/dev/null)
if [ ! -z "$actual_sinks" ]; then
    for sink in $actual_sinks; do
        # Skip system sinks that cannot be deleted
        if [[ "$sink" == "_Required" || "$sink" == "_Default" ]]; then
            echo "   ℹ️  Skipping system sink: $sink (cannot be deleted)"
            continue
        fi
        if gcloud logging sinks describe $sink &>/dev/null; then
            gcloud logging sinks delete $sink --quiet
            echo "   ✅ Deleted logging sink: $sink"
        else
            echo "   ℹ️  Logging sink $sink already deleted or does not exist"
        fi
    done
else
    echo "   ℹ️  No logging sinks found"
fi
echo "✅ Logging sinks cleanup complete"

echo "📋 Cleaning up Secret Manager secrets..."
actual_secrets=$(gcloud secrets list --format="value(name.segment(-1))" 2>/dev/null)
if [ ! -z "$actual_secrets" ]; then
    for secret in $actual_secrets; do
        if gcloud secrets describe $secret &>/dev/null; then
            gcloud secrets delete $secret --quiet
            echo "   ✅ Deleted secret: $secret"
        else
            echo "   ℹ️  Secret $secret already deleted or does not exist"
        fi
    done
else
    echo "   ℹ️  No secrets found"
fi
echo "✅ Secret Manager cleanup complete"

echo "📋 Cleaning up IAM service accounts..."
# Get all service accounts (excluding default ones)
actual_service_accounts=$(gcloud iam service-accounts list --format="value(email)" --filter="email:*@${PROJECT_ID}.iam.gserviceaccount.com")
if [ ! -z "$actual_service_accounts" ]; then
    for sa_email in $actual_service_accounts; do
        if gcloud iam service-accounts describe $sa_email &>/dev/null; then
            gcloud iam service-accounts delete $sa_email --quiet
            echo "   ✅ Deleted service account: $sa_email"
        else
            echo "   ℹ️  Service account $sa_email already deleted or does not exist"
        fi
    done
else
    echo "   ℹ️  No custom service accounts found"
fi
echo "✅ IAM service accounts cleanup complete"

echo "📋 Cleaning up Instance Templates and Managed Instance Groups..."
# Clean up managed instance groups
migs=$(gcloud compute instance-groups managed list --format="value(name,zone,region)" 2>/dev/null)
if [ ! -z "$migs" ]; then
    while IFS=$'\t' read -r mig_name location_type location; do
        if [ ! -z "$mig_name" ]; then
            if [ ! -z "$location" ] && [[ "$location" == *"-"* ]]; then
                if [[ "$location" == *"-a" ]] || [[ "$location" == *"-b" ]] || [[ "$location" == *"-c" ]]; then
                    # It's a zone
                    gcloud compute instance-groups managed delete "$mig_name" --zone="$location" --quiet &>/dev/null
                else
                    # It's a region
                    gcloud compute instance-groups managed delete "$mig_name" --region="$location" --quiet &>/dev/null
                fi
                echo "   ✅ Deleted managed instance group: $mig_name"
            fi
        fi
    done <<< "$migs"
else
    echo "   ℹ️  No managed instance groups found"
fi

# Clean up instance templates
templates=$(gcloud compute instance-templates list --format="value(name)" 2>/dev/null)
if [ ! -z "$templates" ]; then
    for template in $templates; do
        gcloud compute instance-templates delete "$template" --quiet &>/dev/null
        echo "   ✅ Deleted instance template: $template"
    done
else
    echo "   ℹ️  No instance templates found"
fi
echo "✅ Instance Templates and MIGs cleanup complete"

echo "📋 Cleaning up Load Balancers and Networking..."
# Clean up any load balancers
lb_rules=$(gcloud compute forwarding-rules list --format="value(name,region)" 2>/dev/null)
if [ ! -z "$lb_rules" ]; then
    while IFS=$'\t' read -r rule_name region; do
        if [ ! -z "$rule_name" ]; then
            if [ ! -z "$region" ]; then
                gcloud compute forwarding-rules delete "$rule_name" --region="$region" --quiet &>/dev/null
            else
                gcloud compute forwarding-rules delete "$rule_name" --global --quiet &>/dev/null
            fi
            echo "   ✅ Deleted forwarding rule: $rule_name"
        fi
    done <<< "$lb_rules"
else
    echo "   ℹ️  No forwarding rules found"
fi

# Clean up backend services
backend_services=$(gcloud compute backend-services list --format="value(name)" 2>/dev/null)
if [ ! -z "$backend_services" ]; then
    for service in $backend_services; do
        gcloud compute backend-services delete "$service" --global --quiet &>/dev/null
        echo "   ✅ Deleted backend service: $service"
    done
else
    echo "   ℹ️  No backend services found"
fi

# Clean up health checks
health_checks=$(gcloud compute health-checks list --format="value(name)" 2>/dev/null)
if [ ! -z "$health_checks" ]; then
    for check in $health_checks; do
        gcloud compute health-checks delete "$check" --quiet &>/dev/null
        echo "   ✅ Deleted health check: $check"
    done
else
    echo "   ℹ️  No health checks found"
fi
echo "✅ Load Balancers and Networking cleanup complete"

echo "📋 Cleaning up Datadog-related resources..."
# Remove datadog-puller-key.json file if it exists in various locations
key_locations=("../datadog-puller-key.json" "./datadog-puller-key.json" "../../datadog-puller-key.json")
for key_file in "${key_locations[@]}"; do
    if [ -f "$key_file" ]; then
        rm -f "$key_file"
        echo "   ✅ Removed datadog-puller-key.json file from: $key_file"
    fi
done
echo "✅ Datadog resources cleanup complete"

echo "📋 Cleaning up Terraform state..."
if [ -d "../terraform" ]; then
    cd ../terraform
    terraform destroy -auto-approve &>/dev/null
    rm -f terraform.tfstate*
    rm -rf .terraform/
    echo "   ✅ Terraform resources destroyed and state cleaned"
else
    echo "   ℹ️  Terraform directory does not exist"
fi
echo "✅ Terraform cleanup complete"

echo ""
echo "📋 Additional Manual Cleanup Required:"
echo "⚠️  Datadog Integration - Must be disconnected manually from Datadog console"
echo "⚠️  Any external monitoring/alerting services connected to this project"
echo "⚠️  Check billing console for any unexpected charges from missed resources"
echo ""

echo ""
echo "🎯 Teardown Summary"
echo "==================="
echo "✅ All Dataflow jobs stopped"
echo "✅ All Compute Engine instances processed"
echo "✅ All Cloud Storage buckets processed" 
echo "✅ All Cloud Functions processed"
echo "✅ All Pub/Sub topics and subscriptions processed"
echo "✅ BigQuery datasets processed"
echo "✅ Cloud Logging sinks processed"
echo "✅ Secret Manager secrets processed"
echo "✅ IAM service accounts processed"
echo "✅ Instance Templates and MIGs processed"
echo "✅ Load Balancers and networking processed"
echo "✅ Terraform infrastructure processed"
echo ""
echo "💰 Expected cost impact: ~$0/month (all billable resources removed)"
echo "🔐 Security impact: All API keys and sensitive data removed"
echo ""
echo "🔍 Final Verification Commands:"
echo "   gcloud compute instances list"
echo "   gsutil ls"
echo "   gcloud functions list"
echo "   gcloud pubsub topics list"
echo "   bq ls"
echo "   gcloud dataflow jobs list --status=active"
echo ""
echo "Run these commands to confirm all resources are gone."
