"""Test script to verify AI functionality"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')
print(f"API Key found: {'Yes' if api_key else 'No'}")

if api_key:
    print(f"API Key starts with: {api_key[:10]}...")
    
    try:
        genai.configure(api_key=api_key)
        
        # List available models first
        print("Available models:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"  - {m.name}")
        
        # Test with the most stable model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        test_response = model.generate_content("Test: Is PM Modi the current Prime Minister of India?")
        
        if test_response and test_response.text:
            print("✅ AI Test Successful!")
            print("Response:", test_response.text[:200] + "..." if len(test_response.text) > 200 else test_response.text)
        else:
            print("❌ No response from AI")
            
    except Exception as e:
        print(f"❌ AI Test Failed: {str(e)}")
else:
    print("❌ No API key found in .env file")