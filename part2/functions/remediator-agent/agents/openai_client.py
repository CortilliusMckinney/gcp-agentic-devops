# ============================================
# 🧠 ai_client.py (shared)
# Loads API keys from Secret Manager and initializes:
#  - OpenAI client
#  - Anthropic (Claude) client
#  - Cloudflare Workers AI endpoint config
# ============================================

import os
from agents.secrets_manager import get_secret  # Secure secret fetcher

# --------------------------------------------
# 🔐 Secret names & project context
# --------------------------------------------
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "YOUR_PROJECT_ID")
OPENAI_SECRET = "openai-api-key"
CLOUDFLARE_SECRET = "cloudflare-api-key"
ANTHROPIC_SECRET = "claude-agent-key"

# --------------------------------------------
# 🔑 Retrieve API keys from GCP Secret Manager
# --------------------------------------------
openai_api_key = get_secret(OPENAI_SECRET, PROJECT_ID)
cloudflare_api_key = get_secret(CLOUDFLARE_SECRET, PROJECT_ID)
anthropic_api_key = get_secret(ANTHROPIC_SECRET, PROJECT_ID)

# --------------------------------------------
# 📦 Initialize SDK clients
# These are imported by the ModelRouter.
# --------------------------------------------
from openai import OpenAI
import anthropic

openai_client = OpenAI(api_key=openai_api_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)

# --------------------------------------------
# 🌐 Cloudflare Workers AI config
# --------------------------------------------
account_id = "561736ff0c0388f8c24aa22ffcc5e3d9"

CLOUDFLARE_BASE_URL = (
    f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/"
    "@cf/meta/llama-2-7b-chat-fp16"
)

headers_cf = {
    "Authorization": f"Bearer {cloudflare_api_key}",
    "Content-Type": "application/json"
}