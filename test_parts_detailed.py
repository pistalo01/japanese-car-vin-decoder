#!/usr/bin/env python3
"""
Test script to show detailed parts information
"""

from enhanced_vin_decoder import EnhancedJapaneseCarVINDecoder, PartInformation
import json

def test_detailed_parts():
    decoder = EnhancedJapaneseCarVINDecoder()
    
    print("🔍 Testing detailed parts information...")
    print("=" * 60)
    
    # Test with a VIN that should have detailed data (2005 Toyota Camry)
    test_vin = "1NXBR32E85Z123456"  # This should decode as Toyota Corolla 2005
    
    print(f"Testing VIN: {test_vin}")
    vehicle_info = decoder.decode_vin(test_vin)
    
    if vehicle_info:
        print(f"\nVehicle: {vehicle_info.year} {vehicle_info.make} {vehicle_info.model}")
        print(f"Engine: {vehicle_info.engine}")
        
        print(f"\n📋 Parts Information:")
        print("-" * 40)
        
        for category, parts in vehicle_info.parts_compatibility.items():
            print(f"\n🔧 {category.upper()} PARTS:")
            if isinstance(parts, list) and parts:
                for i, part in enumerate(parts, 1):
                    if isinstance(part, PartInformation):
                        print(f"  {i}. {part.part_name}")
                        print(f"     Part Number: {part.part_number}")
                        print(f"     Brand: {part.brand}")
                        print(f"     Price Range: {part.price_range}")
                        print(f"     Maintenance: {part.maintenance_interval}")
                        if part.alternatives:
                            print(f"     Alternatives: {', '.join(part.alternatives)}")
                        print()
                    else:
                        print(f"  {i}. {part}")
            else:
                print(f"  No detailed parts info available for {category}")
    
    # Test direct database access
    print(f"\n📊 Database Contents:")
    print("-" * 40)
    
    # Check what's actually in the database
    for make, make_data in decoder.enhanced_parts_database.items():
        print(f"\n🏭 {make}:")
        for model, model_data in make_data.items():
            print(f"  📱 {model}:")
            for year, year_data in model_data.items():
                print(f"    📅 {year}:")
                for category, parts in year_data.items():
                    part_count = len(parts) if isinstance(parts, dict) else 0
                    print(f"      🔧 {category}: {part_count} parts")
                    
                    # Show first part as example
                    if isinstance(parts, dict) and parts:
                        first_part_key = list(parts.keys())[0]
                        first_part = parts[first_part_key]
                        print(f"        Example: {first_part.part_name} ({first_part.part_number})")

if __name__ == "__main__":
    test_detailed_parts()