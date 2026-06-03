#!/usr/bin/env python3
"""Quick test of API endpoints"""
import requests
import json
import time

BASE_URL = "http://localhost:3000"

print("🧪 Testing Tree Lead Ranker API...\n")

# Test 1: Check if server is running
print("1️⃣  Testing server connection...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"   ✅ Server is running: {response.json()}")
except Exception as e:
    print(f"   ❌ Server error: {e}")
    exit(1)

# Test 2: Get states
print("\n2️⃣  Testing /states endpoint...")
try:
    response = requests.get(f"{BASE_URL}/states")
    states = response.json()
    print(f"   ✅ States loaded: {len(states)} states")
    print(f"   Sample: SC has {len(states.get('SC', []))} cities")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 3: Get cities for a state
print("\n3️⃣  Testing /states/SC/cities endpoint...")
try:
    response = requests.get(f"{BASE_URL}/states/SC/cities")
    data = response.json()
    print(f"   ✅ Cities loaded: {data.get('cities', [])}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 4: Test scan endpoint
print("\n4️⃣  Testing /scan POST endpoint...")
try:
    scan_data = {"state": "SC", "city": "Charleston"}
    response = requests.post(f"{BASE_URL}/scan", json=scan_data)
    print(f"   ✅ Scan initiated: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test 5: Test progress stream
print("\n5️⃣  Testing /scan/progress stream...")
try:
    response = requests.get(f"{BASE_URL}/scan/progress", stream=True)
    print(f"   ✅ Progress stream connected (status: {response.status_code})")
    
    # Read first few events
    lines_read = 0
    for line in response.iter_lines():
        if line and lines_read < 3:
            print(f"   📨 {line.decode()}")
            lines_read += 1
        elif lines_read >= 3:
            break
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n✅ API tests complete!")
