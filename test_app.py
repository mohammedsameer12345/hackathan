#!/usr/bin/env python3
"""
Test script for the Intelligent Document Query System
"""

import requests
import json
import os
import time

def test_health_endpoint():
    """Test the health check endpoint"""
    print("Testing health endpoint...")
    try:
        response = requests.get('http://localhost:5000/health')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_main_page():
    """Test the main page loads"""
    print("Testing main page...")
    try:
        response = requests.get('http://localhost:5000/')
        if response.status_code == 200:
            print("✅ Main page loads successfully")
            return True
        else:
            print(f"❌ Main page failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Main page error: {e}")
        return False

def test_upload_endpoint():
    """Test the upload endpoint (without file)"""
    print("Testing upload endpoint...")
    try:
        response = requests.post('http://localhost:5000/upload')
        if response.status_code == 400:
            data = response.json()
            if 'error' in data and 'No file provided' in data['error']:
                print("✅ Upload endpoint correctly rejects empty requests")
                return True
            else:
                print(f"❌ Upload endpoint unexpected response: {data}")
                return False
        else:
            print(f"❌ Upload endpoint should return 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Upload endpoint error: {e}")
        return False

def test_query_endpoint():
    """Test the query endpoint (without data)"""
    print("Testing query endpoint...")
    try:
        response = requests.post('http://localhost:5000/query')
        if response.status_code == 400:
            data = response.json()
            if 'error' in data and 'No query provided' in data['error']:
                print("✅ Query endpoint correctly rejects empty requests")
                return True
            else:
                print(f"❌ Query endpoint unexpected response: {data}")
                return False
        else:
            print(f"❌ Query endpoint should return 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Query endpoint error: {e}")
        return False

def test_analyze_endpoint():
    """Test the analyze endpoint (without data)"""
    print("Testing analyze endpoint...")
    try:
        response = requests.post('http://localhost:5000/analyze')
        if response.status_code == 400:
            data = response.json()
            if 'error' in data and 'No document text provided' in data['error']:
                print("✅ Analyze endpoint correctly rejects empty requests")
                return True
            else:
                print(f"❌ Analyze endpoint unexpected response: {data}")
                return False
        else:
            print(f"❌ Analyze endpoint should return 400, got {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Analyze endpoint error: {e}")
        return False

def test_perplexity_api():
    """Test the Perplexity API integration"""
    print("Testing Perplexity API integration...")
    try:
        from perplexity_api import PerplexityAPI
        
        api_client = PerplexityAPI()
        result = api_client.query_document(
            "What is covered under this insurance policy?",
            "This is a sample insurance policy document that covers medical expenses.",
            "coverage"
        )
        
        if 'answer' in result and 'clauses' in result:
            print("✅ Perplexity API integration working")
            print(f"   Answer: {result['answer'][:100]}...")
            print(f"   Clauses found: {len(result['clauses'])}")
            return True
        else:
            print(f"❌ Perplexity API unexpected response: {result}")
            return False
    except Exception as e:
        print(f"❌ Perplexity API error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Intelligent Document Query System Tests")
    print("=" * 50)
    
    # Check if app is running
    print("Checking if application is running...")
    if not test_health_endpoint():
        print("❌ Application is not running. Please start it first:")
        print("   python app.py")
        return
    
    print("\n✅ Application is running! Starting tests...\n")
    
    # Run tests
    tests = [
        test_main_page,
        test_upload_endpoint,
        test_query_endpoint,
        test_analyze_endpoint,
        test_perplexity_api
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    # Summary
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your application is working correctly.")
        print("\n🌐 You can now access your application at: http://localhost:5000")
        print("📖 Check the README.md for usage instructions")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("🔧 Make sure all dependencies are installed and the app is running correctly.")

if __name__ == "__main__":
    main() 