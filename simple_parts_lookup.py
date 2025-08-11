#!/usr/bin/env python3
"""
Simple Parts Lookup Tool
Shows you exactly how to get detailed parts information
"""

from enhanced_vin_decoder import EnhancedJapaneseCarVINDecoder, PartInformation
import json

def lookup_parts_by_vehicle():
    """Interactive parts lookup"""
    decoder = EnhancedJapaneseCarVINDecoder()
    
    print("🔧 Japanese Vehicle Parts Lookup Tool")
    print("=" * 50)
    
    # Show available data
    print("📊 Available Detailed Parts Data:")
    print("-" * 30)
    
    for make, make_data in decoder.enhanced_parts_database.items():
        for model, model_data in make_data.items():
            for year, year_data in model_data.items():
                total_parts = sum(len(parts) for parts in year_data.values() if isinstance(parts, dict))
                print(f"✅ {year} {make} {model} - {total_parts} detailed parts")
    
    print(f"\n🎯 How to get detailed parts:")
    print("1. Use a VIN that decodes to one of the above vehicles")
    print("2. Or call get_enhanced_parts() directly")
    print("3. Or use the web interface")
    
    print(f"\n🧪 Example - Direct Parts Lookup:")
    print("-" * 40)
    
    # Direct lookup example
    make = "TOYOTA"
    model = "CAMRY" 
    year = "2005"
    engine = "1ZZ-FE"
    
    parts = decoder.get_enhanced_parts(make, model, year, engine)
    
    print(f"🚗 {year} {make} {model} ({engine})")
    print(f"📦 Found {len(parts)} parts categories:")
    
    for category, parts_list in parts.items():
        print(f"\n🔧 {category.upper().replace('_', ' ')} ({len(parts_list)} parts):")
        
        if isinstance(parts_list, dict):
            for part_key, part_info in parts_list.items():
                print(f"   • {part_info.part_name}")
                print(f"     Part#: {part_info.part_number}")
                print(f"     Price: {part_info.price_range}")
                print(f"     Brand: {part_info.brand}")
                if part_info.alternatives:
                    print(f"     Alt: {', '.join(part_info.alternatives[:3])}")
        else:
            for part in parts_list:
                if isinstance(part, PartInformation):
                    print(f"   • {part.part_name} - {part.price_range}")
                else:
                    print(f"   • {part}")

def create_camry_vin_example():
    """Show how to create a working example"""
    print(f"\n🎯 Working Example - Manual Vehicle Creation:")
    print("=" * 50)
    
    decoder = EnhancedJapaneseCarVINDecoder()
    
    # Get all the data manually
    make = "TOYOTA"
    model = "CAMRY"
    year = "2005"
    engine = "1ZZ-FE"
    
    print(f"🚗 Creating: {year} {make} {model} with {engine} engine")
    
    # Get detailed parts
    parts = decoder.get_enhanced_parts(make, model, year, engine)
    maintenance = decoder.get_maintenance_schedule(make, model, year)
    specs = decoder.get_vehicle_specifications(make, model, year, engine)
    
    print(f"\n📋 Parts Summary:")
    total_parts = 0
    for category, parts_dict in parts.items():
        count = len(parts_dict) if isinstance(parts_dict, dict) else len(parts_dict)
        total_parts += count
        print(f"   {category}: {count} parts")
    
    print(f"\n💰 Estimated Parts Costs:")
    sample_costs = {
        "Air Filter": "$15-25",
        "Oil Filter": "$8-15", 
        "Spark Plugs": "$8-12 each (x4 = $32-48)",
        "Timing Belt Kit": "$150-250",
        "Front Brake Pads": "$45-80",
        "Front Brake Rotors": "$80-150 each (x2 = $160-300)",
        "Front Shocks": "$120-200 each (x2 = $240-400)"
    }
    
    for part, cost in sample_costs.items():
        print(f"   • {part}: {cost}")
    
    total_min = 15 + 8 + 32 + 150 + 45 + 160 + 240
    total_max = 25 + 15 + 48 + 250 + 80 + 300 + 400
    print(f"\n💵 Total Parts Cost Range: ${total_min} - ${total_max}")
    
    if maintenance:
        print(f"\n🔧 Maintenance Schedule ({len(maintenance)} intervals):")
        for interval, schedule in maintenance.items():
            print(f"   • {interval.replace('_', ' ').title()}: {schedule.estimated_cost}")
    
    if specs:
        print(f"\n📊 Specifications:")
        print(f"   • Engine: {specs.engine_displacement} {specs.horsepower}")
        print(f"   • Capacities: {specs.fuel_capacity} fuel, {specs.oil_capacity} oil")

def api_example():
    """Show how to use it programmatically"""
    print(f"\n🔌 API Usage Example:")
    print("=" * 50)
    
    code_example = '''
# Python code to get detailed parts:

from enhanced_vin_decoder import EnhancedJapaneseCarVINDecoder

decoder = EnhancedJapaneseCarVINDecoder()

# Method 1: Try VIN decoding (may fall back to generic)
vehicle_info = decoder.decode_vin("YOUR_VIN_HERE")

# Method 2: Direct parts lookup (guaranteed detailed if available)
parts = decoder.get_enhanced_parts("TOYOTA", "CAMRY", "2005", "1ZZ-FE")

# Method 3: Get specific part info
if "engine_parts" in parts:
    air_filter = parts["engine_parts"]["air_filter"]
    print(f"Air Filter: {air_filter.part_number} - {air_filter.price_range}")
'''
    
    print(code_example)

if __name__ == "__main__":
    lookup_parts_by_vehicle()
    create_camry_vin_example()
    api_example()