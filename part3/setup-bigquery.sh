#!/bin/bash

# Create BigQuery Analytics Dataset

echo "Creating BigQuery dataset for analytics..."
# Create dataset for analytics
bq mk --dataset YOUR_PROJECT_ID:agent_analytics

echo "Creating metrics table..."
# Create metrics table
bq mk --table YOUR_PROJECT_ID:agent_analytics.metrics \
  timestamp:TIMESTAMP,service:STRING,log_text:STRING,processing_time:FLOAT,status:STRING,error_type:STRING,ai_provider:STRING,estimated_cost:FLOAT

echo "Verifying table creation..."
bq ls agent_analytics
bq show agent_analytics.metrics

echo "BigQuery analytics dataset created successfully!"
