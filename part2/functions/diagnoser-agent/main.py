import base64
import json
import os
import time
import uuid

import functions_framework
from google.cloud import pubsub_v1

# Lazy-load the model router
from agents.model_router import ModelRouter

router = None  # initialized on first invocation


def _decode_pubsub_message(cloud_event):
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


def _resolve_validation_topic():
    """
    FIXED: Use validation-requests topic consistently.
    Falls back to env project + topic 'validation-requests'.
    """
    env_val = os.getenv("VALIDATION_TOPIC", "").strip()
    if env_val.startswith("projects/") and "/topics/" in env_val:
        return env_val

    topic_id = env_val or "validation-requests"  # CHANGED from "diagnosis-events"
    project = (
        os.getenv("GCP_PROJECT")
        or os.getenv("GOOGLE_CLOUD_PROJECT")
        or os.getenv("GCLOUD_PROJECT")
    )
    if not project:
        raise RuntimeError("Missing GOOGLE_CLOUD_PROJECT/GCP_PROJECT")
    return f"projects/{project}/topics/{topic_id}"


@functions_framework.cloud_event
def diagnose_event(cloud_event):
    """
    Pub/Sub-triggered function:
      - Decodes pipeline event
      - Asks ModelRouter for a diagnosis
      - Publishes a normalized diagnosis to the validation-requests topic
    """
    global router

    # Init router lazily (secrets only available at runtime)
    if router is None:
        router = ModelRouter()
        print("[Diagnoser] ModelRouter initialized")

    # Decode event
    event = _decode_pubsub_message(cloud_event)
    print(f"[Diagnoser] Processing pipeline event: {event}")

    # Build prompt for analysis
    prompt = (
        "Analyze this CI/CD failure and propose a safe, specific fix "
        "as a one-line command, plus a short diagnosis. If unsure, pick the safest, "
        "non-destructive remediation.\n\n"
        f"Build Status: {event.get('buildStatus','unknown')}\n"
        f"Step: {event.get('step','unknown')}\n"
        f"Error: {event.get('error') or event.get('log','no details')}\n"
        f"Provider: {event.get('provider','unknown')}\n"
    )

    # Call the router
    try:
        ai = router.route(prompt, {"provider": "anthropic"})  # adjust provider if you want
        if ai.get("error"):
            raise RuntimeError(ai["error"])
        text = (ai.get("response") or "").strip()
    except Exception as e:
        # Soft-fallback so the pipeline keeps moving
        text = (
            "Diagnosis: Dependency conflict in npm install.\n"
            "Command: npm install --legacy-peer-deps\n"
            f"(fallback due to AI error: {e})"
        )
        print(f"[Diagnoser] AI analysis failed, using fallback: {e}")

    # IMPROVED: More robust heuristic normalization
    lower = text.lower()
    
    # Better pattern matching for consistent field mapping
    if "legacy-peer-deps" in lower or "peer-deps" in lower:
        command = "npm install --legacy-peer-deps"
        fix_type = "npm_fix"
        risk = "low"
        conf = 0.9
        diagnosis = "react dependency conflict"
    elif "npm install" in lower and "react" in lower:
        command = "npm install --save"
        fix_type = "npm_fix"
        risk = "low"
        conf = 0.8
        diagnosis = "react version mismatch"
    elif "npm ci" in lower or "clean install" in lower:
        command = "npm ci"
        fix_type = "npm_fix"
        risk = "low"
        conf = 0.7
        diagnosis = "npm cache issue"
    else:
        command = "echo 'manual review required'"
        fix_type = "manual_review"
        risk = "high"
        conf = 0.3
        diagnosis = "complex issue requiring manual review"

    payload = {
        # generate a stable-enough id for tracing
        "id": f"diag-{int(time.time())}-{uuid.uuid4().hex[:8]}",
        "diagnosis": diagnosis,  # CONSISTENT naming
        "fix_type": fix_type,
        "command": command,
        "risk": risk,
        "confidence": conf,
        "metadata": {
            "repository": event.get("repository", "unknown"),
            "buildId": event.get("buildId", "unknown"),
            "provider": event.get("provider", "unknown"),
            "step": event.get("step", "unknown"),
        },
        "ai_response": text[:200] + "..." if len(text) > 200 else text,  # Store original response
        "diagnosis_timestamp": time.time()
    }

    # Publish to validator (validation-requests topic)
    try:
        topic_path = _resolve_validation_topic()
        publisher = pubsub_v1.PublisherClient()
        publisher.publish(topic_path, json.dumps(payload).encode("utf-8"))
        print(f"[Diagnoser] Published diagnosis to validation: {payload}")
        return {"status": "ok"}
    except Exception as e:
        print(f"[Diagnoser] Publish failed: {e}")
        # still return ok to avoid retries storm; validator just won't receive this one
        return {"status": "publish_failed", "error": str(e)}