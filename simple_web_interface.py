#!/usr/bin/env python3
"""
Simple Web Interface for Japanese Car VIN Decoder
=================================================

A simple web application using Python's built-in HTTP server.
"""

import http.server
import socketserver
import json
import urllib.parse
from japanese_car_vin_decoder import JapaneseCarVINDecoder
import threading
import time

# Initialize the VIN decoder
decoder = JapaneseCarVINDecoder()

class VINDecoderHandler(http.server.SimpleHTTPRequestHandler):
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
                vehicle_dict = {
                    'vin': vehicle_info.vin,
                    'make': vehicle_info.make,
                    'model': vehicle_info.model,
                    'year': vehicle_info.year,
                    'engine': vehicle_info.engine,
                    'transmission': vehicle_info.transmission,
                    'body_style': vehicle_info.body_style,
                    'trim': vehicle_info.trim,
                    'fuel_type': vehicle_info.fuel_type,
                    'drive_type': vehicle_info.drive_type,
                    'doors': vehicle_info.doors,
                    'seats': vehicle_info.seats,
                    'safety_features': vehicle_info.safety_features,
                    'parts_compatibility': vehicle_info.parts_compatibility
                }
                response = {'success': True, 'vehicle': vehicle_dict}
            else:
                response = {'success': False, 'error': 'Could not decode VIN'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())

    def handle_api_parts(self, vin):
        try:
            vehicle_info = decoder.decode_vin(vin)
            if vehicle_info:
                search_results = decoder.search_parts_by_vehicle(vehicle_info)
                # Convert VehicleInfo object to dict for JSON serialization
                vehicle_dict = {
                    'vin': vehicle_info.vin,
                    'make': vehicle_info.make,
                    'model': vehicle_info.model,
                    'year': vehicle_info.year,
                    'engine': vehicle_info.engine,
                    'transmission': vehicle_info.transmission,
                    'body_style': vehicle_info.body_style,
                    'trim': vehicle_info.trim,
                    'fuel_type': vehicle_info.fuel_type,
                    'drive_type': vehicle_info.drive_type,
                    'doors': vehicle_info.doors,
                    'seats': vehicle_info.seats,
                    'safety_features': vehicle_info.safety_features,
                    'parts_compatibility': vehicle_info.parts_compatibility
                }
                search_results['vehicle'] = vehicle_dict
                response = {'success': True, 'parts_search': search_results}
            else:
                response = {'success': False, 'error': 'Could not decode VIN'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())

    def handle_decode_vin(self, vin):
        try:
            vehicle_info = decoder.decode_vin(vin)
            if vehicle_info:
                vehicle_dict = {
                    'vin': vehicle_info.vin,
                    'make': vehicle_info.make,
                    'model': vehicle_info.model,
                    'year': vehicle_info.year,
                    'engine': vehicle_info.engine,
                    'transmission': vehicle_info.transmission,
                    'body_style': vehicle_info.body_style,
                    'trim': vehicle_info.trim,
                    'fuel_type': vehicle_info.fuel_type,
                    'drive_type': vehicle_info.drive_type,
                    'doors': vehicle_info.doors,
                    'seats': vehicle_info.seats,
                    'safety_features': vehicle_info.safety_features,
                    'parts_compatibility': vehicle_info.parts_compatibility
                }
                response = {'success': True, 'vehicle_info': vehicle_dict}
            else:
                response = {'success': False, 'error': 'Could not decode VIN'}
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode())
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode())

    def get_html_content(self):
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Japanese Car VIN Decoder</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
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
        .vehicle-info {
            background-color: #ecf0f1;
            padding: 20px;
            border-radius: 5px;
            margin-bottom: 20px;
        }
        .parts-section {
            background-color: #e8f5e8;
            padding: 20px;
            border-radius: 5px;
        }
        .parts-category {
            margin-bottom: 15px;
        }
        .parts-category h4 {
            color: #27ae60;
            margin-bottom: 10px;
        }
        .parts-list {
            list-style: none;
            padding: 0;
        }
        .parts-list li {
            background-color: white;
            padding: 8px 12px;
            margin: 5px 0;
            border-radius: 3px;
            border-left: 4px solid #27ae60;
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
    </style>
</head>
<body>
    <div class="container">
        <h1>🚗 Japanese Car VIN Decoder & Parts Identifier</h1>
        
        <div class="japanese-brands">
            <h3>Supported Japanese Manufacturers:</h3>
            <p>Toyota, Honda, Nissan, Mazda, Mitsubishi, Subaru, Suzuki, Isuzu, Daihatsu, Lexus, Acura, Infiniti, Scion, Datsun</p>
        </div>
        
        <div class="input-section">
            <div class="form-group">
                <label for="vin">Vehicle Identification Number (VIN):</label>
                <input type="text" id="vin" name="vin" placeholder="Enter 17-character VIN (e.g., 1HGBH41JXMN109186)" maxlength="17">
            </div>
            <button onclick="decodeVIN()">🔍 Decode VIN & Find Parts</button>
        </div>
        
        <div id="loading" class="loading" style="display: none;">
            Decoding VIN and identifying compatible parts...
        </div>
        
        <div id="results" class="results">
            <div class="vehicle-info">
                <h3>🚙 Vehicle Information</h3>
                <div id="vehicle-details"></div>
            </div>
            
            <div class="parts-section">
                <h3>🔧 Compatible Parts</h3>
                <div id="parts-details"></div>
            </div>
        </div>
        
        <div id="error" class="error" style="display: none;"></div>
    </div>

    <script>
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
        
        function displayResults(vehicleInfo) {
            // Display vehicle information
            const vehicleDetails = document.getElementById('vehicle-details');
            vehicleDetails.innerHTML = `
                <p><strong>Make:</strong> ${vehicleInfo.make || 'N/A'}</p>
                <p><strong>Model:</strong> ${vehicleInfo.model || 'N/A'}</p>
                <p><strong>Year:</strong> ${vehicleInfo.year || 'N/A'}</p>
                <p><strong>Engine:</strong> ${vehicleInfo.engine || 'N/A'}</p>
                <p><strong>Transmission:</strong> ${vehicleInfo.transmission || 'N/A'}</p>
                <p><strong>Body Style:</strong> ${vehicleInfo.body_style || 'N/A'}</p>
                <p><strong>Fuel Type:</strong> ${vehicleInfo.fuel_type || 'N/A'}</p>
                <p><strong>Drive Type:</strong> ${vehicleInfo.drive_type || 'N/A'}</p>
                <p><strong>Safety Features:</strong> ${vehicleInfo.safety_features.join(', ') || 'N/A'}</p>
            `;
            
            // Display parts compatibility
            const partsDetails = document.getElementById('parts-details');
            let partsHTML = '';
            
            for (const [category, parts] of Object.entries(vehicleInfo.parts_compatibility)) {
                if (parts && parts.length > 0) {
                    partsHTML += `
                        <div class="parts-category">
                            <h4>${category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}</h4>
                            <ul class="parts-list">
                                ${parts.map(part => `<li>${part.replace('_', ' ')}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                }
            }
            
            if (partsHTML === '') {
                partsHTML = '<p>No specific parts compatibility information available for this vehicle.</p>';
            }
            
            partsDetails.innerHTML = partsHTML;
            
            // Show results
            document.getElementById('results').style.display = 'block';
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

def start_server(port=5000):
    """Start the HTTP server"""
    with socketserver.TCPServer(("", port), VINDecoderHandler) as httpd:
        print(f"🚗 Starting Japanese Car VIN Decoder Web Interface...")
        print(f"📱 Open your browser and go to: http://localhost:{port}")
        print(f"🔧 API endpoints available at:")
        print(f"   - GET /api/vehicle/<vin>")
        print(f"   - GET /api/parts/<vin>")
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
