# model_router.py

import json
import requests
from typing import Optional, Any, Dict, Union

# ✅ Import initialized clients from the previous step
from agents.clients import openai_client, anthropic_client, headers_cf, CLOUDFLARE_BASE_URL

class ModelRouter:
    """
    Central router class for dispatching prompts to OpenAI, Claude (Anthropic),
    or Cloudflare Workers AI. Standardizes responses for consistency.
    """

    def __init__(self):
        # Store API clients and config values for reuse
        self.openai = openai_client
        self.anthropic = anthropic_client
        self.cloudflare_url = CLOUDFLARE_BASE_URL
        self.cloudflare_headers = headers_cf

    def route(self, prompt: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Routes the incoming prompt to the correct model based on metadata.

        Args:
            prompt (str): The natural language prompt to send
            metadata (dict): Contains routing details like:
                {
                    "provider": "openai" | "anthropic" | "cloudflare",
                    "model": "<optional_model_id>"  # Overrides default if provided
                }

        Returns:
            dict: Standardized response with keys:
                - provider: Which AI model was used
                - response: The parsed model output
                - raw: The full raw response (SDK or JSON)
                - error: (optional) Error info if something fails
        """
        provider = metadata.get("provider", "").lower()

        if provider == "openai":
            model = metadata.get("model")
            return self.call_openai(prompt, model if model else "gpt-3.5-turbo")
        elif provider == "anthropic":
            model = metadata.get("model")
            return self.call_anthropic(prompt, model if model else "claude-3-haiku-20240307")
        elif provider == "cloudflare":
            return self.call_cloudflare(prompt)
        else:
            return {"error": f"Unsupported provider: {provider}"}

    def call_openai(self, prompt: str, model: str = "gpt-3.5-turbo") -> Dict[str, Any]:
        """
        Sends the prompt to OpenAI's chat endpoint.

        Args:
            prompt (str): User prompt
            model (str): Optional override model ID (default: gpt-3.5-turbo)

        Returns:
            dict: Standardized OpenAI response
        """
        try:
            response = self.openai.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300
            )
            return {
                "provider": "openai",
                "response": response.choices[0].message.content,
                "raw": response
            }
        except Exception as e:
            return {"error": f"OpenAI call failed: {str(e)}"}

    def call_anthropic(self, prompt: str, model: str = "claude-3-haiku-20240307") -> Dict[str, Any]:
        """
        Sends the prompt to Anthropic's Claude chat model.

        Args:
            prompt (str): User prompt
            model (str): Optional Claude model name (default: Claude 3 Haiku)

        Returns:
            dict: Standardized Anthropic response
        """
        try:
            response = self.anthropic.messages.create(
                model=model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}]
            )
            # Handle different content types safely
            content = response.content[0]
            # Use string conversion as fallback for all content types
            response_text = str(content)
            
            return {
                "provider": "anthropic",
                "response": response_text,
                "raw": response
            }
        except Exception as e:
            return {"error": f"Anthropic call failed: {str(e)}"}

    def call_cloudflare(self, prompt: str) -> Dict[str, Any]:
        """
        Sends the prompt to Cloudflare Workers AI using direct HTTP POST.

        Args:
            prompt (str): User prompt

        Returns:
            dict: Standardized Cloudflare response or error
        """
        payload = {
            "messages": [{"role": "user", "content": prompt}]
        }

        try:
            response = requests.post(self.cloudflare_url, headers=self.cloudflare_headers, json=payload)

            # Handle non-200 status codes
            if response.status_code == 200:
                data = response.json()
                return {
                    "provider": "cloudflare",
                    "response": data.get("result", {}).get("response", ""),
                    "raw": data
                }
            else:
                return {
                    "error": f"Cloudflare failed: {response.status_code}",
                    "details": response.text
                }
        except Exception as e:
            return {"error": f"Cloudflare request error: {str(e)}"}