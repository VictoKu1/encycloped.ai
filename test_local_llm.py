#!/usr/bin/env python3
"""
Test script for local LLM integration
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.local_llm import validate_local_llm_setup, get_local_llm_client, get_local_llm_model
from agents.topic_generator import set_llm_mode, generate_topic_content

def test_local_llm():
    """Test the local LLM integration."""
    print("🧪 Testing Local LLM Integration")
    print("=" * 40)
    
    # Test 1: Validate setup
    print("\n1. Testing setup validation...")
    if validate_local_llm_setup():
        print("✅ Setup validation passed")
    else:
        print("❌ Setup validation failed")
        return False
    
    # Test 2: Get client
    print("\n2. Testing client creation...")
    client = get_local_llm_client()
    if client:
        print("✅ Client creation successful")
    else:
        print("❌ Client creation failed")
        return False
    
    # Test 3: Get model
    print("\n3. Testing model configuration...")
    model = get_local_llm_model()
    print(f"✅ Model configured: {model}")
    
    # Test 4: Test topic generation
    print("\n4. Testing topic generation...")
    set_llm_mode(True)  # Enable local LLM mode
    
    try:
        reply_code, content = generate_topic_content("Python")
        if reply_code in ["1", "45"]:
            print("✅ Topic generation successful")
            print(f"   Reply code: {reply_code}")
            print(f"   Content length: {len(content)} characters")
        else:
            print("❌ Topic generation failed")
            print(f"   Reply code: {reply_code}")
            return False
    except Exception as e:
        print(f"❌ Topic generation error: {e}")
        return False
    
    print("\n🎉 All tests passed! Local LLM integration is working correctly.")
    return True

if __name__ == "__main__":
    success = test_local_llm()
    sys.exit(0 if success else 1) 