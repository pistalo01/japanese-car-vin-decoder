#!/usr/bin/env python3
"""
PartsTech API Integration for Real Parts Data
============================================

Integrates with PartsTech API to provide real parts inventory, pricing, and availability.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PartsSearch:
    """Parts search parameters"""
    vin: str = ""
    year: str = ""
    make: str = ""
    model: str = ""
    engine: str = ""
    part_type: str = ""
    search_query: str = ""

@dataclass
class RealPartInfo:
    """Real part information from PartsTech"""
    part_name: str
    part_number: str
    brand: str
    price: float
    availability: str
    supplier: str
    description: str
    fitment_notes: str
    shipping_time: str
    location: str
    in_stock: bool
    category: str

class PartsTeachAPIClient:
    """PartsTech API client for real parts lookup"""
    
    def __init__(self):
        # PartsTech API credentials
        self.api_key = "b2b87bdc38ec417c8e69f936638e3c1c"
        self.username = "unitypartsllc@gmail.com"
        
        # API endpoints (to be discovered)
        self.base_url = "https://api.partstech.com"  # Assumed base URL
        
        # Common API endpoint patterns to test
        self.potential_endpoints = [
            "/api/v1/search",
            "/api/search",
            "/v1/parts/search",
            "/search/parts",
            "/api/v1/vin-lookup",
            "/vin-lookup",
            "/api/v1/inventory",
            "/inventory",
            "/api/parts",
            "/parts"
        ]
        
        # Session for connection pooling
        self.session = requests.Session()
        
        # Set up authentication headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'User-Agent': 'Japanese-VIN-Decoder/1.0'
        })
        
    def authenticate(self) -> bool:
        """Authenticate with PartsTech API"""
        auth_methods = [
            # Method 1: API Key in header
            {'X-API-Key': self.api_key},
            {'Authorization': f'Bearer {self.api_key}'},
            {'Authorization': f'ApiKey {self.api_key}'},
            
            # Method 2: Basic Auth
            None  # Will try basic auth separately
        ]
        
        for auth_header in auth_methods:
            if auth_header:
                self.session.headers.update(auth_header)
            
            # Test authentication with a simple endpoint
            if self._test_auth():
                logger.info(f"✅ Authentication successful with method: {auth_header}")
                return True
            
            # Remove auth header for next test
            if auth_header:
                for key in auth_header.keys():
                    self.session.headers.pop(key, None)
        
        # Try Basic Auth
        try:
            self.session.auth = (self.username, self.api_key)
            if self._test_auth():
                logger.info("✅ Authentication successful with Basic Auth")
                return True
        except Exception as e:
            logger.error(f"Basic auth failed: {e}")
        
        logger.error("❌ All authentication methods failed")
        return False
    
    def _test_auth(self) -> bool:
        """Test authentication by trying common endpoints"""
        test_endpoints = [
            "/api/v1/test",
            "/test",
            "/ping",
            "/health",
            "/api/status",
            "/status"
        ]
        
        for endpoint in test_endpoints:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                if response.status_code in [200, 401, 403]:  # Any response indicates connection
                    return response.status_code == 200
            except Exception as e:
                logger.debug(f"Test endpoint {endpoint} failed: {e}")
        
        return False
    
    def discover_api_structure(self) -> Dict[str, Any]:
        """Discover API endpoints and structure"""
        discoveries = {
            'working_endpoints': [],
            'authentication_method': None,
            'example_responses': {},
            'api_structure': {}
        }
        
        logger.info("🔍 Discovering PartsTech API structure...")
        
        # Try authentication
        if self.authenticate():
            discoveries['authentication_method'] = 'authenticated'
        
        # Test potential endpoints
        for endpoint in self.potential_endpoints:
            try:
                # Try GET request
                response = self.session.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    discoveries['working_endpoints'].append(endpoint)
                    discoveries['example_responses'][endpoint] = {
                        'status_code': response.status_code,
                        'response': response.json() if 'json' in response.headers.get('content-type', '') else response.text[:500]
                    }
                    logger.info(f"✅ Found working endpoint: {endpoint}")
                
                elif response.status_code in [400, 422]:  # Bad request but endpoint exists
                    discoveries['working_endpoints'].append(f"{endpoint} (needs parameters)")
                    logger.info(f"📋 Found endpoint requiring parameters: {endpoint}")
                
            except Exception as e:
                logger.debug(f"Endpoint {endpoint} failed: {e}")
        
        return discoveries
    
    def search_parts_by_vin(self, vin: str, part_category: str = None) -> List[RealPartInfo]:
        """Search for parts using VIN"""
        search_data = {
            'vin': vin,
            'category': part_category
        }
        
        return self._search_parts(search_data)
    
    def search_parts_by_vehicle(self, year: str, make: str, model: str, engine: str = "", part_category: str = None) -> List[RealPartInfo]:
        """Search for parts by vehicle information"""
        search_data = {
            'year': year,
            'make': make,
            'model': model,
            'engine': engine,
            'category': part_category
        }
        
        return self._search_parts(search_data)
    
    def search_parts_by_keyword(self, keyword: str, vehicle_info: Dict[str, str] = None) -> List[RealPartInfo]:
        """Search parts by keyword with optional vehicle context"""
        search_data = {
            'query': keyword,
            'vehicle': vehicle_info or {}
        }
        
        return self._search_parts(search_data)
    
    def _search_parts(self, search_data: Dict[str, Any]) -> List[RealPartInfo]:
        """Internal method to search for parts"""
        parts = []
        
        for endpoint in self.potential_endpoints:
            try:
                # Try POST request with search data
                response = self.session.post(
                    f"{self.base_url}{endpoint}",
                    json=search_data,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    parts.extend(self._parse_parts_response(data))
                    break
                    
            except Exception as e:
                logger.debug(f"Search attempt on {endpoint} failed: {e}")
        
        return parts
    
    def _parse_parts_response(self, response_data: Dict[str, Any]) -> List[RealPartInfo]:
        """Parse PartsTech API response into RealPartInfo objects"""
        parts = []
        
        # Common response structures to handle
        parts_keys = ['parts', 'results', 'data', 'items', 'products']
        
        for key in parts_keys:
            if key in response_data:
                parts_data = response_data[key]
                if isinstance(parts_data, list):
                    for part_data in parts_data:
                        try:
                            part = RealPartInfo(
                                part_name=part_data.get('name', part_data.get('part_name', 'Unknown Part')),
                                part_number=part_data.get('part_number', part_data.get('partNumber', 'N/A')),
                                brand=part_data.get('brand', part_data.get('manufacturer', 'Unknown')),
                                price=float(part_data.get('price', part_data.get('cost', 0))),
                                availability=part_data.get('availability', 'Unknown'),
                                supplier=part_data.get('supplier', part_data.get('vendor', 'Unknown')),
                                description=part_data.get('description', ''),
                                fitment_notes=part_data.get('fitment', part_data.get('notes', '')),
                                shipping_time=part_data.get('shipping_time', part_data.get('lead_time', 'Unknown')),
                                location=part_data.get('location', ''),
                                in_stock=part_data.get('in_stock', part_data.get('available', False)),
                                category=part_data.get('category', part_data.get('type', 'General'))
                            )
                            parts.append(part)
                        except Exception as e:
                            logger.warning(f"Failed to parse part data: {e}")
                
                break
        
        return parts

def demo_partstech_integration():
    """Demonstrate PartsTech API integration"""
    print("🔧 PartsTech API Integration Demo")
    print("=" * 50)
    
    client = PartsTeachAPIClient()
    
    # Discover API structure
    discoveries = client.discover_api_structure()
    
    print(f"\n📊 API Discovery Results:")
    print(f"Working endpoints: {len(discoveries['working_endpoints'])}")
    for endpoint in discoveries['working_endpoints']:
        print(f"  ✅ {endpoint}")
    
    print(f"Authentication: {discoveries['authentication_method']}")
    
    # Test parts search
    test_cases = [
        {"vin": "4T1BE32K25U123456", "description": "2005 Toyota Camry"},
        {"vin": "1HGEM21503L123456", "description": "2003 Honda Civic"},
        {"year": "2003", "make": "Honda", "model": "Civic", "engine": "D16W7", "description": "Honda Civic by vehicle info"}
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['description']}")
        print("-" * 40)
        
        if 'vin' in test_case and len(test_case.get('vin', '')) == 17:
            parts = client.search_parts_by_vin(test_case['vin'], 'engine')
        else:
            parts = client.search_parts_by_vehicle(
                test_case.get('year', ''),
                test_case.get('make', ''),
                test_case.get('model', ''),
                test_case.get('engine', ''),
                'engine'
            )
        
        if parts:
            print(f"✅ Found {len(parts)} parts:")
            for part in parts[:3]:  # Show first 3 parts
                print(f"  • {part.part_name} ({part.part_number}) - ${part.price}")
                print(f"    Brand: {part.brand}, Supplier: {part.supplier}")
                print(f"    Available: {part.in_stock}, Location: {part.location}")
        else:
            print("❌ No parts found or API not accessible")
    
    # Test keyword search
    print(f"\n🔍 Testing keyword search: 'air filter'")
    print("-" * 40)
    
    keyword_parts = client.search_parts_by_keyword(
        'air filter', 
        {'year': '2003', 'make': 'Honda', 'model': 'Civic'}
    )
    
    if keyword_parts:
        print(f"✅ Found {len(keyword_parts)} air filters")
        for part in keyword_parts[:3]:
            print(f"  • {part.part_name} - ${part.price} ({part.supplier})")
    else:
        print("❌ No keyword search results")

if __name__ == "__main__":
    demo_partstech_integration()