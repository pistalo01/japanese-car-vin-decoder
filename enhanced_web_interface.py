#!/usr/bin/env python3
"""
Enhanced Web Interface for Japanese Car VIN Decoder
===================================================

A comprehensive web application that displays detailed vehicle information,
parts data, specifications, maintenance schedules, and more.
"""

import http.server
import socketserver
import json
import urllib.parse
from enhanced_vin_decoder import EnhancedJapaneseCarVINDecoder
import threading
import time

# Initialize the enhanced VIN decoder
decoder = EnhancedJapaneseCarVINDecoder()

class EnhancedVINDecoderHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_html_content().encode())
        elif self.path.startswith('/api/vehicle/'):
            vin = self.path.split('/')[-1]
            self.handle_api_vehicle(vin)
        elif self.path.startswith('/api/parts/'):
            vin = self.path.split('/')[-1]
            self.handle_api_parts(vin)
        elif self.path.startswith('/api/specifications/'):
            vin = self.path.split('/')[-1]
            self.handle_api_specifications(vin)
        elif self.path.startswith('/api/maintenance/'):
            vin = self.path.split('/')[-1]
            self.handle_api_maintenance(vin)
        else:
            super().do_GET()

    def do_POST(self):
        if self.path == '/decode':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            vin = data.get('vin', '')
            self.handle_decode_vin(vin)
        else:
            self.send_response(404)
            self.end_headers()

    def handle_api_vehicle(self, vin):
        try:
            vehicle_info = decoder.decode_vin(vin)
            if vehicle_info:
                # Convert dataclass to dict for JSON serialization
                vehicle_dict = self.vehicle_info_to_dict(vehicle_info)
                response = {'success': True, 'vehicle': vehicle_dict}
            else:
                response = {'success': False, 'error': 'Could not decode VIN'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())

    def handle_api_parts(self, vin):
        try:
            vehicle_info = decoder.decode_vin(vin)
            if vehicle_info:
                parts_dict = self.parts_info_to_dict(vehicle_info.parts_compatibility)
                response = {'success': True, 'parts': parts_dict}
            else:
                response = {'success': False, 'error': 'Could not decode VIN'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())

    def handle_api_specifications(self, vin):
        try:
            vehicle_info = decoder.decode_vin(vin)
            if vehicle_info and vehicle_info.specifications:
                specs_dict = self.specifications_to_dict(vehicle_info.specifications)
                response = {'success': True, 'specifications': specs_dict}
            else:
                response = {'success': False, 'error': 'No specifications available'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())

    def handle_api_maintenance(self, vin):
        try:
            vehicle_info = decoder.decode_vin(vin)
            if vehicle_info and vehicle_info.maintenance_schedule:
                maintenance_dict = self.maintenance_to_dict(vehicle_info.maintenance_schedule)
                response = {'success': True, 'maintenance': maintenance_dict}
            else:
                response = {'success': False, 'error': 'No maintenance schedule available'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())

    def handle_decode_vin(self, vin):
        try:
            vehicle_info = decoder.decode_vin(vin)
            if vehicle_info:
                vehicle_dict = self.vehicle_info_to_dict(vehicle_info)
                response = {'success': True, 'vehicle_info': vehicle_dict}
            else:
                response = {'success': False, 'error': 'Could not decode VIN'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response, default=str).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())

    def vehicle_info_to_dict(self, vehicle_info):
        """Convert vehicle info dataclass to dictionary"""
        return {
            'vin': vehicle_info.vin,
            'make': vehicle_info.make,
            'model': vehicle_info.model,
            'year': vehicle_info.year,
            'engine': vehicle_info.engine,
            'engine_code': vehicle_info.engine_code,
            'transmission': vehicle_info.transmission,
            'transmission_code': vehicle_info.transmission_code,
            'drive_type': vehicle_info.drive_type,
            'body_style': vehicle_info.body_style,
            'trim': vehicle_info.trim,
            'fuel_type': vehicle_info.fuel_type,
            'doors': vehicle_info.doors,
            'seats': vehicle_info.seats,
            'specifications': self.specifications_to_dict(vehicle_info.specifications) if vehicle_info.specifications else None,
            'safety_features': vehicle_info.safety_features,
            'standard_features': vehicle_info.standard_features,
            'optional_features': vehicle_info.optional_features,
            'parts_compatibility': self.parts_info_to_dict(vehicle_info.parts_compatibility),
            'maintenance_schedule': self.maintenance_to_dict(vehicle_info.maintenance_schedule) if vehicle_info.maintenance_schedule else None,
            'recalls': vehicle_info.recalls,
            'common_issues': vehicle_info.common_issues,
            'service_bulletins': vehicle_info.service_bulletins
        }

    def specifications_to_dict(self, specs):
        """Convert specifications dataclass to dictionary"""
        if not specs:
            return None
        return {
            'engine_displacement': specs.engine_displacement,
            'horsepower': specs.horsepower,
            'torque': specs.torque,
            'fuel_capacity': specs.fuel_capacity,
            'oil_capacity': specs.oil_capacity,
            'transmission_fluid_capacity': specs.transmission_fluid_capacity,
            'coolant_capacity': specs.coolant_capacity,
            'brake_fluid_type': specs.brake_fluid_type,
            'tire_size': specs.tire_size,
            'wheel_size': specs.wheel_size,
            'weight': specs.weight,
            'dimensions': specs.dimensions,
            'towing_capacity': specs.towing_capacity,
            'payload_capacity': specs.payload_capacity
        }

    def parts_info_to_dict(self, parts_compatibility):
        """Convert parts compatibility to dictionary"""
        if not parts_compatibility:
            return {}
        
        result = {}
        for category, parts in parts_compatibility.items():
            result[category] = []
            for part in parts:
                part_dict = {
                    'part_name': part.part_name,
                    'part_number': part.part_number,
                    'brand': part.brand,
                    'price_range': part.price_range,
                    'compatibility_notes': part.compatibility_notes,
                    'specifications': part.specifications,
                    'alternatives': part.alternatives,
                    'maintenance_interval': part.maintenance_interval
                }
                result[category].append(part_dict)
        
        return result

    def maintenance_to_dict(self, maintenance_schedule):
        """Convert maintenance schedule to dictionary"""
        if not maintenance_schedule:
            return {}
        
        result = {}
        for interval, schedule in maintenance_schedule.items():
            result[interval] = {
                'interval_miles': schedule.interval_miles,
                'interval_months': schedule.interval_months,
                'services': schedule.services,
                'parts_needed': schedule.parts_needed,
                'estimated_cost': schedule.estimated_cost
            }
        
        return result

    def get_html_content(self):
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enhanced Japanese Car VIN Decoder</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
        }
        .input-section {
            margin-bottom: 30px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
            color: #34495e;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
            box-sizing: border-box;
        }
        input[type="text"]:focus {
            border-color: #3498db;
            outline: none;
        }
        button {
            background-color: #3498db;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            width: 100%;
        }
        button:hover {
            background-color: #2980b9;
        }
        .results {
            margin-top: 30px;
            display: none;
        }
        .section {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .section h3 {
            color: #2c3e50;
            margin-top: 0;
            border-bottom: 2px solid #3498db;
            padding-bottom: 10px;
        }
        .specs-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .spec-item {
            background: white;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #3498db;
        }
        .spec-label {
            font-weight: bold;
            color: #34495e;
        }
        .spec-value {
            color: #2c3e50;
            margin-top: 5px;
        }
        .parts-category {
            margin-bottom: 20px;
        }
        .parts-category h4 {
            color: #27ae60;
            margin-bottom: 15px;
            background: #e8f5e8;
            padding: 10px;
            border-radius: 5px;
        }
        .part-item {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #27ae60;
        }
        .part-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }
        .part-name {
            font-weight: bold;
            color: #2c3e50;
        }
        .part-number {
            color: #7f8c8d;
            font-family: monospace;
        }
        .part-details {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 10px;
            margin-top: 10px;
        }
        .detail-item {
            background: #f8f9fa;
            padding: 8px;
            border-radius: 3px;
        }
        .detail-label {
            font-weight: bold;
            color: #34495e;
            font-size: 0.9em;
        }
        .detail-value {
            color: #2c3e50;
            margin-top: 3px;
        }
        .maintenance-schedule {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 15px;
            margin-top: 15px;
        }
        .maintenance-item {
            background: white;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #e74c3c;
        }
        .maintenance-interval {
            font-weight: bold;
            color: #e74c3c;
            margin-bottom: 10px;
        }
        .services-list {
            list-style: none;
            padding: 0;
        }
        .services-list li {
            background: #f8f9fa;
            padding: 5px 10px;
            margin: 5px 0;
            border-radius: 3px;
            border-left: 3px solid #e74c3c;
        }
        .error {
            background-color: #f8d7da;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin-top: 20px;
        }
        .loading {
            text-align: center;
            color: #7f8c8d;
            margin: 20px 0;
        }
        .japanese-brands {
            background-color: #fff3cd;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .japanese-brands h3 {
            color: #856404;
            margin-top: 0;
        }
        .tabs {
            display: flex;
            border-bottom: 2px solid #ddd;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            cursor: pointer;
            border: none;
            background: none;
            color: #7f8c8d;
            font-weight: bold;
        }
        .tab.active {
            color: #3498db;
            border-bottom: 2px solid #3498db;
        }
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        .recalls-section {
            background-color: #fff5f5;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }
        .recall-item {
            background: white;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #e74c3c;
        }
        .issues-section {
            background-color: #fff8e1;
            padding: 15px;
            border-radius: 5px;
            margin-top: 15px;
        }
        .issue-item {
            background: white;
            padding: 10px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #ff9800;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 Enhanced Japanese Car VIN Decoder & Parts Identifier</h1>
        
        <div class="japanese-brands">
            <h3>Supported Japanese Manufacturers:</h3>
            <p>Toyota, Honda, Nissan, Mazda, Mitsubishi, Subaru, Suzuki, Isuzu, Daihatsu, Lexus, Acura, Infiniti, Scion, Datsun</p>
        </div>
        
        <div class="input-section">
            <div class="form-group">
                <label for="vin">Vehicle Identification Number (VIN):</label>
                <input type="text" id="vin" name="vin" placeholder="Enter 17-character VIN (e.g., 1NXBR32E85Z123456)" maxlength="17">
            </div>
            <button onclick="decodeVIN()">🔍 Decode VIN & Get Comprehensive Information</button>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            Decoding VIN and gathering comprehensive vehicle information...
        </div>
        
        <div id="results" class="results">
            <div class="tabs">
                <button class="tab active" onclick="showTab('overview')">Overview</button>
                <button class="tab" onclick="showTab('specifications')">Specifications</button>
                <button class="tab" onclick="showTab('parts')">Parts</button>
                <button class="tab" onclick="showTab('maintenance')">Maintenance</button>
                <button class="tab" onclick="showTab('issues')">Issues & Recalls</button>
            </div>
            
            <div id="overview" class="tab-content active">
                <div class="section">
                    <h3>🚙 Vehicle Information</h3>
                    <div id="vehicle-details"></div>
                </div>
            </div>
            
            <div id="specifications" class="tab-content">
                <div class="section">
                    <h3>📊 Vehicle Specifications</h3>
                    <div id="specifications-details"></div>
                </div>
            </div>
            
            <div id="parts" class="tab-content">
                <div class="section">
                    <h3>🔧 Compatible Parts</h3>
                    <div id="parts-details"></div>
                </div>
            </div>
            
            <div id="maintenance" class="tab-content">
                <div class="section">
                    <h3>🔧 Maintenance Schedule</h3>
                    <div id="maintenance-details"></div>
                </div>
            </div>
            
            <div id="issues" class="tab-content">
                <div class="section">
                    <h3>⚠️ Issues & Recalls</h3>
                    <div id="issues-details"></div>
                </div>
            </div>
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
    </div>

    <script>
        let currentVehicleInfo = null;
        
        async function decodeVIN() {
            const vin = document.getElementById('vin').value.trim();
            
            if (!vin) {
                showError('Please enter a VIN');
                return;
            }
            
            if (vin.length !== 17) {
                showError('VIN must be exactly 17 characters long');
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').style.display = 'none';
            document.getElementById('error').style.display = 'none';
            
            try {
                const response = await fetch('/decode', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ vin: vin })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    currentVehicleInfo = data.vehicle_info;
                    displayResults(data.vehicle_info);
                } else {
                    showError(data.error || 'Failed to decode VIN');
                }
            } catch (error) {
                showError('Network error: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function showTab(tabName) {
            // Hide all tab contents
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Remove active class from all tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            // Show selected tab content
            document.getElementById(tabName).classList.add('active');
            
            // Add active class to clicked tab
            event.target.classList.add('active');
            
            // Update content based on tab
            if (currentVehicleInfo) {
                switch(tabName) {
                    case 'overview':
                        displayVehicleOverview(currentVehicleInfo);
                        break;
                    case 'specifications':
                        displaySpecifications(currentVehicleInfo);
                        break;
                    case 'parts':
                        displayParts(currentVehicleInfo);
                        break;
                    case 'maintenance':
                        displayMaintenance(currentVehicleInfo);
                        break;
                    case 'issues':
                        displayIssues(currentVehicleInfo);
                        break;
                }
            }
        }
        
        function displayResults(vehicleInfo) {
            displayVehicleOverview(vehicleInfo);
            displaySpecifications(vehicleInfo);
            displayParts(vehicleInfo);
            displayMaintenance(vehicleInfo);
            displayIssues(vehicleInfo);
            
            // Show results
            document.getElementById('results').style.display = 'block';
        }
        
        function displayVehicleOverview(vehicleInfo) {
            const vehicleDetails = document.getElementById('vehicle-details');
            vehicleDetails.innerHTML = `
                <div class="specs-grid">
                    <div class="spec-item">
                        <div class="spec-label">Make</div>
                        <div class="spec-value">${vehicleInfo.make || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Model</div>
                        <div class="spec-value">${vehicleInfo.model || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Year</div>
                        <div class="spec-value">${vehicleInfo.year || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Engine</div>
                        <div class="spec-value">${vehicleInfo.engine || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Engine Code</div>
                        <div class="spec-value">${vehicleInfo.engine_code || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Transmission</div>
                        <div class="spec-value">${vehicleInfo.transmission || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Body Style</div>
                        <div class="spec-value">${vehicleInfo.body_style || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Fuel Type</div>
                        <div class="spec-value">${vehicleInfo.fuel_type || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Drive Type</div>
                        <div class="spec-value">${vehicleInfo.drive_type || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Doors</div>
                        <div class="spec-value">${vehicleInfo.doors || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Seats</div>
                        <div class="spec-value">${vehicleInfo.seats || 'N/A'}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">Safety Features</div>
                        <div class="spec-value">${(vehicleInfo.safety_features || []).join(', ') || 'N/A'}</div>
                    </div>
                </div>
            `;
        }
        
        function displaySpecifications(vehicleInfo) {
            const specsDetails = document.getElementById('specifications-details');
            
            if (vehicleInfo.specifications) {
                const specs = vehicleInfo.specifications;
                specsDetails.innerHTML = `
                    <div class="specs-grid">
                        <div class="spec-item">
                            <div class="spec-label">Engine Displacement</div>
                            <div class="spec-value">${specs.engine_displacement || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Horsepower</div>
                            <div class="spec-value">${specs.horsepower || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Torque</div>
                            <div class="spec-value">${specs.torque || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Fuel Capacity</div>
                            <div class="spec-value">${specs.fuel_capacity || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Oil Capacity</div>
                            <div class="spec-value">${specs.oil_capacity || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Transmission Fluid</div>
                            <div class="spec-value">${specs.transmission_fluid_capacity || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Coolant Capacity</div>
                            <div class="spec-value">${specs.coolant_capacity || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Brake Fluid Type</div>
                            <div class="spec-value">${specs.brake_fluid_type || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Tire Size</div>
                            <div class="spec-value">${specs.tire_size || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Wheel Size</div>
                            <div class="spec-value">${specs.wheel_size || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Weight</div>
                            <div class="spec-value">${specs.weight || 'N/A'}</div>
                        </div>
                        <div class="spec-item">
                            <div class="spec-label">Towing Capacity</div>
                            <div class="spec-value">${specs.towing_capacity || 'N/A'}</div>
                        </div>
                    </div>
                    ${specs.dimensions ? `
                    <h4>Dimensions</h4>
                    <div class="specs-grid">
                        ${Object.entries(specs.dimensions).map(([key, value]) => `
                            <div class="spec-item">
                                <div class="spec-label">${key.charAt(0).toUpperCase() + key.slice(1)}</div>
                                <div class="spec-value">${value}</div>
                            </div>
                        `).join('')}
                    </div>
                    ` : ''}
                `;
            } else {
                specsDetails.innerHTML = '<p>No detailed specifications available for this vehicle.</p>';
            }
        }
        
        function displayParts(vehicleInfo) {
            const partsDetails = document.getElementById('parts-details');
            let partsHTML = '';
            
            for (const [category, parts] of Object.entries(vehicleInfo.parts_compatibility)) {
                if (parts && parts.length > 0) {
                    partsHTML += `
                        <div class="parts-category">
                            <h4>${category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}</h4>
                            ${parts.map(part => `
                                <div class="part-item">
                                    <div class="part-header">
                                        <div class="part-name">${part.part_name}</div>
                                        <div class="part-number">${part.part_number || 'Generic'}</div>
                                    </div>
                                    <div class="part-details">
                                        <div class="detail-item">
                                            <div class="detail-label">Brand</div>
                                            <div class="detail-value">${part.brand || 'Various'}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">Price Range</div>
                                            <div class="detail-value">${part.price_range || 'Varies'}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">Maintenance Interval</div>
                                            <div class="detail-value">${part.maintenance_interval || 'Varies'}</div>
                                        </div>
                                        <div class="detail-item">
                                            <div class="detail-label">Compatibility</div>
                                            <div class="detail-value">${part.compatibility_notes || 'Fits this vehicle'}</div>
                                        </div>
                                    </div>
                                    ${part.alternatives && part.alternatives.length > 0 ? `
                                        <div style="margin-top: 10px;">
                                            <strong>Alternatives:</strong> ${part.alternatives.join(', ')}
                                        </div>
                                    ` : ''}
                                </div>
                            `).join('')}
                        </div>
                    `;
                }
            }
            
            if (partsHTML === '') {
                partsHTML = '<p>No specific parts compatibility information available for this vehicle.</p>';
            }
            
            partsDetails.innerHTML = partsHTML;
        }
        
        function displayMaintenance(vehicleInfo) {
            const maintenanceDetails = document.getElementById('maintenance-details');
            
            if (vehicleInfo.maintenance_schedule && Object.keys(vehicleInfo.maintenance_schedule).length > 0) {
                let maintenanceHTML = '<div class="maintenance-schedule">';
                
                for (const [interval, schedule] of Object.entries(vehicleInfo.maintenance_schedule)) {
                    maintenanceHTML += `
                        <div class="maintenance-item">
                            <div class="maintenance-interval">${schedule.interval_miles} miles / ${schedule.interval_months} months</div>
                            <div><strong>Services:</strong></div>
                            <ul class="services-list">
                                ${schedule.services.map(service => `<li>${service}</li>`).join('')}
                            </ul>
                            <div><strong>Parts Needed:</strong> ${schedule.parts_needed.join(', ')}</div>
                            <div><strong>Estimated Cost:</strong> ${schedule.estimated_cost}</div>
                        </div>
                    `;
                }
                
                maintenanceHTML += '</div>';
                maintenanceDetails.innerHTML = maintenanceHTML;
            } else {
                maintenanceDetails.innerHTML = '<p>No maintenance schedule available for this vehicle.</p>';
            }
        }
        
        function displayIssues(vehicleInfo) {
            const issuesDetails = document.getElementById('issues-details');
            let issuesHTML = '';
            
            if (vehicleInfo.recalls && vehicleInfo.recalls.length > 0) {
                issuesHTML += `
                    <div class="recalls-section">
                        <h4>🚨 Recalls (${vehicleInfo.recalls.length})</h4>
                        ${vehicleInfo.recalls.map(recall => `
                            <div class="recall-item">
                                <div><strong>Recall #:</strong> ${recall.recall_number}</div>
                                <div><strong>Issue:</strong> ${recall.issue}</div>
                                <div><strong>Date:</strong> ${recall.date}</div>
                                <div><strong>Status:</strong> ${recall.status}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            if (vehicleInfo.common_issues && vehicleInfo.common_issues.length > 0) {
                issuesHTML += `
                    <div class="issues-section">
                        <h4>⚠️ Common Issues (${vehicleInfo.common_issues.length})</h4>
                        ${vehicleInfo.common_issues.map(issue => `
                            <div class="issue-item">
                                <div>${issue}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            if (vehicleInfo.service_bulletins && vehicleInfo.service_bulletins.length > 0) {
                issuesHTML += `
                    <div class="issues-section">
                        <h4>📋 Service Bulletins (${vehicleInfo.service_bulletins.length})</h4>
                        ${vehicleInfo.service_bulletins.map(bulletin => `
                            <div class="issue-item">
                                <div>${bulletin}</div>
                            </div>
                        `).join('')}
                    </div>
                `;
            }
            
            if (issuesHTML === '') {
                issuesHTML = '<p>No recalls, common issues, or service bulletins found for this vehicle.</p>';
            }
            
            issuesDetails.innerHTML = issuesHTML;
        }
        
        function showError(message) {
            const errorDiv = document.getElementById('error');
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
        }
        
        // Allow Enter key to submit
        document.getElementById('vin').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                decodeVIN();
            }
        });
    </script>
</body>
</html>
        '''

def start_server(port=5001):
    """Start the enhanced HTTP server"""
    with socketserver.TCPServer(("", port), EnhancedVINDecoderHandler) as httpd:
        print(f"🚗 Starting Enhanced Japanese Car VIN Decoder Web Interface...")
        print(f"📱 Open your browser and go to: http://localhost:{port}")
        print(f"🔧 Enhanced API endpoints available at:")
        print(f"   - GET /api/vehicle/<vin>")
        print(f"   - GET /api/parts/<vin>")
        print(f"   - GET /api/specifications/<vin>")
        print(f"   - GET /api/maintenance/<vin>")
        print(f"   - POST /decode")
        print(f"🛑 Press Ctrl+C to stop the server")
        httpd.serve_forever()

if __name__ == '__main__':
    try:
        start_server()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting server: {e}")
