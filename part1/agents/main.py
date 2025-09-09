import os
from secrets_manager import get_secret

# Environment variable for project ID
GCP_PROJECT_ID = os.environ.get("GCP_PROJECT_ID", "YOUR_PROJECT_ID")

# 🔑 Replace with the secret names from Step 10 of the setup guide
OPENAI_SECRET_NAME = "openai-api-key"
CLAUDE_SECRET_NAME = "claude-agent-key"
CLOUDFLARE_SECRET_NAME = "cloudflare-api-key"

# 🔑 Retrieve API keys from Secret Manager
openai_api_key = get_secret(OPENAI_SECRET_NAME, GCP_PROJECT_ID)
claude_api_key = get_secret(CLAUDE_SECRET_NAME, GCP_PROJECT_ID)
cloudflare_api_key = get_secret(CLOUDFLARE_SECRET_NAME, GCP_PROJECT_ID)

def safe_preview(key, name):
    if key:
        print(f"{name} key starts with: {key[:8]}...")
    else:
        print(f"{name} API key not found. Please check Secret Manager.")
        # Optional: exit(1) if missing keys should stop execution

safe_preview(openai_api_key, "OpenAI")
safe_preview(claude_api_key, "Claude")
safe_preview(cloudflare_api_key, "Cloudflare")





