"""
Local LLM Integration
Handles interactions with local LLMs using Ollama.
"""

import json
import logging
import requests
import sys
from typing import Dict, Any, Optional


class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def is_available(self) -> bool:
        """Check if Ollama is running and accessible."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_models(self) -> list:
        """Get list of available models."""
        try:
            response = self.session.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except requests.RequestException:
            return []
    
    def model_exists(self, model_name: str) -> bool:
        """Check if a specific model exists."""
        models = self.list_models()
        return model_name in models
    
    def generate(self, model: str, messages: list, max_tokens: int = 800, temperature: float = 0.7) -> Optional[str]:
        """Generate a response using the specified model."""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature
                }
            }
            
            response = self.session.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=120  # Increased timeout for local LLMs
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('message', {}).get('content', '').strip()
            else:
                logging.error(f"Ollama API error: {response.status_code} - {response.text}")
                return None
                
        except requests.RequestException as e:
            logging.error(f"Error communicating with Ollama: {e}")
            return None


def load_local_llm_config() -> Dict[str, Any]:
    """Load local LLM configuration from local_llm.json."""
    default_config = {
        "model": "deepseek-coder:6.7b",
        "base_url": "http://localhost:11434"
    }
    
    try:
        with open("local_llm.json", "r") as f:
            config = json.load(f)
            # Merge with defaults
            default_config.update(config)
            return default_config
    except FileNotFoundError:
        logging.warning("local_llm.json not found, using default configuration")
        return default_config
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing local_llm.json: {e}")
        return default_config


def validate_local_llm_setup() -> bool:
    """Validate that the local LLM setup is working."""
    config = load_local_llm_config()
    client = OllamaClient(config["base_url"])
    
    if not client.is_available():
        print("❌ Error: Ollama is not running or not accessible.")
        print("Please make sure Ollama is installed and running on your system.")
        print("You can start Ollama with: ollama serve")
        return False
    
    model = config["model"]
    if not client.model_exists(model):
        print(f"❌ Error: Model '{model}' is not available in Ollama.")
        print("Available models:")
        models = client.list_models()
        if models:
            for m in models:
                print(f"  - {m}")
        else:
            print("  No models found. Please pull a model first:")
            print(f"  ollama pull {model}")
        return False
    
    print(f"✅ Local LLM setup validated successfully!")
    print(f"   Model: {model}")
    print(f"   Base URL: {config['base_url']}")
    return True


def get_local_llm_client() -> Optional[OllamaClient]:
    """Get a configured Ollama client."""
    config = load_local_llm_config()
    client = OllamaClient(config["base_url"])
    
    if not client.is_available():
        return None
    
    return client


def get_local_llm_model() -> str:
    """Get the configured local LLM model name."""
    config = load_local_llm_config()
    return config["model"] 