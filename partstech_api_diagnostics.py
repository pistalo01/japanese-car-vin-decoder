#!/usr/bin/env python3
"""
PartsTech API Connection Diagnostics
===================================

Advanced diagnostics to identify and fix connection issues with PartsTech API
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

class PartsTechDiagnostics:
    def __init__(self):
        self.username = "unitypartsllc@gmail.com"
        self.api_key = "b2b87bdc38ec417c8e69f936638e3c1c"
        
        # Multiple possible API endpoints based on documentation analysis
        self.api_endpoints = [
            "https://api.partstech.com",
            "https://api.beta.partstech.com",  # Beta server from docs
            "https://platform.partstech.com/api",
            "https://app.partstech.com/api", 
            "https://backend.partstech.com/api"
        ]
        
        self.session = requests.Session()
        self.session.timeout = 30
        
    def run_comprehensive_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive diagnostics on PartsTech API"""
        results = {
            'timestamp': datetime.now().isoformat(),
            'basic_connectivity': {},
            'authentication_tests': {},
            'endpoint_discovery': {},
            'recommended_actions': []
        }
        
        print("🔍 PartsTech API Comprehensive Diagnostics")
        print("=" * 50)
        
        # Test 1: Basic connectivity
        print("\n1️⃣  Testing Basic Connectivity...")
        results['basic_connectivity'] = self.test_basic_connectivity()
        
        # Test 2: Authentication methods
        print("\n2️⃣  Testing Authentication Methods...")
        results['authentication_tests'] = self.test_authentication_methods()
        
        # Test 3: Alternative endpoints
        print("\n3️⃣  Testing Alternative Endpoints...")  
        results['endpoint_discovery'] = self.discover_working_endpoints()
        
        # Generate recommendations
        results['recommended_actions'] = self.generate_recommendations(results)
        
        return results
    
    def test_basic_connectivity(self) -> Dict[str, Any]:
        """Test basic network connectivity to PartsTech"""
        connectivity_results = {}
        
        for endpoint in self.api_endpoints:
            print(f"   Testing: {endpoint}")
            result = {
                'reachable': False,
                'status_code': None,
                'response_time_ms': None,
                'error': None,
                'headers': {},
                'cloudfront_blocked': False,
                'ip_restriction': False
            }
            
            try:
                start_time = time.time()
                response = self.session.get(endpoint, timeout=10)
                result['response_time_ms'] = int((time.time() - start_time) * 1000)
                result['status_code'] = response.status_code
                result['reachable'] = True
                result['headers'] = dict(response.headers)
                
                # Check for CloudFront blocks
                if 'cloudfront' in response.text.lower() and response.status_code == 403:
                    result['cloudfront_blocked'] = True
                    result['error'] = 'CloudFront 403 - Possible geographic restriction'
                    print(f"     ❌ CloudFront blocked: {endpoint}")
                elif response.status_code == 403:
                    result['ip_restriction'] = True
                    result['error'] = '403 Forbidden - Possible IP whitelist required'
                    print(f"     ⚠️  IP restricted: {endpoint}")
                else:
                    print(f"     ✅ Connected: {endpoint} ({response.status_code})")
                    
            except requests.exceptions.ConnectionError as e:
                result['error'] = f'Connection failed: {str(e)}'
                print(f"     ❌ Connection failed: {endpoint}")
            except requests.exceptions.Timeout as e:
                result['error'] = f'Timeout: {str(e)}'
                print(f"     ⏱️  Timeout: {endpoint}")
            except Exception as e:
                result['error'] = f'Unexpected error: {str(e)}'
                print(f"     ❌ Error: {endpoint} - {str(e)}")
            
            connectivity_results[endpoint] = result
            
        return connectivity_results
    
    def test_authentication_methods(self) -> Dict[str, Any]:
        """Test different authentication methods"""
        auth_results = {}
        
        # Get a working endpoint first
        working_endpoint = self.get_best_endpoint()
        if not working_endpoint:
            return {'error': 'No reachable endpoints found'}
        
        auth_methods = {
            'jwt_oauth': {
                'description': 'JWT OAuth (Official Method)',
                'endpoint': '/oauth/access',
                'method': 'POST',
                'payload': {
                    "accessType": "user",
                    "credentials": {
                        "username": self.username,
                        "apiKey": self.api_key
                    }
                }
            },
            'basic_auth': {
                'description': 'Basic Authentication',
                'endpoint': '/oauth/access',
                'method': 'POST', 
                'auth': (self.username, self.api_key)
            },
            'api_key_header': {
                'description': 'API Key in Header',
                'endpoint': '/oauth/access',
                'method': 'POST',
                'headers': {'X-API-Key': self.api_key}
            },
            'bearer_token': {
                'description': 'Bearer Token',
                'endpoint': '/oauth/access', 
                'method': 'POST',
                'headers': {'Authorization': f'Bearer {self.api_key}'}
            }
        }
        
        for method_name, method_config in auth_methods.items():
            print(f"   Testing: {method_config['description']}")
            result = self.test_auth_method(working_endpoint, method_config)
            auth_results[method_name] = result
            
            if result.get('success'):
                print(f"     ✅ Success: {method_name}")
                return auth_results  # Return on first success
            else:
                print(f"     ❌ Failed: {method_name} - {result.get('error', 'Unknown error')}")
        
        return auth_results
    
    def test_auth_method(self, base_url: str, method_config: Dict[str, Any]) -> Dict[str, Any]:
        """Test a specific authentication method"""
        result = {
            'success': False,
            'status_code': None,
            'response': None,
            'error': None,
            'access_token': None
        }
        
        try:
            url = base_url + method_config['endpoint']
            
            # Prepare request parameters
            kwargs = {
                'url': url,
                'timeout': 15,
                'headers': {'Content-Type': 'application/json'}
            }
            
            # Add authentication
            if 'payload' in method_config:
                kwargs['json'] = method_config['payload']
            if 'auth' in method_config:
                kwargs['auth'] = method_config['auth']
            if 'headers' in method_config:
                kwargs['headers'].update(method_config['headers'])
            
            # Make request
            if method_config['method'].upper() == 'POST':
                response = self.session.post(**kwargs)
            else:
                response = self.session.get(**kwargs)
            
            result['status_code'] = response.status_code
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    result['response'] = response_data
                    result['access_token'] = response_data.get('accessToken')
                    result['success'] = True
                except:
                    result['response'] = response.text
                    result['success'] = True  # 200 is still success
            else:
                result['error'] = f"HTTP {response.status_code}: {response.text[:200]}"
                
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def discover_working_endpoints(self) -> Dict[str, Any]:
        """Discover working API endpoints"""
        discovery_results = {}
        
        working_base = self.get_best_endpoint()
        if not working_base:
            return {'error': 'No working base endpoint found'}
        
        # Common API paths to test
        test_paths = [
            '/oauth/access',
            '/punchout/quote/create', 
            '/search',
            '/api/search',
            '/vin',
            '/api/vin',
            '/parts',
            '/api/parts',
            '/status',
            '/health',
            '/ping'
        ]
        
        for path in test_paths:
            print(f"   Testing endpoint: {path}")
            result = self.test_endpoint(working_base + path)
            discovery_results[path] = result
            
            if result['accessible']:
                print(f"     ✅ Accessible: {path} ({result['status_code']})")
            elif result['status_code'] in [400, 401, 422]:
                print(f"     📋 Needs auth/params: {path} ({result['status_code']})")
            else:
                print(f"     ❌ Failed: {path} ({result.get('status_code', 'No response')})")
        
        return discovery_results
    
    def test_endpoint(self, url: str) -> Dict[str, Any]:
        """Test if an endpoint is accessible"""
        result = {
            'accessible': False,
            'status_code': None,
            'needs_auth': False,
            'needs_params': False,
            'error': None
        }
        
        try:
            response = self.session.get(url, timeout=10)
            result['status_code'] = response.status_code
            
            if response.status_code == 200:
                result['accessible'] = True
            elif response.status_code == 401:
                result['needs_auth'] = True
            elif response.status_code in [400, 422]:
                result['needs_params'] = True
            
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def get_best_endpoint(self) -> Optional[str]:
        """Get the best working endpoint"""
        for endpoint in self.api_endpoints:
            try:
                response = self.session.get(endpoint, timeout=5)
                if response.status_code != 404:  # Any response except 404
                    return endpoint
            except:
                continue
        return None
    
    def generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on diagnostic results"""
        recommendations = []
        
        # Check connectivity issues
        connectivity = results.get('basic_connectivity', {})
        cloudfront_blocks = [url for url, data in connectivity.items() 
                           if data.get('cloudfront_blocked', False)]
        
        if cloudfront_blocks:
            recommendations.append(
                "🌍 GEOGRAPHIC RESTRICTION: PartsTech API is blocked by CloudFront. "
                "This typically means the API is geographically restricted. "
                "Recommendation: Have your USA partner test from their location, "
                "or contact PartsTech support to whitelist your IP/location."
            )
        
        # Check IP restrictions
        ip_blocks = [url for url, data in connectivity.items() 
                    if data.get('ip_restriction', False)]
        
        if ip_blocks:
            recommendations.append(
                "🔒 IP WHITELIST REQUIRED: Your IP address may need to be whitelisted. "
                "Contact PartsTech support with your IP address for whitelist approval."
            )
        
        # Check authentication
        auth_results = results.get('authentication_tests', {})
        if auth_results and not any(result.get('success', False) for result in auth_results.values()):
            recommendations.append(
                "🔐 AUTHENTICATION ISSUE: All authentication methods failed. "
                "Possible issues: 1) Account needs activation, 2) API credentials expired, "
                "3) Account suspended. Contact PartsTech support to verify account status."
            )
        
        # General recommendations
        if not recommendations:
            recommendations.append(
                "✅ API appears functional. If you're still having issues, "
                "try testing from your USA partner's location/network."
            )
        
        recommendations.append(
            "📞 SUPPORT CONTACT: PartsTech support can be reached through their platform "
            "at https://app.partstech.com or through their documentation portal."
        )
        
        return recommendations
    
    def create_working_config(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Create a working configuration based on diagnostic results"""
        config = {
            'recommended_endpoint': None,
            'working_auth_method': None,
            'fallback_mode': True,
            'connection_status': 'failed'
        }
        
        # Find working endpoint
        connectivity = results.get('basic_connectivity', {})
        for url, data in connectivity.items():
            if data.get('reachable') and not data.get('cloudfront_blocked'):
                config['recommended_endpoint'] = url
                break
        
        # Find working auth method
        auth_results = results.get('authentication_tests', {})
        for method, result in auth_results.items():
            if result.get('success'):
                config['working_auth_method'] = method
                config['connection_status'] = 'success'
                config['fallback_mode'] = False
                break
        
        return config

def main():
    """Run diagnostics and create configuration"""
    diagnostics = PartsTechDiagnostics()
    results = diagnostics.run_comprehensive_diagnostics()
    
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    # Print recommendations
    for i, recommendation in enumerate(results['recommended_actions'], 1):
        print(f"\n{i}. {recommendation}")
    
    # Create working configuration
    config = diagnostics.create_working_config(results)
    
    print(f"\n🔧 CONFIGURATION RECOMMENDATIONS:")
    print(f"Recommended Endpoint: {config['recommended_endpoint']}")
    print(f"Working Auth Method: {config['working_auth_method']}")
    print(f"Connection Status: {config['connection_status']}")
    print(f"Use Fallback Mode: {config['fallback_mode']}")
    
    # Save full results
    with open('partstech_diagnostics_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n💾 Full diagnostic results saved to: partstech_diagnostics_results.json")
    
    return results

if __name__ == "__main__":
    main()