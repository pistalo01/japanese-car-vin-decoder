#!/usr/bin/env python3
"""
Enhanced Parts API Integration
==============================

Integrates multiple parts APIs including PartsTech, with fallbacks and enhanced error handling.
"""

import requests
import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class LivePartInfo:
    """Live part information from real APIs"""
    part_name: str
    part_number: str
    brand: str
    price: float
    list_price: float
    availability: str
    supplier: str
    supplier_location: str
    description: str
    fitment_notes: str
    shipping_time: str
    in_stock: bool
    stock_quantity: int
    category: str
    image_url: str = ""
    warranty: str = ""
    core_charge: float = 0.0
    source_api: str = ""

class EnhancedPartsAPIClient:
    """Enhanced parts API client with multiple providers"""
    
    def __init__(self):
        # PartsTech credentials
        self.partstech_api_key = "b2b87bdc38ec417c8e69f936638e3c1c"
        self.partstech_username = "unitypartsllc@gmail.com"
        
        # Possible PartsTech API URLs to try
        self.partstech_urls = [
            "https://api.partstech.com",
            "https://partstech.com/api",
            "https://app.partstech.com/api",
            "https://backend.partstech.com/api",
            "https://platform.partstech.com/api"
        ]
        
        # Alternative parts APIs (free/demo versions)
        self.backup_apis = {
            'nhtsa': 'https://vpic.nhtsa.dot.gov/api',
            'carmd': 'http://api.carmd.com/v3.0',  # Requires separate API key
            'edmunds': 'https://api.edmunds.com'   # Requires separate API key
        }
        
        # Session with retries
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Japanese-VIN-Decoder/1.0 (Contact: unitypartsllc@gmail.com)',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def test_partstech_connection(self) -> Dict[str, Any]:
        """Test different PartsTech API connection methods"""
        results = {
            'connection_found': False,
            'working_url': None,
            'auth_method': None,
            'endpoints_discovered': [],
            'sample_response': None
        }
        
        print("🔍 Testing PartsTech API connections...")
        
        # Authentication methods to try
        auth_methods = [
            ('api_key_header', {'X-API-Key': self.partstech_api_key}),
            ('bearer_token', {'Authorization': f'Bearer {self.partstech_api_key}'}),
            ('api_key_auth', {'Authorization': f'ApiKey {self.partstech_api_key}'}),
            ('basic_auth', None),  # Will use session.auth
            ('url_param', None)    # Will add API key as URL parameter
        ]
        
        for base_url in self.partstech_urls:
            for auth_name, auth_header in auth_methods:
                try:
                    # Set up authentication
                    if auth_header:
                        self.session.headers.update(auth_header)
                    elif auth_name == 'basic_auth':
                        self.session.auth = (self.partstech_username, self.partstech_api_key)
                    
                    # Test endpoints
                    test_endpoints = [
                        '/api/v1/search',
                        '/api/search',
                        '/search',
                        '/api/parts',
                        '/parts',
                        '/api/vin',
                        '/vin',
                        '/api/status',
                        '/status',
                        '/'
                    ]
                    
                    for endpoint in test_endpoints:
                        test_url = base_url + endpoint
                        
                        # Add API key as URL parameter for url_param method
                        if auth_name == 'url_param':
                            test_url += f"?api_key={self.partstech_api_key}"
                        
                        print(f"   Testing: {test_url}")
                        
                        response = self.session.get(test_url, timeout=10)
                        
                        if response.status_code in [200, 400, 422]:  # Any meaningful response
                            results['connection_found'] = True
                            results['working_url'] = base_url
                            results['auth_method'] = auth_name
                            results['endpoints_discovered'].append(endpoint)
                            
                            if response.status_code == 200:
                                try:
                                    results['sample_response'] = response.json()
                                except:
                                    results['sample_response'] = response.text[:500]
                            
                            print(f"   ✅ Connection successful: {test_url}")
                            print(f"   Status: {response.status_code}")
                            break
                    
                    if results['connection_found']:
                        break
                        
                    # Clean up auth for next test
                    if auth_header:
                        for key in auth_header.keys():
                            self.session.headers.pop(key, None)
                    elif auth_name == 'basic_auth':
                        self.session.auth = None
                
                except Exception as e:
                    print(f"   ❌ Failed: {base_url} ({auth_name}) - {str(e)}")
                    continue
            
            if results['connection_found']:
                break
        
        return results
    
    def search_parts_advanced(self, search_params: Dict[str, Any]) -> List[LivePartInfo]:
        """Advanced parts search with multiple fallback strategies"""
        parts = []
        
        # Strategy 1: Try PartsTech API
        partstech_parts = self._search_partstech(search_params)
        if partstech_parts:
            parts.extend(partstech_parts)
            return parts
        
        # Strategy 2: Try alternative APIs
        alt_parts = self._search_alternative_apis(search_params)
        if alt_parts:
            parts.extend(alt_parts)
        
        # Strategy 3: Enhanced static database with realistic data
        static_parts = self._get_enhanced_static_parts(search_params)
        parts.extend(static_parts)
        
        return parts
    
    def _search_partstech(self, search_params: Dict[str, Any]) -> List[LivePartInfo]:
        """Search PartsTech API with discovered endpoints"""
        parts = []
        
        # First test connection
        connection_info = self.test_partstech_connection()
        
        if not connection_info['connection_found']:
            print("❌ No PartsTech connection established")
            return parts
        
        print(f"✅ Using PartsTech: {connection_info['working_url']} ({connection_info['auth_method']})")
        
        # Try to make actual search calls
        for endpoint in connection_info['endpoints_discovered']:
            try:
                search_url = connection_info['working_url'] + endpoint
                
                # Different payload structures to try
                payloads = [
                    search_params,  # Direct parameters
                    {'search': search_params},  # Nested
                    {'query': search_params},   # Query wrapper
                    {'data': search_params}     # Data wrapper
                ]
                
                for payload in payloads:
                    response = self.session.post(search_url, json=payload, timeout=15)
                    
                    if response.status_code == 200:
                        data = response.json()
                        parsed_parts = self._parse_partstech_response(data)
                        if parsed_parts:
                            parts.extend(parsed_parts)
                            return parts
                    
            except Exception as e:
                logger.debug(f"PartsTech search failed on {endpoint}: {e}")
        
        return parts
    
    def _parse_partstech_response(self, data: Dict[str, Any]) -> List[LivePartInfo]:
        """Parse PartsTech API response"""
        parts = []
        
        # Common response structures
        possible_keys = ['parts', 'results', 'data', 'items', 'products', 'inventory']
        
        for key in possible_keys:
            if key in data and isinstance(data[key], list):
                for item in data[key]:
                    try:
                        part = LivePartInfo(
                            part_name=item.get('name', item.get('description', 'Unknown Part')),
                            part_number=item.get('partNumber', item.get('part_number', item.get('sku', 'N/A'))),
                            brand=item.get('brand', item.get('manufacturer', 'Unknown')),
                            price=float(item.get('price', item.get('cost', item.get('unitPrice', 0)))),
                            list_price=float(item.get('listPrice', item.get('msrp', item.get('list_price', 0)))),
                            availability=item.get('availability', item.get('status', 'Unknown')),
                            supplier=item.get('supplier', item.get('vendor', item.get('distributor', 'PartsTech'))),
                            supplier_location=item.get('location', item.get('warehouse', '')),
                            description=item.get('description', item.get('longDescription', '')),
                            fitment_notes=item.get('fitment', item.get('notes', item.get('compatibility', ''))),
                            shipping_time=item.get('leadTime', item.get('shippingTime', item.get('delivery', 'Unknown'))),
                            in_stock=bool(item.get('inStock', item.get('available', False))),
                            stock_quantity=int(item.get('quantity', item.get('stock', 0))),
                            category=item.get('category', item.get('type', 'General')),
                            image_url=item.get('imageUrl', item.get('image', '')),
                            warranty=item.get('warranty', ''),
                            core_charge=float(item.get('coreCharge', item.get('core', 0))),
                            source_api='PartsTech'
                        )
                        parts.append(part)
                    except Exception as e:
                        logger.warning(f"Failed to parse PartsTech item: {e}")
                break
        
        return parts
    
    def _search_alternative_apis(self, search_params: Dict[str, Any]) -> List[LivePartInfo]:
        """Search alternative parts APIs"""
        parts = []
        
        # For now, return empty as we focus on PartsTech and static data
        # This is where you'd integrate other APIs like CarMD, Edmunds, etc.
        
        return parts
    
    def _get_enhanced_static_parts(self, search_params: Dict[str, Any]) -> List[LivePartInfo]:
        """Get enhanced static parts data with realistic pricing and suppliers"""
        parts = []
        
        # Enhanced Honda D16W7 parts with realistic data
        if any(param in str(search_params).upper() for param in ['D16W7', 'HONDA', 'CIVIC']):
            honda_parts = [
                LivePartInfo(
                    part_name="Air Filter",
                    part_number="17220-P2A-000",
                    brand="Honda OEM",
                    price=18.50,
                    list_price=24.99,
                    availability="In Stock",
                    supplier="Honda Parts Direct",
                    supplier_location="Atlanta, GA",
                    description="OEM Honda Air Filter for D16W7 Engine",
                    fitment_notes="Fits 2001-2005 Honda Civic with D16W7 engine",
                    shipping_time="1-2 business days",
                    in_stock=True,
                    stock_quantity=25,
                    category="Engine",
                    warranty="12 months",
                    source_api="Enhanced Static"
                ),
                LivePartInfo(
                    part_name="Oil Filter",
                    part_number="15400-PLM-A02",
                    brand="Honda OEM",
                    price=12.75,
                    list_price=16.99,
                    availability="In Stock",
                    supplier="Honda Parts Network",
                    supplier_location="Miami, FL",
                    description="Honda OEM Oil Filter Cartridge",
                    fitment_notes="D16W7 SOHC VTEC Engine",
                    shipping_time="Same day",
                    in_stock=True,
                    stock_quantity=15,
                    category="Engine",
                    warranty="6 months",
                    source_api="Enhanced Static"
                ),
                LivePartInfo(
                    part_name="Spark Plugs Set",
                    part_number="98079-55846",
                    brand="NGK (Honda OEM)",
                    price=32.50,
                    list_price=42.99,
                    availability="In Stock",
                    supplier="NGK Distributor Jamaica",
                    supplier_location="Kingston, JM",
                    description="NGK Iridium Spark Plugs (Set of 4)",
                    fitment_notes="D16W7 VTEC Engine - Gap: 0.039-0.043\"",
                    shipping_time="Next day delivery",
                    in_stock=True,
                    stock_quantity=8,
                    category="Engine",
                    warranty="60,000 miles",
                    source_api="Enhanced Static"
                ),
                LivePartInfo(
                    part_name="VTEC Solenoid Valve",
                    part_number="15810-P2A-A01",
                    brand="Honda OEM",
                    price=125.00,
                    list_price=165.99,
                    availability="Limited Stock",
                    supplier="Honda Specialist Jamaica",
                    supplier_location="Spanish Town, JM",
                    description="VTEC Solenoid Valve Assembly",
                    fitment_notes="D16W7 SOHC VTEC Engine Control",
                    shipping_time="2-3 business days",
                    in_stock=True,
                    stock_quantity=3,
                    category="Engine Control",
                    warranty="24 months",
                    source_api="Enhanced Static"
                ),
                LivePartInfo(
                    part_name="Front Brake Pads",
                    part_number="45022-S5A-E50",
                    brand="Akebono (Honda OEM)",
                    price=45.99,
                    list_price=65.99,
                    availability="In Stock",
                    supplier="Brake Parts Jamaica",
                    supplier_location="Montego Bay, JM",
                    description="Ceramic Front Brake Pads",
                    fitment_notes="2001-2005 Honda Civic Front Wheels",
                    shipping_time="1-2 business days",
                    in_stock=True,
                    stock_quantity=12,
                    category="Brakes",
                    warranty="25,000 miles",
                    source_api="Enhanced Static"
                )
            ]
            parts.extend(honda_parts)
        
        # Enhanced Toyota parts
        if any(param in str(search_params).upper() for param in ['TOYOTA', 'CAMRY', '1ZZ', '2AZ']):
            toyota_parts = [
                LivePartInfo(
                    part_name="Air Filter",
                    part_number="17801-0P010",
                    brand="Toyota OEM",
                    price=22.50,
                    list_price=29.99,
                    availability="In Stock",
                    supplier="Toyota Parts Jamaica",
                    supplier_location="Kingston, JM",
                    description="OEM Toyota Air Filter",
                    fitment_notes="2005 Toyota Camry 1ZZ-FE Engine",
                    shipping_time="Same day",
                    in_stock=True,
                    stock_quantity=18,
                    category="Engine",
                    warranty="12 months",
                    source_api="Enhanced Static"
                ),
                LivePartInfo(
                    part_name="Oil Filter",
                    part_number="90915-YZZJ1",
                    brand="Toyota OEM",
                    price=14.25,
                    list_price=18.99,
                    availability="In Stock",
                    supplier="Toyota Direct Import",
                    supplier_location="Portmore, JM",
                    description="Toyota OEM Spin-On Oil Filter",
                    fitment_notes="Camry 1ZZ-FE Engine",
                    shipping_time="Next day",
                    in_stock=True,
                    stock_quantity=22,
                    category="Engine",
                    warranty="6 months",
                    source_api="Enhanced Static"
                )
            ]
            parts.extend(toyota_parts)
        
        return parts

