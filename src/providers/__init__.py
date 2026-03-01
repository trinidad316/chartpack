"""
Data Providers Package
Contains all market data provider implementations
"""
from .databento_provider import DataBentoProvider

# Register all available providers
AVAILABLE_PROVIDERS = {
    "databento": DataBentoProvider,
}