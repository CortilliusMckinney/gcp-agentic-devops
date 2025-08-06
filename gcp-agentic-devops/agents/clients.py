import os
import json
import requests
from secrets_manager import get_secret

# 🔐 Project and Secret Names
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "agentic-devops-464519")
OPENAI_SECRET = "openai-api-key"
CLOUDFLARE_SECRET = "cloudflare-api-key"
ANTHROPIC_SECRET = "claude-agent-key"

# 🔑 Retrieve API keys from Secret Manager
openai_api_key = get_secret(OPENAI_SECRET, PROJECT_ID)
cloudflare_api_key = get_secret(CLOUDFLARE_SECRET, PROJECT_ID)
anthropic_api_key = get_secret(ANTHROPIC_SECRET, PROJECT_ID)

# ✅ Masked output for safety
print("🔑 Loaded OpenAI Key:", openai_api_key[:8] + "..." + openai_api_key[-4:])
print("🔑 Loaded Cloudflare Key:", cloudflare_api_key[:8] + "..." + cloudflare_api_key[-4:])
print("🔑 Loaded Anthropic Key:", anthropic_api_key[:8] + "..." + anthropic_api_key[-4:])

# 📦 Initialize SDK Clients
from openai import OpenAI
import anthropic

openai_client = OpenAI(api_key=openai_api_key)
anthropic_client = anthropic.Anthropic(api_key=anthropic_api_key)

# 🌐 Cloudflare Workers AI Endpoint – your real account ID
account_id = "561736ff0c0388f8c24aa22ffcc5e3d9"
CLOUDFLARE_BASE_URL = f"https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/run/@cf/meta/llama-2-7b-chat-fp16"

headers_cf = {
    "Authorization": f"Bearer {cloudflare_api_key}",
    "Content-Type": "application/json"
}
payload_cf = {
    "messages": [
        {"role": "user", "content": "Say hello from Cloudflare Workers AI!"}
    ]
}

print("\n✅ OpenAI client initialized")
print("✅ Anthropic client initialized")
print("✅ Cloudflare Workers AI headers prepared")

# 📤 Show Cloudflare Headers nicely
print("\n📤 Cloudflare Headers (Pretty Printed):")
print(json.dumps(headers_cf, indent=2))

# 🔍 Test OpenAI
print("\n🔍 Testing OpenAI...\n" + "-"*40)
try:
    models = openai_client.models.list()
    print("✅ OpenAI Models Available:", [m.id for m in models.data[:3]], "...")
except Exception as e:
    print("❌ OpenAI test failed:", str(e))

# 🔍 Test Anthropic
print("\n🔍 Testing Anthropic...\n" + "-"*40)
try:
    response = anthropic_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=20,
        messages=[{"role": "user", "content": "Test response"}]
    )
    print("✅ Anthropic Test Response:", response.content[0].text)
except Exception as e:
    print("❌ Anthropic test failed:", str(e))

# 🔍 Test Cloudflare Workers AI
print("\n🔍 Testing Cloudflare Workers AI...\n" + "-"*40)
try:
    print("📤 Cloudflare Request URL:", CLOUDFLARE_BASE_URL)
    print("📤 Cloudflare Payload:", json.dumps(payload_cf, indent=2))

    response_cf = requests.post(CLOUDFLARE_BASE_URL, headers=headers_cf, json=payload_cf)

    print("📥 Cloudflare Response Code:", response_cf.status_code)
    print("📥 Cloudflare Raw Response:", response_cf.text)

    if response_cf.status_code == 200:
        cf_data = response_cf.json()
        print("✅ Cloudflare Test Response:", cf_data.get("result", {}).get("response", "")[:60], "...")
    else:
        print("❌ Cloudflare Test Failed:", response_cf.status_code, response_cf.text)
except Exception as e:
    print("❌ Cloudflare request failed:", str(e))