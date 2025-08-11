#!/usr/bin/env python3
"""
Interactive VIN Decoder - No Dependencies Required
==================================================

Simple command-line interface for testing the VIN decoder with detailed parts information.
"""

from japanese_car_vin_decoder import JapaneseCarVINDecoder
from enhanced_vin_decoder import EnhancedJapaneseCarVINDecoder, PartInformation
import json

def format_parts_info(parts_compatibility):
    """Format parts information for display"""
    output = []
    
    for category, parts in parts_compatibility.items():
        output.append(f"\n🔧 {category.upper().replace('_', ' ')} PARTS:")
        output.append("-" * 40)
        
        if isinstance(parts, dict):
            for part_key, part_info in parts.items():
                if isinstance(part_info, PartInformation):
                    output.append(f"✨ {part_info.part_name}")
                    output.append(f"   Part Number: {part_info.part_number}")
                    output.append(f"   Brand: {part_info.brand}")
                    output.append(f"   Price: {part_info.price_range}")
                    output.append(f"   Maintenance: {part_info.maintenance_interval}")
                    if part_info.alternatives:
                        output.append(f"   Alternatives: {', '.join(part_info.alternatives[:3])}")
                    output.append("")
        elif isinstance(parts, list):
            for i, part in enumerate(parts, 1):
                if isinstance(part, PartInformation):
                    output.append(f"{i}. {part.part_name} ({part.part_number}) - {part.price_range}")
                else:
                    output.append(f"{i}. {part}")
        else:
            output.append(f"   {parts}")
    
    return "\n".join(output)

