#!/usr/bin/env python3
"""
Startup Script for Japanese Car VIN Decoder
===========================================

This script provides an easy way to start the web interface.
"""

import sys
import os
import subprocess

def main():
    print("🚗 Japanese Car VIN Decoder - Startup Menu")
    print("=" * 40)
    print("1. Start Enhanced Web Interface (Recommended)")
    print("2. Start Simple Web Interface")
    print("3. Start Flask Web Interface (requires Flask)")
    print("4. Run Test Suite")
    print("5. Exit")
    print()
    
    while True:
        try:
            choice = input("Enter your choice (1-5): ").strip()
            
            if choice == "1":
                print("\n🚀 Starting Enhanced Web Interface...")
                print("📱 Open your browser and go to: http://localhost:5001")
                print("🛑 Press Ctrl+C to stop the server")
                print("-" * 40)
                subprocess.run([sys.executable, "enhanced_web_interface.py"])
                break
                
            elif choice == "2":
                print("\n🚀 Starting Simple Web Interface...")
                print("📱 Open your browser and go to: http://localhost:5000")
                print("🛑 Press Ctrl+C to stop the server")
                print("-" * 40)
                subprocess.run([sys.executable, "simple_web_interface.py"])
                break
                
            elif choice == "3":
                print("\n🚀 Starting Flask Web Interface...")
                print("📱 Open your browser and go to: http://localhost:5000")
                print("🛑 Press Ctrl+C to stop the server")
                print("-" * 40)
                try:
                    subprocess.run([sys.executable, "web_interface.py"])
                except FileNotFoundError:
                    print("❌ Flask not installed. Please install Flask first:")
                    print("   pip install flask flask-cors")
                break
                
            elif choice == "4":
                print("\n🧪 Running Test Suite...")
                print("-" * 40)
                subprocess.run([sys.executable, "test_system.py"])
                break
                
            elif choice == "5":
                print("\n👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1, 2, 3, 4, or 5.")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            break

if __name__ == "__main__":
    main()
