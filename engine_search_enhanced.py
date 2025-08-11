#!/usr/bin/env python3
"""
Enhanced VIN Decoder with Engine Number Search Support
======================================================

Adds capability to search by engine codes (like D16W7) in addition to VINs.
"""

import requests
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging
from enhanced_vin_decoder import EnhancedVehicleInfo, VehicleSpecifications, PartInformation, MaintenanceSchedule

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class EngineInfo:
    """Engine-specific information"""
    engine_code: str
    displacement: str
    type_: str  # SOHC, DOHC, etc.
    fuel_system: str
    valves_per_cylinder: int
    compression_ratio: str
    max_power: str
    max_torque: str
    fuel_type: str
    common_vehicles: List[Dict[str, str]]  # [{"make": "Honda", "model": "Civic", "years": "1996-2000"}]

class EnhancedEngineVINDecoder:
    """Enhanced decoder supporting both VIN and engine number searches"""
    
    def __init__(self):
        self.nhtsa_base_url = "https://vpic.nhtsa.dot.gov/api"
        
        # Engine database with detailed information
        self.engine_database = {
            # Honda D-Series Engines
            'D16W7': EngineInfo(
                engine_code='D16W7',
                displacement='1.6L (1590cc)',
                type_='SOHC VTEC',
                fuel_system='PGM-FI Multipoint',
                valves_per_cylinder=4,
                compression_ratio='9.6:1',
                max_power='127 hp @ 6600 rpm',
                max_torque='107 lb-ft @ 5500 rpm',
                fuel_type='Gasoline',
                common_vehicles=[
                    {"make": "Honda", "model": "Civic", "years": "2001-2005"},
                    {"make": "Honda", "model": "Civic Si", "years": "2002-2005"}
                ]
            ),
            'D17A1': EngineInfo(
                engine_code='D17A1',
                displacement='1.7L (1668cc)',
                type_='SOHC VTEC',
                fuel_system='PGM-FI Multipoint',
                valves_per_cylinder=4,
                compression_ratio='9.5:1',
                max_power='115 hp @ 6100 rpm',
                max_torque='110 lb-ft @ 4500 rpm',
                fuel_type='Gasoline',
                common_vehicles=[
                    {"make": "Honda", "model": "Civic", "years": "2001-2005"},
                    {"make": "Honda", "model": "Civic Hybrid", "years": "2003-2005"}
                ]
            ),
            'D16Y8': EngineInfo(
                engine_code='D16Y8',
                displacement='1.6L (1590cc)',
                type_='SOHC VTEC',
                fuel_system='PGM-FI Multipoint',
                valves_per_cylinder=4,
                compression_ratio='9.6:1',
                max_power='127 hp @ 6600 rpm',
                max_torque='107 lb-ft @ 5500 rpm',
                fuel_type='Gasoline',
                common_vehicles=[
                    {"make": "Honda", "model": "Civic", "years": "1996-2000"},
                    {"make": "Honda", "model": "Civic Si", "years": "1999-2000"}
                ]
            ),
            # Toyota Engines (for comparison)
            '1ZZ-FE': EngineInfo(
                engine_code='1ZZ-FE',
                displacement='1.8L (1794cc)',
                type_='DOHC VVT-i',
                fuel_system='Electronic Fuel Injection',
                valves_per_cylinder=4,
                compression_ratio='10.0:1',
                max_power='130 hp @ 6400 rpm',
                max_torque='125 lb-ft @ 4200 rpm',
                fuel_type='Gasoline',
                common_vehicles=[
                    {"make": "Toyota", "model": "Corolla", "years": "2000-2008"},
                    {"make": "Toyota", "model": "Camry", "years": "2000-2008"}
                ]
            ),
            '2AZ-FE': EngineInfo(
                engine_code='2AZ-FE',
                displacement='2.4L (2362cc)',
                type_='DOHC VVT-i',
                fuel_system='Electronic Fuel Injection',
                valves_per_cylinder=4,
                compression_ratio='9.6:1',
                max_power='160 hp @ 5600 rpm',
                max_torque='162 lb-ft @ 4000 rpm',
                fuel_type='Gasoline',
                common_vehicles=[
                    {"make": "Toyota", "model": "Camry", "years": "2002-2011"},
                    {"make": "Toyota", "model": "RAV4", "years": "2006-2012"}
                ]
            )
        }
        
        # Enhanced parts database for Honda Civic with D16W7 engine
        self.engine_parts_database = {
            'D16W7': {
                'engine_parts': {
                    'air_filter': PartInformation(
                        part_name="Air Filter",
                        part_number="17220-P2A-000",
                        brand="Honda OEM",
                        price_range="$12-22",
                        compatibility_notes="Fits 2001-2005 Honda Civic with D16W7 engine",
                        specifications={"filter_type": "Paper", "dimensions": "7.8\" x 6.1\" x 1.2\""},
                        alternatives=["Fram CA10467", "K&N 33-2276", "Mann C 2275"],
                        maintenance_interval="Every 12,000 miles"
                    ),
                    'oil_filter': PartInformation(
                        part_name="Oil Filter",
                        part_number="15400-PLM-A02",
                        brand="Honda OEM",
                        price_range="$6-12",
                        compatibility_notes="Fits Honda D16W7 engine",
                        specifications={"filter_type": "Cartridge", "thread_size": "M20 x 1.5"},
                        alternatives=["Fram PH3980", "Mobil 1 M1-110", "K&N HP-1008"],
                        maintenance_interval="Every 5,000 miles"
                    ),
                    'spark_plugs': PartInformation(
                        part_name="Spark Plugs",
                        part_number="98079-55846",
                        brand="Honda OEM (NGK)",
                        price_range="$6-10 each",
                        compatibility_notes="Iridium spark plugs for D16W7 VTEC engine",
                        specifications={"gap": "0.039-0.043\"", "heat_range": "6", "thread_size": "14mm"},
                        alternatives=["NGK ZFR6F-11", "Denso IK20", "Champion RE14MCC4"],
                        maintenance_interval="Every 60,000 miles"
                    ),
                    'timing_belt': PartInformation(
                        part_name="Timing Belt",
                        part_number="14400-P2A-004",
                        brand="Honda OEM",
                        price_range="$45-85",
                        compatibility_notes="Timing belt for D16W7 SOHC VTEC",
                        specifications={"length": "102 teeth", "width": "25mm"},
                        alternatives=["Gates T297", "Dayco 95297", "Continental 40297"],
                        maintenance_interval="Every 105,000 miles"
                    ),
                    'water_pump': PartInformation(
                        part_name="Water Pump",
                        part_number="19200-P2A-003",
                        brand="Honda OEM",
                        price_range="$65-120",
                        compatibility_notes="Water pump for Honda D16W7 engine",
                        specifications={"outlet_diameter": "38mm", "impeller_type": "Centrifugal"},
                        alternatives=["GMB GWH-43A", "Aisin WPH-043", "Beck Arnley 131-2243"],
                        maintenance_interval="Every 105,000 miles (with timing belt)"
                    ),
                    'vtec_solenoid': PartInformation(
                        part_name="VTEC Solenoid Valve",
                        part_number="15810-P2A-A01",
                        brand="Honda OEM",
                        price_range="$85-150",
                        compatibility_notes="VTEC solenoid valve for D16W7 engine",
                        specifications={"voltage": "12V", "resistance": "14-30 ohms"},
                        alternatives=["Standard VS63", "Wells SU4086", "Beck Arnley 028-0238"],
                        maintenance_interval="Replace if faulty"
                    )
                },
                'brake_parts': {
                    'brake_pads_front': PartInformation(
                        part_name="Front Brake Pads",
                        part_number="45022-S5A-E50",
                        brand="Honda OEM",
                        price_range="$35-65",
                        compatibility_notes="Ceramic brake pads for 2001-2005 Civic",
                        specifications={"pad_type": "Ceramic", "thickness": "10mm"},
                        alternatives=["Akebono ACT787", "Wagner ThermoQuiet QC787", "RayBestos SGD787C"],
                        maintenance_interval="Every 25,000-40,000 miles"
                    ),
                    'brake_rotors_front': PartInformation(
                        part_name="Front Brake Rotors",
                        part_number="45251-S5A-A10",
                        brand="Honda OEM",
                        price_range="$55-95 each",
                        compatibility_notes="Vented rotors for Honda Civic",
                        specifications={"diameter": "262mm", "thickness": "22mm"},
                        alternatives=["Centric 121.40047", "RayBestos 96954R", "Wagner BD125508"],
                        maintenance_interval="Every 50,000-70,000 miles"
                    )
                },
                'maintenance_parts': {
                    'coolant': PartInformation(
                        part_name="Engine Coolant",
                        part_number="08CLA-P99-08ZA",
                        brand="Honda OEM",
                        price_range="$12-18 per gallon",
                        compatibility_notes="Honda Long Life Coolant for D16W7",
                        specifications={"type": "Ethylene Glycol", "color": "Blue/Green"},
                        alternatives=["Prestone Honda/Acura", "Zerex Asian Blue", "Peak Final Charge"],
                        maintenance_interval="Every 60,000 miles"
                    )
                }
            }
        }

    def search_by_engine_code(self, engine_input: str) -> Optional[Dict[str, Any]]:
        """Search by engine code/number"""
        # Clean the input - extract engine code part
        engine_code = self.extract_engine_code(engine_input)
        
        if not engine_code:
            logger.error(f"Could not extract valid engine code from: {engine_input}")
            return None
        
        # Look up engine information
        engine_info = self.engine_database.get(engine_code.upper())
        if not engine_info:
            logger.warning(f"Engine code '{engine_code}' not found in database")
            return None
        
        # Get parts for this engine
        parts_data = self.engine_parts_database.get(engine_code.upper(), {})
        
        # Create response
        result = {
            'search_type': 'engine_code',
            'engine_code': engine_code.upper(),
            'engine_info': {
                'displacement': engine_info.displacement,
                'type': engine_info.type_,
                'fuel_system': engine_info.fuel_system,
                'valves_per_cylinder': engine_info.valves_per_cylinder,
                'compression_ratio': engine_info.compression_ratio,
                'max_power': engine_info.max_power,
                'max_torque': engine_info.max_torque,
                'fuel_type': engine_info.fuel_type,
                'common_vehicles': engine_info.common_vehicles
            },
            'parts_compatibility': parts_data,
            'total_parts': sum(len(category) for category in parts_data.values()),
            'parts_categories': list(parts_data.keys())
        }
        
        return result

    def extract_engine_code(self, engine_input: str) -> Optional[str]:
        """Extract engine code from various input formats"""
        engine_input = engine_input.strip().upper()
        
        # Common Honda engine patterns
        honda_patterns = [
            r'(D\d{2}[A-Z]\d?)',  # D16W7, D17A1, etc.
            r'(B\d{2}[A-Z]\d?)',  # B18C1, B16A2, etc.
            r'(H\d{2}[A-Z]\d?)',  # H22A1, H23A1, etc.
            r'(F\d{2}[A-Z]\d?)',  # F22B1, F20B, etc.
            r'(K\d{2}[A-Z]\d?)',  # K20A2, K24A2, etc.
        ]
        
        # Toyota engine patterns
        toyota_patterns = [
            r'(\d[A-Z]{2}-[A-Z]{2})',  # 1ZZ-FE, 2AZ-FE, etc.
            r'(\d[A-Z]{2}FE)',         # 1ZZFE, 2AZFE, etc.
        ]
        
        all_patterns = honda_patterns + toyota_patterns
        
        for pattern in all_patterns:
            match = re.search(pattern, engine_input)
            if match:
                return match.group(1)
        
        # If no pattern matches, check if it's a direct engine code
        if engine_input in self.engine_database:
            return engine_input
        
        return None

    def is_engine_code(self, input_string: str) -> bool:
        """Check if input looks like an engine code vs VIN"""
        input_string = input_string.strip()
        
        # VIN is exactly 17 characters
        if len(input_string) == 17:
            return False
        
        # Check if it matches engine code patterns
        return self.extract_engine_code(input_string) is not None

    def search(self, search_input: str) -> Dict[str, Any]:
        """Universal search - auto-detects VIN vs engine code"""
        search_input = search_input.strip()
        
        if self.is_engine_code(search_input):
            # Engine code search
            result = self.search_by_engine_code(search_input)
            if result:
                return {
                    'success': True,
                    'search_type': 'engine_code',
                    'data': result
                }
            else:
                return {
                    'success': False,
                    'error': f'Engine code not found: {search_input}',
                    'suggestion': 'Try: D16W7, D17A1, 1ZZ-FE, 2AZ-FE'
                }
        else:
            # Assume VIN search - delegate to enhanced decoder
            from enhanced_vin_decoder import EnhancedJapaneseCarVINDecoder
            
            decoder = EnhancedJapaneseCarVINDecoder()
            vehicle_info = decoder.decode_vin(search_input)
            
            if vehicle_info:
                return {
                    'success': True,
                    'search_type': 'vin',
                    'data': vehicle_info
                }
            else:
                return {
                    'success': False,
                    'error': f'Could not decode VIN: {search_input}',
                    'suggestion': 'Ensure VIN is exactly 17 characters'
                }

