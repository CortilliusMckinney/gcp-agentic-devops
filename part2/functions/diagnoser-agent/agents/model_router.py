# ============================================
# 🤖 agents/model_router.py (Clean Production Version)
# Routes prompts to AI models without testing noise
# ============================================

import os
import json
import requests
from typing import Dict, Any, Optional
from openai import OpenAI
from anthropic import Anthropic

# Configuration
VERBOSE = os.getenv("VERBOSE_LOGS", "0") == "1"

class ModelRouter:
    def __init__(self):
        """Initialize AI clients without testing noise."""
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.anthropic = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.cloudflare_url = f"https://api.cloudflare.com/client/v4/accounts/{os.getenv('CLOUDFLARE_ACCOUNT_ID')}/ai/run/@cf/meta/llama-2-7b-chat-fp16"
        self.cloudflare_headers = {
            "Authorization": f"Bearer {os.getenv('CLOUDFLARE_API_TOKEN')}",
            "Content-Type": "application/json"
        }
        
        # NO TESTING IN PRODUCTION - keeps logs clean

    def route(self, prompt: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Route prompt to appropriate AI model."""
        if not metadata:
            metadata = {}
            
        provider = metadata.get("provider", "openai").lower()
        model = metadata.get("model")
        
        if provider == "openai":
            return self._call_openai(prompt, model or "gpt-3.5-turbo")
        elif provider == "anthropic":
            return self._call_anthropic(prompt, model or "claude-3-haiku-20240307")
        elif provider == "cloudflare":
            return self._call_cloudflare(prompt)
        else:
            return {"provider": provider, "response": None, "error": "Unknown provider"}

    def _call_openai(self, prompt: str, model: str) -> Dict[str, Any]:
        """Call OpenAI API."""
        try:
            resp = self.openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.3,
            )
            return {
                "provider": "openai",
                "response": resp.choices[0].message.content,
                "raw": resp,
            }
        except Exception as e:
            return {"provider": "openai", "response": None, "error": f"OpenAI call failed: {e}"}

    def _call_anthropic(self, prompt: str, model: str) -> Dict[str, Any]:
        """Call Anthropic API with safe text extraction."""
        try:
            resp = self.anthropic.messages.create(
                model=model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            content = resp.content[0]
            
            # Safe text extraction with fallback
            try:
                response_text = content.text  # type: ignore
            except AttributeError:
                response_text = str(content)
            
            return {
                "provider": "anthropic",
                "response": response_text,
                "raw": resp,
            }
        except Exception as e:
            return {"provider": "anthropic", "response": None, "error": f"Anthropic call failed: {e}"}

    def _call_cloudflare(self, prompt: str) -> Dict[str, Any]:
        """Call Cloudflare Workers AI API."""
        try:
            payload = {
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
            }
            
            resp = requests.post(
                self.cloudflare_url,
                headers=self.cloudflare_headers,
                json=payload,
                timeout=30
            )
            
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success") and "result" in data:
                    return {
                        "provider": "cloudflare",
                        "response": data["result"].get("response", ""),
                        "raw": data,
                    }
                else:
                    return {"provider": "cloudflare", "response": None, "error": "API success=false"}
            else:
                return {"provider": "cloudflare", "response": None, "error": f"HTTP {resp.status_code}"}
                
        except Exception as e:
            return {"provider": "cloudflare", "response": None, "error": f"Cloudflare call failed: {e}"}