#!/usr/bin/env python3
"""
Japanese Car VIN Decoder and Parts Identification System
========================================================

This system provides VIN decoding and parts identification specifically for Japanese vehicles.
It uses the NHTSA API and additional data sources to provide comprehensive vehicle information.

Features:
- VIN decoding for Japanese vehicles
- Parts identification and compatibility
- Vehicle specifications lookup
- Engine and transmission information
- Safety features identification
"""

import requests
import json
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class VehicleInfo:
    """Data class for vehicle information"""
    vin: str
    make: str
    model: str
    year: str
    engine: str
    transmission: str
    body_style: str
    trim: str
    fuel_type: str
    drive_type: str
    doors: str
    seats: str
    safety_features: List[str]
    parts_compatibility: Dict[str, List[str]]

class JapaneseCarVINDecoder:
    """VIN Decoder specifically for Japanese vehicles"""
    
    def __init__(self):
        self.nhtsa_base_url = "https://vpic.nhtsa.dot.gov/api"
        self.japanese_manufacturers = {
            'TOYOTA', 'HONDA', 'NISSAN', 'MAZDA', 'MITSUBISHI', 'SUBARU', 
            'SUZUKI', 'ISUZU', 'DAIHATSU', 'LEXUS', 'ACURA', 'INFINITI',
            'SCION', 'DATSUN'
        }
        
        # Japanese manufacturer VIN patterns
        self.vin_patterns = {
            'TOYOTA': {
                'pattern': r'^[1-5][A-Z0-9]{16}$',
                'wmi': ['1T', '2T', '3T', '4T', '5T', 'JT', 'KL', 'KM', 'KN', 'KP', 'KR', 'KS', 'KT', 'KU', 'KV', 'KW', 'KX', 'KY', 'KZ']
            },
            'HONDA': {
                'pattern': r'^[1-5][A-Z0-9]{16}$',
                'wmi': ['1H', '2H', '3H', '4H', '5H', 'JH', 'KL', 'KM', 'KN', 'KP', 'KR', 'KS', 'KT', 'KU', 'KV', 'KW', 'KX', 'KY', 'KZ']
            },
            'NISSAN': {
                'pattern': r'^[1-5][A-Z0-9]{16}$',
                'wmi': ['1N', '2N', '3N', '4N', '5N', 'JN', 'KL', 'KM', 'KN', 'KP', 'KR', 'KS', 'KT', 'KU', 'KV', 'KW', 'KX', 'KY', 'KZ']
            },
            'MAZDA': {
                'pattern': r'^[1-5][A-Z0-9]{16}$',
                'wmi': ['1Y', '2Y', '3Y', '4Y', '5Y', 'JM', 'KL', 'KM', 'KN', 'KP', 'KR', 'KS', 'KT', 'KU', 'KV', 'KW', 'KX', 'KY', 'KZ']
            },
            'MITSUBISHI': {
                'pattern': r'^[1-5][A-Z0-9]{16}$',
                'wmi': ['1A', '2A', '3A', '4A', '5A', 'JA', 'KL', 'KM', 'KN', 'KP', 'KR', 'KS', 'KT', 'KU', 'KV', 'KW', 'KX', 'KY', 'KZ']
            },
            'SUBARU': {
                'pattern': r'^[1-5][A-Z0-9]{16}$',
                'wmi': ['1S', '2S', '3S', '4S', '5S', 'JF', 'KL', 'KM', 'KN', 'KP', 'KR', 'KS', 'KT', 'KU', 'KV', 'KW', 'KX', 'KY', 'KZ']
            }
        }
        
        # Common Japanese car parts categories
        self.parts_categories = {
            'engine': ['air_filter', 'oil_filter', 'spark_plugs', 'timing_belt', 'water_pump', 'thermostat'],
            'brakes': ['brake_pads', 'brake_rotors', 'brake_calipers', 'brake_lines', 'master_cylinder'],
            'suspension': ['shocks', 'struts', 'springs', 'control_arms', 'bushings', 'ball_joints'],
            'transmission': ['transmission_filter', 'transmission_fluid', 'clutch', 'flywheel'],
            'electrical': ['battery', 'alternator', 'starter', 'ignition_coil', 'spark_plug_wires'],
            'cooling': ['radiator', 'hoses', 'coolant', 'fan', 'temperature_sensor'],
            'fuel': ['fuel_filter', 'fuel_pump', 'injectors', 'fuel_lines'],
            'exhaust': ['catalytic_converter', 'muffler', 'exhaust_pipes', 'oxygen_sensors']
        }

    def validate_vin(self, vin: str) -> bool:
        """Validate VIN format and checksum"""
        if not vin or len(vin) != 17:
            return False
        
        # Check for valid characters (no I, O, Q)
        invalid_chars = ['I', 'O', 'Q']
        if any(char in vin for char in invalid_chars):
            return False
        
        # Basic pattern validation
        vin_pattern = r'^[A-HJ-NPR-Z0-9]{17}$'
        if not re.match(vin_pattern, vin):
            return False
        
        return True

    def decode_vin_nhtsa(self, vin: str) -> Dict[str, Any]:
        """Decode VIN using NHTSA API"""
        try:
            url = f"{self.nhtsa_base_url}/vehicles/DecodeVin/{vin}?format=json"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            if data.get('Count', 0) == 0:
                return {}
            
            # Convert results to dictionary
            decoded_data = {}
            for item in data.get('Results', []):
                variable = item.get('Variable', '')
                value = item.get('Value', '')
                if value and value != '' and value != 'null':
                    decoded_data[variable] = value
            
            return decoded_data
            
        except requests.RequestException as e:
            logger.error(f"Error decoding VIN with NHTSA API: {e}")
            return {}

    def get_vehicle_specifications(self, make: str, model: str, year: str) -> Dict[str, Any]:
        """Get detailed vehicle specifications"""
        try:
            # Get makes
            makes_url = f"{self.nhtsa_base_url}/vehicles/GetMakes?format=json"
            makes_response = requests.get(makes_url, timeout=10)
            makes_data = makes_response.json()
            
            make_id = None
            for make_item in makes_data.get('Results', []):
                if make_item.get('Make_Name', '').upper() == make.upper():
                    make_id = make_item.get('Make_ID')
                    break
            
            if not make_id:
                return {}
            
            # Get models for the make
            models_url = f"{self.nhtsa_base_url}/vehicles/GetModelsForMakeId/{make_id}?format=json"
            models_response = requests.get(models_url, timeout=10)
            models_data = models_response.json()
            
            model_id = None
            for model_item in models_data.get('Results', []):
                if model_item.get('Model_Name', '').upper() == model.upper():
                    model_id = model_item.get('Model_ID')
                    break
            
            if not model_id:
                return {}
            
            # Get vehicle types
            vehicle_types_url = f"{self.nhtsa_base_url}/vehicles/GetVehicleTypesForMakeId/{make_id}?format=json"
            vehicle_types_response = requests.get(vehicle_types_url, timeout=10)
            vehicle_types_data = vehicle_types_response.json()
            
            return {
                'make_id': make_id,
                'model_id': model_id,
                'vehicle_types': vehicle_types_data.get('Results', [])
            }
            
        except requests.RequestException as e:
            logger.error(f"Error getting vehicle specifications: {e}")
            return {}

    def identify_parts_compatibility(self, vehicle_info: VehicleInfo) -> Dict[str, List[str]]:
        """Identify compatible parts for the vehicle"""
        compatibility = {}
        
        # Engine-specific parts
        if vehicle_info.engine:
            engine_parts = self.get_engine_specific_parts(vehicle_info.engine)
            compatibility['engine'] = engine_parts
        
        # Transmission-specific parts
        if vehicle_info.transmission:
            trans_parts = self.get_transmission_specific_parts(vehicle_info.transmission)
            compatibility['transmission'] = trans_parts
        
        # Year-specific parts
        year_parts = self.get_year_specific_parts(vehicle_info.year, vehicle_info.make)
        compatibility['year_specific'] = year_parts
        
        # Model-specific parts
        model_parts = self.get_model_specific_parts(vehicle_info.make, vehicle_info.model)
        compatibility['model_specific'] = model_parts
        
        return compatibility

    def get_engine_specific_parts(self, engine: str) -> List[str]:
        """Get engine-specific parts based on engine code"""
        engine_parts = {
            '2JZ': ['timing_belt', 'water_pump', 'thermostat', 'oil_filter', 'air_filter'],
            '1JZ': ['timing_belt', 'water_pump', 'thermostat', 'oil_filter', 'air_filter'],
            '3S': ['timing_belt', 'water_pump', 'thermostat', 'oil_filter', 'air_filter'],
            '4A': ['timing_belt', 'water_pump', 'thermostat', 'oil_filter', 'air_filter'],
            'B': ['timing_belt', 'water_pump', 'thermostat', 'oil_filter', 'air_filter'],
            'F': ['timing_belt', 'water_pump', 'thermostat', 'oil_filter', 'air_filter'],
            'K': ['timing_belt', 'water_pump', 'thermostat', 'oil_filter', 'air_filter'],
            'H': ['timing_belt', 'water_pump', 'thermostat', 'oil_filter', 'air_filter']
        }
        
        for engine_code, parts in engine_parts.items():
            if engine_code in engine.upper():
                return parts
        
        return ['timing_belt', 'water_pump', 'thermostat', 'oil_filter', 'air_filter']

    def get_transmission_specific_parts(self, transmission: str) -> List[str]:
        """Get transmission-specific parts"""
        if 'automatic' in transmission.lower():
            return ['transmission_filter', 'transmission_fluid', 'transmission_pan_gasket']
        elif 'manual' in transmission.lower():
            return ['clutch', 'flywheel', 'clutch_master_cylinder', 'clutch_slave_cylinder']
        else:
            return ['transmission_filter', 'transmission_fluid']

    def get_year_specific_parts(self, year: str, make: str) -> List[str]:
        """Get year-specific parts"""
        year_int = int(year)
        
        if year_int < 2000:
            return ['carburetor_parts', 'distributor_cap', 'distributor_rotor']
        elif year_int < 2010:
            return ['ignition_coil', 'spark_plug_wires', 'oxygen_sensors']
        else:
            return ['direct_injection_parts', 'variable_valve_timing_parts', 'turbo_parts']

    def get_model_specific_parts(self, make: str, model: str) -> List[str]:
        """Get model-specific parts"""
        model_specific = {
            'TOYOTA': {
                'CAMRY': ['camry_specific_trim', 'camry_engine_mounts'],
                'COROLLA': ['corolla_specific_trim', 'corolla_engine_mounts'],
                'HIGHLANDER': ['highlander_specific_trim', 'highlander_suspension'],
                'RAV4': ['rav4_specific_trim', 'rav4_suspension']
            },
            'HONDA': {
                'CIVIC': ['civic_specific_trim', 'civic_engine_mounts'],
                'ACCORD': ['accord_specific_trim', 'accord_engine_mounts'],
                'CR-V': ['crv_specific_trim', 'crv_suspension'],
                'PILOT': ['pilot_specific_trim', 'pilot_suspension']
            },
            'NISSAN': {
                'ALTIMA': ['altima_specific_trim', 'altima_engine_mounts'],
                'SENTRA': ['sentra_specific_trim', 'sentra_engine_mounts'],
                'ROGUE': ['rogue_specific_trim', 'rogue_suspension'],
                'MURANO': ['murano_specific_trim', 'murano_suspension']
            }
        }
        
        make_models = model_specific.get(make.upper(), {})
        return make_models.get(model.upper(), [])

    def decode_vin(self, vin: str) -> Optional[VehicleInfo]:
        """Main method to decode VIN and return vehicle information"""
        if not self.validate_vin(vin):
            logger.error(f"Invalid VIN format: {vin}")
            return None
        
        # Decode VIN using NHTSA API
        decoded_data = self.decode_vin_nhtsa(vin)
        if not decoded_data:
            logger.error(f"Could not decode VIN: {vin}")
            return None
        
        # Extract vehicle information
        make = decoded_data.get('Make', '')
        model = decoded_data.get('Model', '')
        year = decoded_data.get('Model Year', '')
        
        # Check if it's a Japanese vehicle
        if make.upper() not in self.japanese_manufacturers:
            logger.warning(f"Vehicle make '{make}' is not a Japanese manufacturer")
        
        # Create VehicleInfo object
        vehicle_info = VehicleInfo(
            vin=vin,
            make=make,
            model=model,
            year=year,
            engine=decoded_data.get('Engine Model', ''),
            transmission=decoded_data.get('Transmission Style', ''),
            body_style=decoded_data.get('Body Class', ''),
            trim=decoded_data.get('Trim', ''),
            fuel_type=decoded_data.get('Fuel Type - Primary', ''),
            drive_type=decoded_data.get('Drive Type', ''),
            doors=decoded_data.get('Doors', ''),
            seats=decoded_data.get('Number of Seats', ''),
            safety_features=self.extract_safety_features(decoded_data),
            parts_compatibility={}
        )
        
        # Get parts compatibility
        vehicle_info.parts_compatibility = self.identify_parts_compatibility(vehicle_info)
        
        return vehicle_info

    def extract_safety_features(self, decoded_data: Dict[str, Any]) -> List[str]:
        """Extract safety features from decoded data"""
        safety_features = []
        
        safety_mapping = {
            'Anti-lock Braking System (ABS)': 'ABS',
            'Electronic Stability Control (ESC)': 'ESC',
            'Traction Control': 'Traction Control',
            'Tire Pressure Monitoring System (TPMS) Type': 'TPMS',
            'Backup Camera': 'Backup Camera',
            'Lane Departure Warning (LDW)': 'Lane Departure Warning',
            'Forward Collision Warning (FCW)': 'Forward Collision Warning',
            'Blind Spot Warning (BSW)': 'Blind Spot Warning',
            'Adaptive Cruise Control (ACC)': 'Adaptive Cruise Control'
        }
        
        for feature, display_name in safety_mapping.items():
            if decoded_data.get(feature):
                safety_features.append(display_name)
        
        return safety_features

    def search_parts_by_vehicle(self, vehicle_info: VehicleInfo, part_category: str = None) -> Dict[str, Any]:
        """Search for parts based on vehicle information"""
        search_results = {
            'vehicle': vehicle_info,
            'parts': {},
            'compatibility_notes': []
        }
        
        if part_category:
            if part_category in vehicle_info.parts_compatibility:
                search_results['parts'][part_category] = vehicle_info.parts_compatibility[part_category]
        else:
            search_results['parts'] = vehicle_info.parts_compatibility
        
        # Add compatibility notes
        search_results['compatibility_notes'].append(
            f"Parts compatible with {vehicle_info.year} {vehicle_info.make} {vehicle_info.model}"
        )
        
        if vehicle_info.engine:
            search_results['compatibility_notes'].append(
                f"Engine: {vehicle_info.engine}"
            )
        
        if vehicle_info.transmission:
            search_results['compatibility_notes'].append(
                f"Transmission: {vehicle_info.transmission}"
            )
        
        return search_results

