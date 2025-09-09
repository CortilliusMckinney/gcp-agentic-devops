#!/bin/bash

# Test Predictive Insights Pipeline

echo "Generating baseline data..."
# Generate multiple pipeline events to establish patterns
for i in {1..10}; do
  gcloud pubsub topics publish pipeline-events \
    --message="{\"buildStatus\":\"FAILURE\",\"step\":\"test step $i\",\"error\":\"sample error $i\",\"provider\":\"github\",\"timestamp\":\"$(date -u +%Y-%m-%dT%H:%M:%SZ)\"}"
  sleep 10
done

echo "Waiting for data processing (60 seconds)..."
sleep 60

echo "Checking BigQuery data collection..."
# Verify data is flowing to BigQuery
bq query --use_legacy_sql=false \
  'SELECT COUNT(*) as total_metrics, 
   AVG(processing_time) as avg_processing_time,
   COUNT(DISTINCT error_type) as unique_errors
   FROM `YOUR_PROJECT_ID.agent_analytics.metrics`
   WHERE timestamp >= TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 HOUR)'

echo "Monitoring predictive alerts..."
# Check for predictive alerts in function logs
gcloud functions logs read log-analytics-processor --limit=20 | grep "PREDICTIVE_ALERT"

echo "Verifying Datadog integration..."
echo "- Check your updated dashboard for new predictive widgets"
echo "- Look for anomaly score trends"
echo "- Verify that processing time predictions are being calculated"

echo "Predictive insights test completed!"
