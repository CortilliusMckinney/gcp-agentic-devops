import os
from secrets_manager import get_secret

# 🔑 Replace with your actual GCP Project ID
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "agentic-devops-464519")

# 🔑 Replace with the secret names you chose in Step 10-3
openai_api_key = get_secret("openai-api-key", PROJECT_ID)
cloudflare_api_key = get_secret("cloudflare-api-key", PROJECT_ID)
anthropic_api_key = get_secret("claude-agent-key", PROJECT_ID)

# ✅ Masked output for safety
print("✅ OpenAI key loaded:", openai_api_key[:8] + "...")
print("✅ Cloudflare key loaded:", cloudflare_api_key[:8] + "...")
print("✅ Anthropic key loaded:", anthropic_api_key[:8] + "...")





