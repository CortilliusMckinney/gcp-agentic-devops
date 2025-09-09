import base64
import json
import os
import time
import uuid

import functions_framework
from google.cloud import pubsub_v1


def _decode_pubsub_message(cloud_event):
    """Decode Pub/Sub message from cloud event."""
    data = cloud_event.data or {}
    message = data.get("message", {})
    if "data" in message:
        try:
            decoded = base64.b64decode(message["data"]).decode("utf-8")
            return json.loads(decoded)
        except Exception:
            # fall back to raw string if not JSON
            return {"raw": message.get("data")}
    # sometimes tests send structured payload directly
    return message or data


def _parse_approved_keywords():
    """
    Parse APPROVED_KEYWORDS with multiple fallback strategies.
    Prevents the parsing errors that crash the validator.
    """
    raw_value = os.getenv("APPROVED_KEYWORDS", "")
    
    if not raw_value:
        # Default safe keywords
        default_keywords = ["fix", "update", "install", "upgrade", "patch", "resolve", "npm"]
        print(f"[Validator] Using default approved keywords: {default_keywords}")
        return default_keywords
    
    # Try multiple parsing strategies
    try:
        # Strategy 1: Comma-separated
        if "," in raw_value:
            keywords = [k.strip().lower() for k in raw_value.split(",") if k.strip()]
            if keywords:
                print(f"[Validator] Parsed {len(keywords)} approved keywords from comma-separated")
                return keywords
        
        # Strategy 2: Space-separated  
        if " " in raw_value:
            keywords = [k.strip().lower() for k in raw_value.split() if k.strip()]
            if keywords:
                print(f"[Validator] Parsed {len(keywords)} approved keywords from space-separated")
                return keywords
        
        # Strategy 3: Single keyword
        single_keyword = raw_value.strip().lower()
        if single_keyword:
            print(f"[Validator] Using single approved keyword: {single_keyword}")
            return [single_keyword]
            
    except Exception as e:
        print(f"[Validator] Failed to parse APPROVED_KEYWORDS '{raw_value}': {e}")
    
    # Fallback to safe defaults
    default_keywords = ["fix", "update", "install", "upgrade", "patch", "resolve", "npm"]
    print(f"[Validator] Using fallback approved keywords: {default_keywords}")
    return default_keywords


def _resolve_remediation_topic():
    """
    Resolve remediation topic from environment variables.
    Falls back to project/topic path if needed.
    """
    env_val = os.getenv("REMEDIATION_TOPIC", "").strip()
    if env_val.startswith("projects/") and "/topics/" in env_val:
        return env_val

    topic_id = env_val or "remediation-tasks"
    project = (
        os.getenv("GCP_PROJECT")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCLOUD_PROJECT")
    )
    if not project:
        raise RuntimeError("Missing GOOGLE_CLOUD_PROJECT/GCP_PROJECT")
    return f"projects/{project}/topics/{topic_id}"


@functions_framework.cloud_event
def validate_fix_event(cloud_event):
    """
    Pub/Sub-triggered function:
      - Receives diagnosis from diagnoser agent
      - Validates command against approved keywords
      - Publishes approved fixes to remediation topic
    """
    print("[Validator] Processing validation request")
    
    # Decode diagnosis event
    diagnosis = _decode_pubsub_message(cloud_event)
    print(f"[Validator] Received diagnosis: {diagnosis}")

    # Get approved keywords
    approved_keywords = _parse_approved_keywords()
    
    # Extract command and metadata
    command = diagnosis.get("command", "").lower()
    fix_type = diagnosis.get("fix_type", "unknown")
    risk = diagnosis.get("risk", "high")
    confidence = diagnosis.get("confidence", 0.3)
    
    # Validation logic
    approved = False
    reason = "Unknown command"
    
    # Check if command contains approved keywords
    for keyword in approved_keywords:
        if keyword in command:
            approved = True
            reason = f"Contains approved keyword: {keyword}"
            break
    
    # Additional validation rules
    if not approved and "npm install" in command:
        approved = True
        reason = "Standard npm install command"
    elif not approved and risk == "low":
        approved = True
        reason = "Low risk operation"
    elif "rm -rf" in command or "sudo" in command or "delete" in command:
        approved = False
        reason = "Dangerous command detected"
    
    # Create validation result
    validation_result = {
        "id": f"rem-{int(time.time())}-{uuid.uuid4().hex[:8]}",
        "original_diagnosis_id": diagnosis.get("id", "unknown"),
        "command": diagnosis.get("command", "echo 'no command'"),
        "fix_type": fix_type,
        "risk": risk,
        "confidence": confidence,
        "approved": approved,
        "reason": reason,
        "metadata": diagnosis.get("metadata", {}),
        "validation_timestamp": time.time()
    }
    
    print(f"[Validator] Validation result: {validation_result}")
    
    if approved:
        # Publish to remediation topic
        try:
            topic_path = _resolve_remediation_topic()
            publisher = pubsub_v1.PublisherClient()
            publisher.publish(topic_path, json.dumps(validation_result).encode("utf-8"))
            print(f"[Validator] ✅ Published approved fix to remediation: {validation_result['command']}")
            return {"status": "approved", "published": True}
        except Exception as e:
            print(f"[Validator] ❌ Failed to publish to remediation: {e}")
            return {"status": "approved", "published": False, "error": str(e)}
    else:
        print(f"[Validator] ❌ Rejected fix: {reason}")
        return {"status": "rejected", "reason": reason}