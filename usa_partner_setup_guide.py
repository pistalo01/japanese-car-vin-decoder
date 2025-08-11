#!/usr/bin/env python3
"""
USA Partner Setup Guide for PartsTech API
=========================================

This script provides setup instructions and testing tools specifically for your USA partner
to establish the PartsTech API connection that's blocked from other locations.
"""

import requests
import json
import sys
from datetime import datetime
from typing import Dict, Any, List

class USAPartnerSetup:
    """Setup and testing tools for USA-based partner"""
    
    def __init__(self):
        self.username = "unitypartsllc@gmail.com"
        self.api_key = "b2b87bdc38ec417c8e69f936638e3c1c"
        self.base_url = "https://api.partstech.com"
        
    def display_setup_instructions(self):
        """Display comprehensive setup instructions for USA partner"""
        instructions = """
🇺🇸 USA PARTNER - PARTSTECH API SETUP GUIDE
===========================================

ISSUE IDENTIFIED: PartsTech API is geographically restricted and blocked outside the USA.
SOLUTION: Your USA partner needs to test and configure the API from their US location.

📋 SETUP STEPS FOR USA PARTNER:

1️⃣  VERIFY LOCATION & NETWORK
   • Confirm you're connecting from within the United States
   • Use a business/residential IP (avoid VPNs if possible)
   • Test from the same network that will be used in production

2️⃣  CREDENTIALS PROVIDED:
   • Username: unitypartsllc@gmail.com
   • API Key: b2b87bdc38ec417c8e69f936638e3c1c
   • Base URL: https://api.partstech.com

3️⃣  QUICK TEST COMMAND:
   Run this Python script to test the connection:
   
   python3 usa_partner_setup_guide.py --test
   
4️⃣  EXPECTED RESULTS:
   ✅ Should get HTTP 200 or 401 (not 403 CloudFront block)
   ✅ Should receive proper API responses
   ✅ JWT authentication should work

5️⃣  IF SUCCESSFUL:
   • Document the working configuration
   • Set up the API integration in your production environment  
   • Configure automated testing to monitor API health

6️⃣  IF ISSUES PERSIST:
   • Contact PartsTech support: https://app.partstech.com
   • Mention account: unitypartsllc@gmail.com
   • Request IP whitelisting if needed
   • Verify account activation status

📞 SUPPORT CONTACTS:
   • PartsTech Platform: https://app.partstech.com
   • API Documentation: https://api-docs.partstech.com
   • Technical Support: Available through platform

🎯 SUCCESS CRITERIA:
   • HTTP 200 response from /oauth/access endpoint
   • Valid JWT access token received
   • Ability to create quotes via /punchout/quote/create
   • Parts search functionality working

"""
        print(instructions)
    
    def test_usa_connection(self) -> Dict[str, Any]:
        """Test PartsTech API connection from USA location"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'location_test': 'USA',
            'base_connectivity': {},
            'authentication': {},
            'endpoints': {},
            'success': False,
            'issues_found': []
        }
        
        print("🧪 TESTING PARTSTECH API FROM USA LOCATION")
        print("=" * 50)
        
        # Test 1: Basic connectivity
        print("1️⃣  Testing basic connectivity...")
        try:
            response = requests.get(self.base_url, timeout=10)
            results['base_connectivity'] = {
                'status_code': response.status_code,
                'reachable': True,
                'cloudfront_blocked': 'cloudfront' in response.text.lower() and response.status_code == 403
            }
            
            if results['base_connectivity']['cloudfront_blocked']:
                print("   ❌ Still blocked by CloudFront - verify USA location")
                results['issues_found'].append("CloudFront geographic block still active")
            else:
                print(f"   ✅ Connected successfully ({response.status_code})")
                
        except Exception as e:
            print(f"   ❌ Connection failed: {str(e)}")
            results['base_connectivity'] = {'reachable': False, 'error': str(e)}
            results['issues_found'].append(f"Connection failed: {str(e)}")
        
        # Test 2: JWT Authentication  
        if results['base_connectivity'].get('reachable'):
            print("2️⃣  Testing JWT authentication...")
            auth_result = self.test_jwt_authentication()
            results['authentication'] = auth_result
            
            if auth_result.get('success'):
                print("   ✅ JWT authentication successful")
                results['success'] = True
            else:
                print(f"   ❌ Authentication failed: {auth_result.get('error')}")
                results['issues_found'].append(f"Auth failed: {auth_result.get('error')}")
        
        # Test 3: API endpoints
        if results['authentication'].get('success'):
            print("3️⃣  Testing API endpoints...")
            endpoint_results = self.test_api_endpoints(results['authentication']['access_token'])
            results['endpoints'] = endpoint_results
            
            working_endpoints = [ep for ep, data in endpoint_results.items() if data.get('working')]
            print(f"   ✅ {len(working_endpoints)} endpoints accessible")
        
        return results
    
    def test_jwt_authentication(self) -> Dict[str, Any]:
        """Test JWT authentication specifically"""
        auth_data = {
            "accessType": "user",
            "credentials": {
                "username": self.username,
                "apiKey": self.api_key
            }
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/oauth/access",
                json=auth_data,
                headers={'Content-Type': 'application/json'},
                timeout=15
            )
            
            if response.status_code == 200:
                token_data = response.json()
                return {
                    'success': True,
                    'access_token': token_data.get('accessToken'),
                    'response': token_data
                }
            else:
                return {
                    'success': False,
                    'status_code': response.status_code,
                    'error': response.text[:200]
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_api_endpoints(self, access_token: str) -> Dict[str, Any]:
        """Test key API endpoints with valid token"""
        endpoints = {
            '/punchout/quote/create': 'POST',
            '/search': 'GET', 
            '/vin': 'GET',
            '/parts': 'GET'
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        results = {}
        
        for endpoint, method in endpoints.items():
            try:
                url = self.base_url + endpoint
                
                if method == 'POST':
                    # Test POST with minimal data
                    test_data = {"test": True}
                    response = requests.post(url, json=test_data, headers=headers, timeout=10)
                else:
                    response = requests.get(url, headers=headers, timeout=10)
                
                results[endpoint] = {
                    'working': response.status_code in [200, 400, 422],  # 400/422 means endpoint exists
                    'status_code': response.status_code,
                    'needs_parameters': response.status_code in [400, 422]
                }
                
            except Exception as e:
                results[endpoint] = {
                    'working': False,
                    'error': str(e)
                }
        
        return results
    
    def create_production_config(self, test_results: Dict[str, Any]) -> str:
        """Create production configuration based on test results"""
        config_template = f'''
# PARTSTECH API PRODUCTION CONFIGURATION
# Generated: {datetime.now().isoformat()}
# Test Results: {"SUCCESS" if test_results.get('success') else "FAILED"}

PARTSTECH_USERNAME = "{self.username}"
PARTSTECH_API_KEY = "{self.api_key}"
PARTSTECH_BASE_URL = "{self.base_url}"

# Authentication Configuration
AUTH_ENDPOINT = "/oauth/access"
TOKEN_EXPIRY_MINUTES = 60

# Working Endpoints (based on test)
'''
        
        if test_results.get('endpoints'):
            working_endpoints = [ep for ep, data in test_results['endpoints'].items() if data.get('working')]
            config_template += "WORKING_ENDPOINTS = [\n"
            for endpoint in working_endpoints:
                config_template += f'    "{endpoint}",\n'
            config_template += "]\n"
        
        config_template += f'''
# Connection Status
CONNECTION_VERIFIED = {test_results.get('success', False)}
FALLBACK_MODE = {not test_results.get('success', True)}

# Issues Found (if any)
ISSUES = {test_results.get('issues_found', [])}
'''
        
        return config_template

def main():
    """Main execution function"""
    setup = USAPartnerSetup()
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Run connection test
        test_results = setup.test_usa_connection()
        
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        print(f"Overall Success: {'✅ YES' if test_results['success'] else '❌ NO'}")
        print(f"Issues Found: {len(test_results['issues_found'])}")
        
        for issue in test_results['issues_found']:
            print(f"  • {issue}")
        
        if test_results['success']:
            print("\n🎉 SUCCESS! PartsTech API is working from your USA location.")
            print("   You can now integrate this into your production system.")
        else:
            print("\n⚠️  ISSUES DETECTED. Please review the problems above.")
            print("   Consider contacting PartsTech support for assistance.")
        
        # Save configuration
        config = setup.create_production_config(test_results)
        with open('partstech_production_config.txt', 'w') as f:
            f.write(config)
        print(f"\n💾 Configuration saved to: partstech_production_config.txt")
        
        # Save test results
        with open('usa_test_results.json', 'w') as f:
            json.dump(test_results, f, indent=2)
        print(f"📋 Test results saved to: usa_test_results.json")
        
    else:
        # Show setup instructions
        setup.display_setup_instructions()
        print("\nTo run the connection test, use:")
        print("python3 usa_partner_setup_guide.py --test")

if __name__ == "__main__":
    main()