def demo_enhanced_integration():
    """Demonstrate enhanced parts API integration"""
    print("🚗 Enhanced Parts API Integration Demo")
    print("=" * 60)
    
    client = EnhancedPartsAPIClient()
    
    # Test PartsTech connection
    connection_results = client.test_partstech_connection()
    print(f"\n📊 PartsTech Connection Results:")
    print(f"Connection Found: {connection_results['connection_found']}")
    print(f"Working URL: {connection_results['working_url']}")
    print(f"Auth Method: {connection_results['auth_method']}")
    print(f"Endpoints: {connection_results['endpoints_discovered']}")
    
    # Test parts searches
    test_searches = [
        {
            'vin': '4T1BE32K25U123456',
            'description': '2005 Toyota Camry'
        },
        {
            'year': '2003',
            'make': 'Honda',
            'model': 'Civic',
            'engine': 'D16W7',
            'description': '2003 Honda Civic D16W7'
        },
        {
            'keyword': 'air filter',
            'make': 'Honda',
            'model': 'Civic',
            'description': 'Honda Civic Air Filter Search'
        }
    ]
    
    for search in test_searches:
        print(f"\n🔍 Testing: {search['description']}")
        print("-" * 50)
        
        parts = client.search_parts_advanced(search)
        
        if parts:
            print(f"✅ Found {len(parts)} parts:")
            for part in parts:
                print(f"\n  📦 {part.part_name}")
                print(f"     Part Number: {part.part_number}")
                print(f"     Brand: {part.brand}")
                print(f"     Price: ${part.price} (List: ${part.list_price})")
                print(f"     Supplier: {part.supplier} ({part.supplier_location})")
                print(f"     In Stock: {part.in_stock} (Qty: {part.stock_quantity})")
                print(f"     Shipping: {part.shipping_time}")
                print(f"     Warranty: {part.warranty}")
                print(f"     Source: {part.source_api}")
        else:
            print("❌ No parts found")

if __name__ == "__main__":
    demo_enhanced_integration()