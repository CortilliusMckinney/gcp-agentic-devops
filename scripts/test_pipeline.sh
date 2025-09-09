#!/bin/bash
# test_pipeline.sh
# Test the end-to-end agentic pipeline

set -e

PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
echo "🧪 Testing Agentic DevOps Pipeline in Project: $PROJECT_ID"

# Function to check if a topic exists
check_topic() {
    local topic_name=$1
    if gcloud pubsub topics describe $topic_name >/dev/null 2>&1; then
        echo "✅ Topic $topic_name exists"
        return 0
    else
        echo "❌ Topic $topic_name missing"
        return 1
    fi
}

# Function to check if a function is deployed
check_function() {
    local func_name=$1
    local expected_entrypoint=$2
    
    if gcloud functions describe $func_name --region=YOUR_REGION >/dev/null 2>&1; then
        echo "✅ Function $func_name is deployed"
        
        # Check entrypoint
        entrypoint=$(gcloud functions describe $func_name --region=YOUR_REGION --format="value(sourceArchiveUrl)" 2>/dev/null || echo "unknown")
        echo "   Entrypoint: $expected_entrypoint"
        return 0
    else
        echo "❌ Function $func_name not found"
        return 1
    fi
}

echo ""
echo "🔍 Pre-flight Checks..."

# Check required topics
echo ""
echo "📡 Checking Pub/Sub Topics:"
topics_ok=true
check_topic "pipeline-events" || topics_ok=false
check_topic "validation-requests" || topics_ok=false
check_topic "remediation-tasks" || topics_ok=false

if [ "$topics_ok" = false ]; then
    echo ""
    echo "⚠️  Creating missing topics..."
    gcloud pubsub topics create pipeline-events || true
    gcloud pubsub topics create validation-requests || true
    gcloud pubsub topics create remediation-tasks || true
    echo "✅ Topics created"
fi

# Check deployed functions
echo ""
echo "⚙️ Checking Cloud Functions:"
functions_ok=true
check_function "diagnoser-agent" "diagnose_event" || functions_ok=false
check_function "validator-agent" "validate_fix_event" || functions_ok=false
check_function "remediator-agent" "remediate_event" || functions_ok=false

if [ "$functions_ok" = false ]; then
    echo ""
    echo "❌ Some functions are missing. Run ./deploy_agents.sh first"
    exit 1
fi

echo ""
echo "🎯 Running Pipeline Test..."

# Test 1: Simple npm dependency failure
echo ""
echo "📤 Test 1: Publishing pipeline failure event..."

TEST_MESSAGE='{
  "buildStatus": "FAILURE",
  "step": "npm install", 
  "error": "ERESOLVE unable to resolve dependency tree - React version conflict",
  "provider": "github",
  "repository": "test-app",
  "buildId": "build-123"
}'

gcloud pubsub topics publish pipeline-events --message="$TEST_MESSAGE"
echo "✅ Test message published to pipeline-events"

# Wait for processing
echo ""
echo "⏱️ Waiting for pipeline processing (30 seconds)..."
sleep 30

# Check logs for each agent
echo ""
echo "📋 Checking Agent Logs..."

echo ""
echo "🔍 Diagnoser Agent Logs (last 5 entries):"
gcloud functions logs read diagnoser-agent --limit=5 --region=YOUR_REGION || echo "No logs yet"

echo ""
echo "🔍 Validator Agent Logs (last 5 entries):"
gcloud functions logs read validator-agent --limit=5 --region=YOUR_REGION || echo "No logs yet"

echo ""
echo "🔍 Remediator Agent Logs (last 5 entries):"
gcloud functions logs read remediator-agent --limit=5 --region=YOUR_REGION || echo "No logs yet"

echo ""
echo "🧪 Test 2: Manual verification commands..."
echo ""
echo "To check message flow, run these commands:"
echo ""
echo "# Check if validation-requests received messages:"
echo "gcloud pubsub subscriptions pull validation-requests-sub --limit=1 --auto-ack"
echo ""
echo "# Check if remediation-tasks received messages:"  
echo "gcloud pubsub subscriptions pull remediation-tasks-sub --limit=1 --auto-ack"
echo ""
echo "# View detailed function logs:"
echo "gcloud functions logs read diagnoser-agent --limit=20"
echo "gcloud functions logs read validator-agent --limit=20"
echo "gcloud functions logs read remediator-agent --limit=20"

echo ""
echo "✅ Pipeline test completed!"
echo ""
echo "📊 Expected Flow:"
echo "1. pipeline-events → diagnoser-agent → validation-requests"
echo "2. validation-requests → validator-agent → remediation-tasks" 
echo "3. remediation-tasks → remediator-agent → execution"
echo ""
echo "🔍 Check the logs above to verify each step worked correctly."