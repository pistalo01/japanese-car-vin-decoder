#!/usr/bin/env python3
"""
Script to demonstrate detailed parts information with correct VIN matching
"""

from enhanced_vin_decoder import EnhancedJapaneseCarVINDecoder, PartInformation
import json

def show_parts_for_camry():
    decoder = EnhancedJapaneseCarVINDecoder()
    
    print("🚗 Demonstrating Detailed Parts Information")
    print("=" * 50)
    
    # The database has detailed info for 2005 Toyota Camry
    # Let's simulate getting a Camry VIN by directly accessing the parts
    
    print("📊 Available Detailed Parts Data:")
    print("-" * 30)
    
    # Show what's in the database
    camry_parts = decoder.enhanced_parts_database['TOYOTA']['CAMRY']['2005']
    
    for category, parts_dict in camry_parts.items():
        print(f"\n🔧 {category.upper().replace('_', ' ')} ({len(parts_dict)} parts):")
        print("-" * 40)
        
        for part_key, part_info in parts_dict.items():
            print(f"✨ {part_info.part_name}")
            print(f"   🏷️  Part Number: {part_info.part_number}")
            print(f"   🏭 Brand: {part_info.brand}")
            print(f"   💰 Price Range: {part_info.price_range}")
            print(f"   📝 Notes: {part_info.compatibility_notes}")
            print(f"   🔧 Maintenance: {part_info.maintenance_interval}")
            
            if part_info.specifications:
                print(f"   📋 Specifications: {part_info.specifications}")
            
            if part_info.alternatives:
                print(f"   🔄 Alternatives: {', '.join(part_info.alternatives)}")
            print()

def test_with_actual_camry_vin():
    """Test with a VIN that might decode as Camry"""
    decoder = EnhancedJapaneseCarVINDecoder()
    
    # Let's try some Camry VINs
    camry_vins = [
        "4T1BE46K75U123456",  # Toyota Camry VIN pattern
        "JTNBE46K750123456",  # Another Toyota pattern
        "1NXBE02E85Z123456",  # Modified pattern
    ]
    
    print("\n🧪 Testing with potential Camry VINs:")
    print("=" * 50)
    
    for vin in camry_vins:
        print(f"\n📋 Testing VIN: {vin}")
        vehicle_info = decoder.decode_vin(vin)
        
        if vehicle_info:
            print(f"   Vehicle: {vehicle_info.year} {vehicle_info.make} {vehicle_info.model}")
            print(f"   Engine: {vehicle_info.engine}")
            
            # Check if we got detailed parts
            detailed_parts = False
            for category, parts in vehicle_info.parts_compatibility.items():
                if isinstance(parts, list) and parts:
                    for part in parts:
                        if isinstance(part, PartInformation) and part.part_number != "Generic":
                            detailed_parts = True
                            break
            
            if detailed_parts:
                print("   ✅ Has detailed parts information!")
            else:
                print("   ❌ Only generic parts information")
        else:
            print("   ❌ Could not decode VIN")

def create_test_camry():
    """Create a direct test for Camry parts"""
    from enhanced_vin_decoder import EnhancedVehicleInfo, VehicleSpecifications
    
    decoder = EnhancedJapaneseCarVINDecoder()
    
    print("\n🔬 Direct Test: Creating 2005 Camry Vehicle Info")
    print("=" * 50)
    
    # Get parts directly from database
    enhanced_parts = decoder.get_enhanced_parts("TOYOTA", "CAMRY", "2005", "1ZZ-FE")
    maintenance_schedule = decoder.get_maintenance_schedule("TOYOTA", "CAMRY", "2005")
    vehicle_specs = decoder.get_vehicle_specifications("TOYOTA", "CAMRY", "2005", "1ZZ-FE")
    
    # Create mock vehicle info
    camry_info = EnhancedVehicleInfo(
        vin="MOCK2005CAMRY1234",
        make="TOYOTA",
        model="CAMRY",
        year="2005",
        engine="1ZZ-FE",
        transmission="Automatic",
        drive_type="FWD",
        body_style="Sedan",
        trim="LE",
        fuel_type="Gasoline",
        doors="4",
        seats="5",
        specifications=vehicle_specs,
        safety_features=["ABS", "Traction Control"],
        parts_compatibility=enhanced_parts,
        maintenance_schedule=maintenance_schedule
    )
    
    print(f"🚗 {camry_info.year} {camry_info.make} {camry_info.model}")
    print(f"🔧 Engine: {camry_info.engine}")
    
    if camry_info.specifications:
        print(f"\n📊 Specifications:")
        print(f"   Displacement: {camry_info.specifications.engine_displacement}")
        print(f"   Horsepower: {camry_info.specifications.horsepower}")
        print(f"   Torque: {camry_info.specifications.torque}")
        print(f"   Fuel Capacity: {camry_info.specifications.fuel_capacity}")
        print(f"   Oil Capacity: {camry_info.specifications.oil_capacity}")
    
    print(f"\n🔧 Detailed Parts ({len(camry_info.parts_compatibility)} categories):")
    for category, parts in camry_info.parts_compatibility.items():
        print(f"\n   📦 {category.upper().replace('_', ' ')} ({len(parts)} parts):")
        for part_key, part_info in parts.items():
            print(f"     • {part_info.part_name} ({part_info.part_number}) - {part_info.price_range}")
    
    if camry_info.maintenance_schedule:
        print(f"\n📅 Maintenance Schedule ({len(camry_info.maintenance_schedule)} intervals):")
        for interval, schedule in camry_info.maintenance_schedule.items():
            print(f"   🔧 {interval.replace('_', ' ').title()}: {schedule.estimated_cost}")
            print(f"      Services: {', '.join(schedule.services)}")

if __name__ == "__main__":
    show_parts_for_camry()
    test_with_actual_camry_vin()
    create_test_camry()