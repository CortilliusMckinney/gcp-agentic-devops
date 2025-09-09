import base64
import json
import os
import subprocess
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


def _execute_command(command, timeout=300):
    """
    Safely execute a command with timeout and logging.
    Returns (success, stdout, stderr).
    """
    print(f"[Remediator] Executing command: {command}")
    
    try:
        # Use shell=False for better security, but allow shell=True for npm/git commands
        if command.startswith(('npm ', 'git ', 'echo ')):
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd="/tmp"  # Safe working directory
            )
        else:
            # Split command for non-shell execution
            cmd_parts = command.split()
            result = subprocess.run(
                cmd_parts,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd="/tmp"
            )
        
        success = result.returncode == 0
        print(f"[Remediator] Command {'succeeded' if success else 'failed'} (code: {result.returncode})")
        
        if result.stdout:
            print(f"[Remediator] STDOUT: {result.stdout[:500]}...")
        if result.stderr:
            print(f"[Remediator] STDERR: {result.stderr[:500]}...")
            
        return success, result.stdout, result.stderr
        
    except subprocess.TimeoutExpired:
        print(f"[Remediator] Command timed out after {timeout}s")
        return False, "", f"Command timed out after {timeout} seconds"
    except Exception as e:
        print(f"[Remediator] Command execution failed: {e}")
        return False, "", str(e)


def _is_safe_command(command):
    """
    Additional safety check for commands.
    Returns (safe, reason).
    """
    command_lower = command.lower()
    
    # Dangerous patterns
    dangerous_patterns = [
        'rm -rf', 'sudo rm', 'rm -f /',
        'format', 'fdisk', 'mkfs',
        'dd if=', 'kill -9',
        'shutdown', 'reboot',
        'chmod 777', 'chown -R',
        'curl | sh', 'wget | sh',
        '$(', '`', '|sh', '|bash',
        'eval', 'exec',
        '/etc/', '/var/', '/usr/',
        'passwd', 'su -', 'sudo su'
    ]
    
    for pattern in dangerous_patterns:
        if pattern in command_lower:
            return False, f"Dangerous pattern detected: {pattern}"
    
    # Safe commands
    safe_patterns = [
        'npm install', 'npm update', 'npm ci',
        'git pull', 'git checkout', 'git reset',
        'echo ', 'cat ', 'ls ', 'pwd',
        'mkdir -p', 'touch ',
        'pip install', 'pip upgrade'
    ]
    
    for pattern in safe_patterns:
        if command_lower.startswith(pattern):
            return True, f"Safe command pattern: {pattern}"
    
    # Default: require manual review
    return False, "Command requires manual review"


@functions_framework.cloud_event
def remediate_event(cloud_event):
    """
    Pub/Sub-triggered function:
      - Receives approved fixes from validator
      - Executes safe, low-risk remediation commands
      - Logs execution results
    """
    print("[Remediator] Processing remediation task")
    
    # Decode remediation task
    task = _decode_pubsub_message(cloud_event)
    print(f"[Remediator] Received task: {task}")
    
    # Validate task structure
    if not task.get("approved", False):
        print("[Remediator] ❌ Task not approved, skipping")
        return {"status": "skipped", "reason": "Not approved"}
    
    command = task.get("command", "")
    risk = task.get("risk", "high")
    fix_type = task.get("fix_type", "unknown")
    
    if not command or command == "echo 'manual review required'":
        print("[Remediator] ❌ No valid command to execute")
        return {"status": "skipped", "reason": "No valid command"}
    
    # Risk assessment
    if risk not in ["low"]:
        print(f"[Remediator] ❌ Risk level '{risk}' requires manual approval")
        return {"status": "rejected", "reason": f"Risk level {risk} requires manual approval"}
    
    # Safety check
    is_safe, safety_reason = _is_safe_command(command)
    if not is_safe:
        print(f"[Remediator] ❌ Safety check failed: {safety_reason}")
        return {"status": "rejected", "reason": safety_reason}
    
    print(f"[Remediator] ✅ Safety check passed: {safety_reason}")
    
    # Execute the command
    if fix_type == "npm_fix":
        print("[Remediator] Executing npm fix:", command)
        success, stdout, stderr = _execute_command(command, timeout=600)  # 10 min for npm
    else:
        print(f"[Remediator] Executing {fix_type}:", command)
        success, stdout, stderr = _execute_command(command, timeout=300)  # 5 min default
    
    # Create execution result
    result = {
        "id": f"exec-{int(time.time())}-{uuid.uuid4().hex[:8]}",
        "task_id": task.get("id", "unknown"),
        "command": command,
        "fix_type": fix_type,
        "risk": risk,
        "success": success,
        "stdout": stdout[:1000] if stdout else "",  # Truncate long output
        "stderr": stderr[:1000] if stderr else "",
        "execution_timestamp": time.time(),
        "metadata": task.get("metadata", {})
    }
    
    if success:
        print("[Remediator] ✅ Remediator Fix executed successfully")
        print(f"[Remediator] Output: {stdout[:200]}...")
    else:
        print("[Remediator] ❌ Fix execution failed")
        print(f"[Remediator] Error: {stderr[:200]}...")
    
    # Log result (in production, you might want to store this in Firestore or BigQuery)
    print(f"[Remediator] Execution result: {result}")
    
    return {
        "status": "executed" if success else "failed",
        "result": result
    }