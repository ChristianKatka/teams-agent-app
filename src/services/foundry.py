import os

from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.azure import AzureProvider


def build_model() -> OpenAIChatModel:
    return OpenAIChatModel(
        os.environ["AZURE_OPENAI_DEPLOYMENT"],
        provider=AzureProvider(
            azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_version=os.environ["AZURE_OPENAI_API_VERSION"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
        ),
    )
