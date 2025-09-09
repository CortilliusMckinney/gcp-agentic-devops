import functions_framework
import json
import pandas as pd
from google.cloud import bigquery
from google.cloud import logging
import base64
from datetime import datetime, timedelta
import re

@functions_framework.cloud_event
def process_log_analytics(cloud_event):
    """
    Process incoming logs and extract metrics for predictive analysis
    """
    try:
        # Decode Pub/Sub message
        message_data = base64.b64decode(cloud_event.data["message"]["data"])
        log_entry = json.loads(message_data)
        
        print(f"Processing log entry: {json.dumps(log_entry, indent=2)[:500]}")
        
        # Extract key metrics from log entry
        metrics = extract_agent_metrics(log_entry)
        
        if metrics:
            print(f"Extracted metrics: {metrics}")
            # Store in BigQuery for ML analysis
            store_metrics_bigquery(metrics)
            
            # Check for anomaly indicators
            anomaly_score = calculate_anomaly_score(metrics)
            
            if anomaly_score > 0.7:  # High anomaly threshold
                send_predictive_alert(metrics, anomaly_score)
        else:
            print("No metrics extracted from log entry")
            
    except Exception as e:
        print(f"Error processing log analytics: {str(e)}")
        import traceback
        traceback.print_exc()

def extract_agent_metrics(log_entry):
    """
    Extract actionable metrics from agent logs
    """
    try:
        log_text = log_entry.get('textPayload', '')
        timestamp = log_entry.get('timestamp')
        service = log_entry.get('resource', {}).get('labels', {}).get('function_name', 'unknown')
        
        # Only process our agent functions
        if not any(name in service for name in ['diagnose-event', 'validate-fix-event', 'remediate']):
            return None
        
        metrics = {
            'timestamp': timestamp,
            'service': service,
            'log_text': log_text
        }
        
        # Extract processing times
        time_match = re.search(r'took (\d+\.?\d*)s', log_text)
        if time_match:
            metrics['processing_time'] = float(time_match.group(1))
        
        # Extract success/failure indicators
        if 'SUCCESS' in log_text.upper() or 'completed' in log_text.lower() or 'Published' in log_text:
            metrics['status'] = 'success'
        elif 'ERROR' in log_text.upper() or 'failed' in log_text.lower() or 'Rejected' in log_text:
            metrics['status'] = 'error'
            metrics['error_type'] = extract_error_type(log_text)
        else:
            metrics['status'] = 'processing'
        
        # Extract AI model usage
        if 'openai' in log_text.lower():
            metrics['ai_provider'] = 'openai'
        elif 'anthropic' in log_text.lower():
            metrics['ai_provider'] = 'anthropic'
        elif 'cloudflare' in log_text.lower():
            metrics['ai_provider'] = 'cloudflare'
        
        # Extract cost indicators
        cost_match = re.search(r'cost.*?(\d+\.?\d*)', log_text.lower())
        if cost_match:
            metrics['estimated_cost'] = float(cost_match.group(1))
        
        return metrics
        
    except Exception as e:
        print(f"Error extracting metrics: {str(e)}")
        return None

def extract_error_type(log_text):
    """
    Classify error types for pattern analysis
    """
    error_patterns = {
        'timeout': ['timeout', 'timed out', 'deadline exceeded'],
        'api_limit': ['rate limit', 'quota exceeded', '429'],
        'dependency': ['dependency', 'package', 'module not found'],
        'network': ['connection', 'network', 'dns'],
        'auth': ['authentication', 'unauthorized', '401', '403'],
        'resource': ['memory', 'cpu', 'disk space', 'resource'],
        'validation': ['rejected', 'validation', 'unknown command']
    }
    
    log_lower = log_text.lower()
    for error_type, patterns in error_patterns.items():
        if any(pattern in log_lower for pattern in patterns):
            return error_type
    
    return 'unknown'

def store_metrics_bigquery(metrics):
    """
    Store metrics in BigQuery for ML analysis
    """
    try:
        client = bigquery.Client()
        table_id = "YOUR_PROJECT_ID.agent_analytics.metrics"
        
        # Insert row
        errors = client.insert_rows_json(table_id, [metrics])
        if errors:
            print(f"Failed to insert metrics: {errors}")
        else:
            print(f"Successfully stored metrics for {metrics['service']}")
    except Exception as e:
        print(f"Error storing metrics in BigQuery: {str(e)}")

def calculate_anomaly_score(metrics):
    """
    Calculate basic anomaly score based on current patterns
    """
    score = 0.0
    
    # Processing time anomalies
    if metrics.get('processing_time', 0) > 30:  # > 30 seconds
        score += 0.3
    
    # Error clustering
    if metrics.get('status') == 'error':
        score += 0.4
    
    # Cost anomalies
    if metrics.get('estimated_cost', 0) > 0.05:  # > $0.05 per request
        score += 0.2
    
    # Time-based patterns (e.g., issues tend to cluster)
    current_hour = datetime.now().hour
    if current_hour in [2, 3, 4]:  # Early morning deployments often problematic
        score += 0.1
    
    return min(score, 1.0)

def send_predictive_alert(metrics, anomaly_score):
    """
    Send proactive alert for predicted issues
    """
    alert_message = {
        'type': 'PREDICTIVE_ALERT',
        'anomaly_score': anomaly_score,
        'service': metrics['service'],
        'indicators': {
            'processing_time': metrics.get('processing_time'),
            'status': metrics.get('status'),
            'error_type': metrics.get('error_type')
        },
        'prediction': f"High likelihood of {metrics['service']} issues based on recent patterns",
        'timestamp': datetime.utcnow().isoformat()
    }
    
    print(f"PREDICTIVE ALERT: {json.dumps(alert_message)}")