def demo_engine_search():
    """Demonstrate engine search functionality"""
    decoder = EnhancedEngineVINDecoder()
    
    print("🔍 ENGINE CODE SEARCH DEMO")
    print("=" * 60)
    
    # Test engine codes
    test_engines = [
        "D16W73005025",  # User's original input
        "D16W7",         # Clean engine code
        "D17A1",         # Another Honda engine
        "1ZZ-FE",        # Toyota engine
    ]
    
    for engine_input in test_engines:
        print(f"\n🔧 Testing input: {engine_input}")
        print("-" * 40)
        
        result = decoder.search(engine_input)
        
        if result['success']:
            if result['search_type'] == 'engine_code':
                data = result['data']
                engine_info = data['engine_info']
                
                print(f"✅ Found engine: {data['engine_code']}")
                print(f"📊 Displacement: {engine_info['displacement']}")
                print(f"🔧 Type: {engine_info['type']}")
                print(f"💪 Power: {engine_info['max_power']}")
                print(f"🚗 Common vehicles:")
                for vehicle in engine_info['common_vehicles']:
                    print(f"   • {vehicle['years']} {vehicle['make']} {vehicle['model']}")
                
                print(f"🔧 Parts available: {data['total_parts']} parts in {len(data['parts_categories'])} categories")
                for category in data['parts_categories']:
                    parts_count = len(data['parts_compatibility'][category])
                    print(f"   • {category.replace('_', ' ').title()}: {parts_count} parts")
                
                # Show first few parts as example
                if 'engine_parts' in data['parts_compatibility']:
                    print(f"\n🔧 Sample Engine Parts:")
                    engine_parts = data['parts_compatibility']['engine_parts']
                    for i, (part_key, part_info) in enumerate(list(engine_parts.items())[:3]):
                        print(f"   {i+1}. {part_info.part_name} ({part_info.part_number}) - {part_info.price_range}")
            else:
                print(f"✅ VIN decoded successfully")
        else:
            print(f"❌ {result['error']}")
            if 'suggestion' in result:
                print(f"💡 {result['suggestion']}")

if __name__ == "__main__":
    demo_engine_search()