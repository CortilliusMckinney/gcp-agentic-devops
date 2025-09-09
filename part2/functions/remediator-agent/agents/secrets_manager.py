# ============================================
# 🔐 secrets_manager.py (shared)
# Small helper to fetch secret values from
# Google Cloud Secret Manager.
# ============================================

from google.cloud import secretmanager

def get_secret(secret_id: str, project_id: str) -> str:
    """
    Fetch the latest version of a secret from GCP Secret Manager.
    Args:
        secret_id: Name of the secret (e.g., "openai-api-key")
        project_id: Your GCP project ID
    Returns:
        The secret value as a UTF-8 string.
    """
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")