from azure.openai import AzureOpenAI
import os
from functools import lru_cache

@lru_cache()
def get_azure_client():
    """
    Singleton pattern to create and cache the Azure OpenAI client.
    Uses lru_cache to ensure only one instance is created.
    """
    return AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-01",
        azure_endpoint="https://dwx-qe-open-ai-canadaeast.openai.azure.com"
    )

AZURE_DEPLOYMENT_NAME = 'dwx-qe-llm'

