#!/usr/bin/env python3
"""
Setup script for local LLM configuration
"""

import json
import sys
import os

def setup_local_llm():
    """Interactive setup for local LLM configuration."""
    print("🔧 Local LLM Setup")
    print("=" * 30)
    
    # Read configuration from local_llm.json
    try:
        with open("local_llm.json", "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"❌ Error reading local_llm.json: {e}")
        config = {}
    
    print("\nThis script will help you configure your local LLM settings.")
    print("Press Enter to use the default values, or type your preferred values.")
    
    # Get model name
    print(f"\nModel name (default: {config['model']}):")
    model = input().strip()
    if model:
        config["model"] = model
    
    # Get base URL
    print(f"\nOllama base URL (default: {config['base_url']}):")
    base_url = input().strip()
    if base_url:
        config["base_url"] = base_url
    
    # Save configuration
    try:
        with open("local_llm.json", "w") as f:
            json.dump(config, f, indent=4)
        print(f"\n✅ Configuration saved to local_llm.json:")
        print(f"   Model: {config['model']}")
        print(f"   Base URL: {config['base_url']}")
        
        print("\n📝 Next steps:")
        print("1. Make sure Ollama is installed and running")
        print("2. Pull your model: ollama pull " + config['model'])
        print("3. Test the setup: python test_local_llm.py")
        print("4. Run the app: python app.py local")
        
    except Exception as e:
        print(f"❌ Error saving configuration: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = setup_local_llm()
    sys.exit(0 if success else 1) 