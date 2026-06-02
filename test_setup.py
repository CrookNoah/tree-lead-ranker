#!/usr/bin/env python3
"""Test setup and validate configuration"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported"""
    print("📦 Testing imports...")
    
    required = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "requests",
        "bs4",
        "anthropic",
    ]
    
    missing = []
    for module in required:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} NOT FOUND")
            missing.append(module)
    
    return len(missing) == 0

def test_env():
    """Test .env configuration"""
    print("\n🔐 Testing environment variables...")
    
    if not Path(".env").exists():
        print("   ❌ .env file not found")
        print("      → Run: cp .env.example .env")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    keys = [
        ("GOOGLE_PLACES_API_KEY", "Google Places API"),
        ("ANTHROPIC_API_KEY", "Anthropic API"),
    ]
    
    missing = []
    for key, name in keys:
        value = os.getenv(key, "")
        if not value or value.startswith("your_"):
            print(f"   ⚠️  {name} ({key}) not set")
            missing.append(key)
        else:
            # Show only first/last characters for security
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "..."
            print(f"   ✅ {name}: {masked}")
    
    if missing:
        print(f"\n   To configure: Edit .env and set {', '.join(missing)}")
        return False
    
    return True

def test_database():
    """Test database setup"""
    print("\n💾 Testing database...")
    
    try:
        from models import engine, Base
        Base.metadata.create_all(engine)
        print("   ✅ Database initialized")
        return True
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def test_config():
    """Test configuration"""
    print("\n⚙️  Testing configuration...")
    
    try:
        from config import STATES_AND_CITIES, SEARCH_TERMS, AI_MODEL
        
        states = len(STATES_AND_CITIES)
        cities = sum(len(v["cities"]) for v in STATES_AND_CITIES.values())
        terms = len(SEARCH_TERMS)
        
        print(f"   ✅ {states} states configured")
        print(f"   ✅ {cities} cities configured")
        print(f"   ✅ {terms} search terms configured")
        print(f"   ✅ AI Model: {AI_MODEL}")
        
        return True
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False

def test_api_modules():
    """Test API integration modules"""
    print("\n🔌 Testing API modules...")
    
    try:
        from places_api import get_places_api
        print("   ✅ Google Places API module")
    except Exception as e:
        print(f"   ❌ Google Places API error: {e}")
        return False
    
    try:
        from website_auditor import get_auditor
        print("   ✅ Website Auditor module")
    except Exception as e:
        print(f"   ❌ Website Auditor error: {e}")
        return False
    
    try:
        from lead_analyzer import get_analyzer
        print("   ✅ Lead Analyzer module")
    except Exception as e:
        print(f"   ❌ Lead Analyzer error: {e}")
        return False
    
    try:
        from deduplicator import deduplicate_businesses
        print("   ✅ Deduplicator module")
    except Exception as e:
        print(f"   ❌ Deduplicator error: {e}")
        return False
    
    return True

def test_web_connectivity():
    """Test basic web connectivity"""
    print("\n🌐 Testing web connectivity...")
    
    try:
        import requests
        # Test Google Places API is reachable
        response = requests.head("https://maps.googleapis.com/maps/api/place/textsearch/json", timeout=5)
        print("   ✅ Google Places API reachable")
        return True
    except Exception as e:
        print(f"   ⚠️  Could not verify Google connectivity: {e}")
        print("      (This may be due to network firewall - okay if you have API key)")
        return True  # Not critical

def main():
    """Run all tests"""
    print("\n" + "="*50)
    print("🌲 Tree Lead Ranker - Setup Test")
    print("="*50)
    
    tests = [
        ("Imports", test_imports),
        ("Environment", test_env),
        ("Database", test_database),
        ("Configuration", test_config),
        ("API Modules", test_api_modules),
        ("Web Connectivity", test_web_connectivity),
    ]
    
    results = []
    for name, test in tests:
        try:
            result = test()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} test failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "="*50)
    print("📊 Summary")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Ready to run.")
        print("   → Run: python main.py")
        return 0
    elif passed >= total - 1:
        print("\n⚠️  Most tests passed. Some features may not work.")
        print("   → Check errors above and fix configuration.")
        print("   → You can still try: python main.py")
        return 1
    else:
        print("\n❌ Setup incomplete. Please fix errors above.")
        print("   See QUICKSTART.md for setup instructions.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