def main():
    """Example usage of the Japanese Car VIN Decoder"""
    decoder = JapaneseCarVINDecoder()
    
    # Example VINs (replace with real VINs)
    test_vins = [
        "1HGBH41JXMN109186",  # Honda
        "1NXBR32E85Z123456",  # Toyota
        "1N4AL11D75C123456",  # Nissan
    ]
    
    print("Japanese Car VIN Decoder and Parts Identification System")
    print("=" * 60)
    
    for vin in test_vins:
        print(f"\nDecoding VIN: {vin}")
        print("-" * 40)
        
        vehicle_info = decoder.decode_vin(vin)
        if vehicle_info:
            print(f"Make: {vehicle_info.make}")
            print(f"Model: {vehicle_info.model}")
            print(f"Year: {vehicle_info.year}")
            print(f"Engine: {vehicle_info.engine}")
            print(f"Transmission: {vehicle_info.transmission}")
            print(f"Body Style: {vehicle_info.body_style}")
            print(f"Fuel Type: {vehicle_info.fuel_type}")
            print(f"Safety Features: {', '.join(vehicle_info.safety_features)}")
            
            print("\nParts Compatibility:")
            for category, parts in vehicle_info.parts_compatibility.items():
                print(f"  {category}: {', '.join(parts)}")
        else:
            print("Could not decode VIN")

if __name__ == "__main__":
    main()
