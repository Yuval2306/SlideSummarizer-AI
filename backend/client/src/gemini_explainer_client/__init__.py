"""
Gemini Explainer Client
A Python client library for interacting with the Gemini Explainer Web API.
"""

from .client import ExplainerClient, Status, ExplainerClientError

__version__ = "0.1.0"
__all__ = ["ExplainerClient", "Status", "ExplainerClientError"]