#!/bin/bash
# deploy_agents.sh
# Deploy each agent from its correct directory with proper entrypoints

set -e

# Get project info
PROJECT_ID=${GOOGLE_CLOUD_PROJECT:-$(gcloud config get-value project)}
echo "🚀 Deploying Agentic DevOps Pipeline to Project: $PROJECT_ID"

# Check if we're in the right directory structure
if [ ! -d "diagnoser-agent" ] || [ ! -d "validator-agent" ] || [ ! -d "remediator-agent" ]; then
    echo "❌ Agent directories not found. Creating proper structure..."
    mkdir -p diagnoser-agent validator-agent remediator-agent
    
    # Copy files to proper locations
    if [ -f "diagnoser-agent/main.py" ]; then
        echo "✅ diagnoser-agent/main.py already exists"
    else
        echo "⚠️  Please copy your diagnoser main.py to diagnoser-agent/main.py"
    fi
fi

# Deploy Diagnoser Agent
echo ""
echo "📡 Deploying Diagnoser Agent..."
cd part2/functions/diagnoser-agent

# Create requirements.txt if missing
if [ ! -f "requirements.txt" ]; then
    echo "Creating requirements.txt for diagnoser..."
    cat > requirements.txt << EOF
functions-framework==3.*
google-cloud-pubsub==2.*
google-cloud-secret-manager==2.*
openai==1.*
anthropic==0.*
requests==2.*
EOF
fi

gcloud functions deploy diagnoser-agent \
  --gen2 \
  --runtime=python39 \
  --source=. \
  --entry-point=diagnose_event \
  --trigger-topic=pipeline-events \
  --memory=512MB \
  --timeout=300s \
  --set-env-vars="GCP_PROJECT=${PROJECT_ID},VALIDATION_TOPIC=validation-requests" \
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest" \
  --region=YOUR_REGION \
  --allow-unauthenticated

if [ $? -eq 0 ]; then
    echo "✅ Diagnoser Agent deployed successfully"
else
    echo "❌ Diagnoser Agent deployment failed"
    exit 1
fi

cd $(pwd)

# Deploy Validator Agent
echo ""
echo "🔍 Deploying Validator Agent..."
cd part2/functions/validator-agent

# Create requirements.txt if missing
if [ ! -f "requirements.txt" ]; then
    echo "Creating requirements.txt for validator..."
    cat > requirements.txt << EOF
functions-framework==3.*
google-cloud-pubsub==2.*
EOF
fi

gcloud functions deploy validator-agent \
  --gen2 \
  --runtime=python39 \
  --source=. \
  --entry-point=validate_fix_event \
  --trigger-topic=validation-requests \
  --memory=512MB \
  --timeout=300s \
  --set-env-vars="GCP_PROJECT=${PROJECT_ID},APPROVED_KEYWORDS=fix,update,install,upgrade,patch,resolve,npm,REMEDIATION_TOPIC=remediation-tasks" \
  --region=YOUR_REGION \
  --allow-unauthenticated

if [ $? -eq 0 ]; then
    echo "✅ Validator Agent deployed successfully"
else
    echo "❌ Validator Agent deployment failed"
    exit 1
fi

cd $(pwd)

# Deploy Remediator Agent
echo ""
echo "⚙️ Deploying Remediator Agent..."
cd part2/functions/remediator-agent

# Create requirements.txt if missing
if [ ! -f "requirements.txt" ]; then
    echo "Creating requirements.txt for remediator..."
    cat > requirements.txt << EOF
functions-framework==3.*
google-cloud-pubsub==2.*
EOF
fi

gcloud functions deploy remediator-agent \
  --gen2 \
  --runtime=python39 \
  --source=. \
  --entry-point=remediate_event \
  --trigger-topic=remediation-tasks \
  --memory=512MB \
  --timeout=600s \
  --set-env-vars="GCP_PROJECT=${PROJECT_ID}" \
  --region=YOUR_REGION \
  --allow-unauthenticated

if [ $? -eq 0 ]; then
    echo "✅ Remediator Agent deployed successfully"
else
    echo "❌ Remediator Agent deployment failed"
    exit 1
fi

cd $(pwd)

echo ""
echo "🎉 All agents deployed successfully!"
echo ""
echo "📋 Deployment Summary:"
echo "├── diagnoser-agent: diagnose_event (triggered by pipeline-events)"
echo "├── validator-agent: validate_fix_event (triggered by validation-requests)"
echo "└── remediator-agent: remediate_event (triggered by remediation-tasks)"
echo ""
echo "🧪 Test the pipeline:"
echo "gcloud pubsub topics publish pipeline-events --message='{\"buildStatus\":\"FAILURE\",\"step\":\"npm install\",\"error\":\"dependency conflict\",\"provider\":\"github\"}'"
echo ""
echo "🔍 Monitor logs:"
echo "gcloud functions logs read diagnoser-agent --limit=10"
echo "gcloud functions logs read validator-agent --limit=10"
echo "gcloud functions logs read remediator-agent --limit=10"