def interactive_decoder():
    """Interactive VIN decoder interface"""
    print("🚗 Japanese Car VIN Decoder - Interactive Mode")
    print("=" * 60)
    print("Enter VINs to decode, or 'quit' to exit")
    print("For detailed parts info, try a 2005 Toyota Camry VIN")
    print()
    
    # Initialize both decoders
    basic_decoder = JapaneseCarVINDecoder()
    enhanced_decoder = EnhancedJapaneseCarVINDecoder()
    
    # Show available detailed data
    print("📊 Available detailed parts data:")
    print("   ✅ 2005 Toyota Camry - 7 detailed parts")
    print("   ✅ 2005 Honda Civic - 1 detailed part")
    print("   ❓ Other vehicles - generic parts info")
    print()
    
    while True:
        vin = input("🔍 Enter VIN (or 'quit'): ").strip().upper()
        
        if vin.lower() == 'quit':
            print("👋 Goodbye!")
            break
        
        if not vin:
            continue
        
        if len(vin) != 17:
            print("❌ VIN must be exactly 17 characters")
            continue
        
        print(f"\n📋 Decoding VIN: {vin}")
        print("-" * 50)
        
        # Try enhanced decoder first
        vehicle_info = enhanced_decoder.decode_vin(vin)
        
        if vehicle_info:
            print(f"✅ Successfully decoded!")
            print(f"🚗 Vehicle: {vehicle_info.year} {vehicle_info.make} {vehicle_info.model}")
            print(f"🔧 Engine: {vehicle_info.engine}")
            print(f"⚙️  Transmission: {vehicle_info.transmission}")
            print(f"🏠 Body Style: {vehicle_info.body_style}")
            print(f"⛽ Fuel Type: {vehicle_info.fuel_type}")
            
            if vehicle_info.safety_features:
                print(f"🛡️  Safety Features: {', '.join(vehicle_info.safety_features)}")
            
            # Check if we have detailed parts info
            has_detailed_parts = False
            total_parts = 0
            
            for category, parts in vehicle_info.parts_compatibility.items():
                if isinstance(parts, dict):
                    total_parts += len(parts)
                    for part_info in parts.values():
                        if isinstance(part_info, PartInformation) and part_info.part_number != "Generic":
                            has_detailed_parts = True
                            break
                elif isinstance(parts, list):
                    total_parts += len(parts)
                    for part in parts:
                        if isinstance(part, PartInformation) and part.part_number != "Generic":
                            has_detailed_parts = True
                            break
            
            if has_detailed_parts:
                print(f"🎉 DETAILED PARTS INFORMATION AVAILABLE!")
                print(f"📦 Found {total_parts} parts across {len(vehicle_info.parts_compatibility)} categories")
                
                # Show detailed parts
                parts_output = format_parts_info(vehicle_info.parts_compatibility)
                print(parts_output)
                
                # Show maintenance schedule if available
                if vehicle_info.maintenance_schedule:
                    print(f"\n📅 MAINTENANCE SCHEDULE:")
                    print("-" * 40)
                    for interval, schedule in vehicle_info.maintenance_schedule.items():
                        print(f"🔧 {interval.replace('_', ' ').title()}")
                        print(f"   Cost: {schedule.estimated_cost}")
                        print(f"   Services: {', '.join(schedule.services)}")
                        print()
                
                # Show specifications if available
                if vehicle_info.specifications:
                    specs = vehicle_info.specifications
                    print(f"\n📊 VEHICLE SPECIFICATIONS:")
                    print("-" * 40)
                    print(f"🔧 Engine: {specs.engine_displacement} {specs.horsepower}")
                    print(f"💪 Torque: {specs.torque}")
                    print(f"⛽ Fuel Capacity: {specs.fuel_capacity}")
                    print(f"🛢️  Oil Capacity: {specs.oil_capacity}")
                    print(f"🧊 Coolant Capacity: {specs.coolant_capacity}")
                    if specs.dimensions:
                        dims = specs.dimensions
                        print(f"📏 Dimensions: {dims.get('length', 'N/A')} L x {dims.get('width', 'N/A')} W x {dims.get('height', 'N/A')} H")
                    print(f"⚖️  Weight: {specs.weight}")
                    print(f"🚛 Towing Capacity: {specs.towing_capacity}")
                
            else:
                print(f"ℹ️  Generic parts information available")
                print(f"📦 Found {total_parts} parts across {len(vehicle_info.parts_compatibility)} categories")
                
                # Show basic parts
                for category, parts in vehicle_info.parts_compatibility.items():
                    print(f"\n🔧 {category.upper().replace('_', ' ')}:")
                    if isinstance(parts, list):
                        for part in parts:
                            if isinstance(part, PartInformation):
                                print(f"   • {part.part_name} - {part.price_range}")
                            else:
                                print(f"   • {part}")
                    elif isinstance(parts, dict):
                        for part in parts.values():
                            if isinstance(part, PartInformation):
                                print(f"   • {part.part_name} - {part.price_range}")
        else:
            print("❌ Could not decode VIN")
            print("   • Check if VIN is valid (17 characters, no I/O/Q)")
            print("   • Ensure internet connection for NHTSA API")
        
        print("\n" + "="*60)

def quick_demo():
    """Quick demonstration with known working VINs"""
    print("🎬 Quick Demo - Known Working Examples")
    print("=" * 50)
    
    demo_vins = [
        ("1HGBH41JXMN109186", "Honda test"),
        ("1NXBR32E85Z123456", "Toyota test"), 
        ("1N4AL11D75C123456", "Nissan test")
    ]
    
    enhanced_decoder = EnhancedJapaneseCarVINDecoder()
    
    for vin, description in demo_vins:
        print(f"\n📋 {description}: {vin}")
        print("-" * 30)
        
        vehicle_info = enhanced_decoder.decode_vin(vin)
        if vehicle_info:
            print(f"   Vehicle: {vehicle_info.year} {vehicle_info.make} {vehicle_info.model}")
            print(f"   Engine: {vehicle_info.engine}")
            
            # Count parts
            total_parts = sum(
                len(parts) if isinstance(parts, (dict, list)) else 1 
                for parts in vehicle_info.parts_compatibility.values()
            )
            print(f"   Parts: {total_parts} items across {len(vehicle_info.parts_compatibility)} categories")
        else:
            print(f"   ❌ Could not decode")

if __name__ == "__main__":
    print("Choose an option:")
    print("1. Interactive decoder")
    print("2. Quick demo")
    
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        interactive_decoder()
    elif choice == "2":
        quick_demo()
    else:
        print("Invalid choice. Running quick demo...")
        quick_demo()