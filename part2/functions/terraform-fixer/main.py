import os
import base64
import json
import functions_framework

@functions_framework.cloud_event  
def terraform_fix_event(cloud_event):
    """Terraform Fix Generator - with maximum defensive programming."""
    print("🔧 [Terraform Fixer] Function started")
    
    try:
        print("🔧 [Terraform Fixer] Processing event (AI disabled for debugging)")
        
        # Step 1: Check if event exists
        if not cloud_event:
            print("🔧 [Terraform Fixer] No cloud_event received")
            return
        
        # Step 2: Check if data exists  
        if not hasattr(cloud_event, 'data') or not cloud_event.data:
            print("🔧 [Terraform Fixer] No event data")
            return
            
        print("🔧 [Terraform Fixer] Event data exists")
        
        # Step 3: Log the type and basic info
        try:
            print(f"🔧 [Terraform Fixer] Event data type: {type(cloud_event.data)}")
            print(f"🔧 [Terraform Fixer] Event data keys: {list(cloud_event.data.keys()) if isinstance(cloud_event.data, dict) else 'not dict'}")
        except Exception as e:
            print(f"🔧 [Terraform Fixer] Error logging data info: {e}")
        
        # Step 4: Try to extract message
        try:
            if isinstance(cloud_event.data, dict) and 'message' in cloud_event.data:
                message = cloud_event.data['message']
                print(f"🔧 [Terraform Fixer] Found message: {type(message)}")
                
                if 'data' in message:
                    base64_data = message['data']
                    print(f"🔧 [Terraform Fixer] Found base64 data: {len(base64_data)} chars")
                    
                    # Step 5: Try base64 decode
                    try:
                        decoded_message = base64.b64decode(base64_data).decode('utf-8')
                        print(f"🔧 [Terraform Fixer] Decoded successfully: {len(decoded_message)} chars")
                        
                        # Step 6: Try JSON parse
                        try:
                            drift_data = json.loads(decoded_message)
                            print("🔧 [Terraform Fixer] JSON parsed successfully")
                            
                            drift_issues = drift_data.get("drift_issues", [])
                            print(f"🔧 [Terraform Fixer] Found {len(drift_issues)} drift issues")
                            
                            # Log each issue safely
                            for i, issue in enumerate(drift_issues[:5]):  # Limit to 5
                                try:
                                    issue_type = issue.get('type', 'unknown')
                                    resource_name = issue.get('resource_name', 'unknown')
                                    print(f"🔧 [Terraform Fixer] Issue {i+1}: {issue_type} - {resource_name}")
                                except Exception as e:
                                    print(f"🔧 [Terraform Fixer] Error logging issue {i+1}: {e}")
                            
                        except json.JSONDecodeError as e:
                            print(f"🔧 [Terraform Fixer] JSON parse error: {e}")
                            drift_issues = []
                            
                    except Exception as e:
                        print(f"🔧 [Terraform Fixer] Base64 decode error: {e}")
                        drift_issues = []
                        
                else:
                    print("🔧 [Terraform Fixer] No 'data' field in message")
                    drift_issues = []
            else:
                print("🔧 [Terraform Fixer] No 'message' field in event data")
                drift_issues = []
                
        except Exception as e:
            print(f"🔧 [Terraform Fixer] Error in message processing: {e}")
            drift_issues = []
        
        print("🔧 [Terraform Fixer] Function completed successfully")
        # No return needed for CloudEvent functions
        
    except Exception as e:
        print(f"🔧 [Terraform Fixer] Critical error: {e}")
        # No return needed for CloudEvent functions
