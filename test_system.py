#!/usr/bin/env python3
"""
Test Script for Japanese Car VIN Decoder System
===============================================

This script tests all components of the VIN decoder system.
"""

import requests
import json
import time
from japanese_car_vin_decoder import JapaneseCarVINDecoder

def test_vin_decoder():
    """Test the VIN decoder functionality"""
    print("🧪 Testing VIN Decoder...")
    
    decoder = JapaneseCarVINDecoder()
    
    # Test VINs
    test_vins = [
        "1HGBH41JXMN109186",  # Honda
        "1NXBR32E85Z123456",  # Toyota
        "1N4AL11D75C123456",  # Nissan
    ]
    
    for vin in test_vins:
        print(f"\n📋 Testing VIN: {vin}")
        vehicle_info = decoder.decode_vin(vin)
        
        if vehicle_info:
            print(f"✅ Successfully decoded:")
            print(f"   Make: {vehicle_info.make}")
            print(f"   Model: {vehicle_info.model}")
            print(f"   Year: {vehicle_info.year}")
            print(f"   Engine: {vehicle_info.engine}")
            print(f"   Parts categories: {len(vehicle_info.parts_compatibility)}")
        else:
            print(f"❌ Failed to decode VIN: {vin}")

def test_web_api():
    """Test the web API endpoints"""
    print("\n🌐 Testing Web API...")
    
    base_url = "http://localhost:5000"
    test_vin = "1NXBR32E85Z123456"
    
    # Test GET /api/vehicle/{vin}
    try:
        response = requests.get(f"{base_url}/api/vehicle/{test_vin}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ GET /api/vehicle/{vin} - Working")
            else:
                print("❌ GET /api/vehicle/{vin} - Failed")
        else:
            print(f"❌ GET /api/vehicle/{test_vin} - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ GET /api/vehicle/{test_vin} - Error: {e}")
    
    # Test GET /api/parts/{vin}
    try:
        response = requests.get(f"{base_url}/api/parts/{test_vin}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ GET /api/parts/{vin} - Working")
            else:
                print("❌ GET /api/parts/{vin} - Failed")
        else:
            print(f"❌ GET /api/parts/{test_vin} - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ GET /api/parts/{test_vin} - Error: {e}")
    
    # Test POST /decode
    try:
        response = requests.post(
            f"{base_url}/decode",
            json={"vin": test_vin},
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ POST /decode - Working")
            else:
                print("❌ POST /decode - Failed")
        else:
            print(f"❌ POST /decode - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ POST /decode - Error: {e}")

def test_nhtsa_api():
    """Test NHTSA API connectivity"""
    print("\n🔗 Testing NHTSA API connectivity...")
    
    try:
        response = requests.get(
            "https://vpic.nhtsa.dot.gov/api/vehicles/DecodeVin/1HGBH41JXMN109186?format=json",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('Count', 0) > 0:
                print("✅ NHTSA API - Working")
                print(f"   Found {data.get('Count')} data points")
            else:
                print("❌ NHTSA API - No data returned")
        else:
            print(f"❌ NHTSA API - HTTP {response.status_code}")
    except Exception as e:
        print(f"❌ NHTSA API - Error: {e}")

def main():
    """Run all tests"""
    print("🚗 Japanese Car VIN Decoder System - Test Suite")
    print("=" * 50)
    
    # Test NHTSA API first
    test_nhtsa_api()
    
    # Test VIN decoder
    test_vin_decoder()
    
    # Test web API (if server is running)
    print("\n🌐 Checking if web server is running...")
    try:
        response = requests.get("http://localhost:5000", timeout=5)
        if response.status_code == 200:
            print("✅ Web server is running")
            test_web_api()
        else:
            print("❌ Web server not responding properly")
    except requests.exceptions.ConnectionError:
        print("❌ Web server is not running")
        print("   Start it with: python3 simple_web_interface.py")
    except Exception as e:
        print(f"❌ Error checking web server: {e}")
    
    print("\n🎉 Test suite completed!")

if __name__ == "__main__":
    main()
