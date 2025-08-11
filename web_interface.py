#!/usr/bin/env python3
"""
Web Interface for Japanese Car VIN Decoder
==========================================

A Flask web application that provides a user-friendly interface for the VIN decoder.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from enhanced_vin_decoder import EnhancedJapaneseCarVINDecoder, PartInformation

app = Flask(__name__)
CORS(app)

# Initialize the enhanced VIN decoder
decoder = EnhancedJapaneseCarVINDecoder()

def convert_parts_to_dict(parts_compatibility):
    """Convert PartInformation objects to dictionaries for JSON serialization"""
    result = {}
    
    for category, parts in parts_compatibility.items():
        if isinstance(parts, dict):
            # Enhanced parts with PartInformation objects
            result[category] = {}
            for part_key, part_info in parts.items():
                if isinstance(part_info, PartInformation):
                    result[category][part_key] = {
                        'name': part_info.part_name,
                        'part_number': part_info.part_number,
                        'brand': part_info.brand,
                        'price_range': part_info.price_range,
                        'compatibility_notes': part_info.compatibility_notes,
                        'maintenance_interval': part_info.maintenance_interval,
                        'specifications': part_info.specifications or {},
                        'alternatives': part_info.alternatives or []
                    }
                else:
                    result[category][part_key] = str(part_info)
        elif isinstance(parts, list):
            # Basic parts list
            result[category] = []
            for part in parts:
                if isinstance(part, PartInformation):
                    result[category].append({
                        'name': part.part_name,
                        'part_number': part.part_number,
                        'brand': part.brand,
                        'price_range': part.price_range,
                        'compatibility_notes': part.compatibility_notes,
                        'maintenance_interval': part.maintenance_interval,
                        'specifications': part.specifications or {},
                        'alternatives': part.alternatives or []
                    })
                else:
                    result[category].append(str(part))
        else:
            result[category] = str(parts)
    
    return result

@app.route('/')
def index():
    """Main page with VIN decoder interface"""
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
                    if (parts && Object.keys(parts).length > 0) {
                        partsHTML += `
                            <div class="parts-category">
                                <h4>${category.charAt(0).toUpperCase() + category.slice(1).replace('_', ' ')}</h4>
                                <div class="parts-list">
                        `;
                        
                        // Handle both enhanced parts (objects) and basic parts (arrays)
                        if (Array.isArray(parts)) {
                            // Basic parts format
                            parts.forEach(part => {
                                if (typeof part === 'object' && part.name) {
                                    // Enhanced part object
                                    partsHTML += `
                                        <div class="part-item">
                                            <h5>${part.name}</h5>
                                            <p><strong>Part #:</strong> ${part.part_number}</p>
                                            <p><strong>Brand:</strong> ${part.brand}</p>
                                            <p><strong>Price:</strong> ${part.price_range}</p>
                                            <p><strong>Maintenance:</strong> ${part.maintenance_interval}</p>
                                            ${part.alternatives && part.alternatives.length > 0 ? 
                                                `<p><strong>Alternatives:</strong> ${part.alternatives.join(', ')}</p>` : ''}
                                        </div>
                                    `;
                                } else {
                                    // Basic part string
                                    partsHTML += `<li>${part.replace('_', ' ')}</li>`;
                                }
                            });
                        } else if (typeof parts === 'object') {
                            // Enhanced parts object format
                            for (const [partKey, partInfo] of Object.entries(parts)) {
                                if (typeof partInfo === 'object' && partInfo.name) {
                                    partsHTML += `
                                        <div class="part-item" style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #28a745;">
                                            <h5 style="color: #28a745; margin: 0 0 10px 0;">${partInfo.name}</h5>
                                            <p style="margin: 5px 0;"><strong>Part Number:</strong> ${partInfo.part_number}</p>
                                            <p style="margin: 5px 0;"><strong>Brand:</strong> ${partInfo.brand}</p>
                                            <p style="margin: 5px 0;"><strong>Price Range:</strong> ${partInfo.price_range}</p>
                                            <p style="margin: 5px 0;"><strong>Maintenance:</strong> ${partInfo.maintenance_interval}</p>
                                            ${partInfo.compatibility_notes ? 
                                                `<p style="margin: 5px 0;"><strong>Notes:</strong> ${partInfo.compatibility_notes}</p>` : ''}
                                            ${partInfo.alternatives && partInfo.alternatives.length > 0 ? 
                                                `<p style="margin: 5px 0;"><strong>Alternatives:</strong> ${partInfo.alternatives.slice(0, 3).join(', ')}</p>` : ''}
                                        </div>
                                    `;
                                } else {
                                    partsHTML += `<li style="padding: 8px 0;">${partKey.replace('_', ' ')}</li>`;
                                }
                            }
                        }
                        
                        partsHTML += `
                                </div>
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

@app.route('/decode', methods=['POST'])
def decode_vin():
    """API endpoint to decode VIN"""
    try:
        data = request.get_json()
        vin = data.get('vin', '').strip()
        
        if not vin:
            return jsonify({'success': False, 'error': 'VIN is required'})
        
        # Decode the VIN
        vehicle_info = decoder.decode_vin(vin)
        
        if vehicle_info:
            # Convert EnhancedVehicleInfo object to dictionary
            vehicle_dict = {
                'vin': vehicle_info.vin,
                'make': vehicle_info.make,
                'model': vehicle_info.model,
                'year': vehicle_info.year,
                'engine': vehicle_info.engine,
                'engine_code': vehicle_info.engine_code,
                'transmission': vehicle_info.transmission,
                'transmission_code': vehicle_info.transmission_code,
                'body_style': vehicle_info.body_style,
                'trim': vehicle_info.trim,
                'fuel_type': vehicle_info.fuel_type,
                'drive_type': vehicle_info.drive_type,
                'doors': vehicle_info.doors,
                'seats': vehicle_info.seats,
                'safety_features': vehicle_info.safety_features or [],
                'standard_features': vehicle_info.standard_features or [],
                'optional_features': vehicle_info.optional_features or [],
                'parts_compatibility': convert_parts_to_dict(vehicle_info.parts_compatibility),
                'specifications': {
                    'engine_displacement': vehicle_info.specifications.engine_displacement if vehicle_info.specifications else '',
                    'horsepower': vehicle_info.specifications.horsepower if vehicle_info.specifications else '',
                    'torque': vehicle_info.specifications.torque if vehicle_info.specifications else '',
                    'fuel_capacity': vehicle_info.specifications.fuel_capacity if vehicle_info.specifications else '',
                    'oil_capacity': vehicle_info.specifications.oil_capacity if vehicle_info.specifications else '',
                    'weight': vehicle_info.specifications.weight if vehicle_info.specifications else '',
                    'dimensions': vehicle_info.specifications.dimensions if vehicle_info.specifications else {}
                },
                'maintenance_schedule': {
                    interval: {
                        'interval_miles': schedule.interval_miles,
                        'interval_months': schedule.interval_months,
                        'services': schedule.services or [],
                        'parts_needed': schedule.parts_needed or [],
                        'estimated_cost': schedule.estimated_cost
                    }
                    for interval, schedule in (vehicle_info.maintenance_schedule or {}).items()
                },
                'recalls': vehicle_info.recalls or [],
                'common_issues': vehicle_info.common_issues or [],
                'service_bulletins': vehicle_info.service_bulletins or []
            }
            
            return jsonify({
                'success': True,
                'vehicle_info': vehicle_dict
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not decode VIN. Please check if the VIN is valid.'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@app.route('/api/vehicle/<vin>')
def api_decode_vin(vin):
    """REST API endpoint for VIN decoding"""
    try:
        vehicle_info = decoder.decode_vin(vin)
        
        if vehicle_info:
            vehicle_dict = {
                'vin': vehicle_info.vin,
                'make': vehicle_info.make,
                'model': vehicle_info.model,
                'year': vehicle_info.year,
                'engine': vehicle_info.engine,
                'engine_code': vehicle_info.engine_code,
                'transmission': vehicle_info.transmission,
                'body_style': vehicle_info.body_style,
                'trim': vehicle_info.trim,
                'fuel_type': vehicle_info.fuel_type,
                'drive_type': vehicle_info.drive_type,
                'doors': vehicle_info.doors,
                'seats': vehicle_info.seats,
                'safety_features': vehicle_info.safety_features or [],
                'parts_compatibility': convert_parts_to_dict(vehicle_info.parts_compatibility),
                'specifications': {
                    'engine_displacement': vehicle_info.specifications.engine_displacement if vehicle_info.specifications else '',
                    'horsepower': vehicle_info.specifications.horsepower if vehicle_info.specifications else '',
                    'torque': vehicle_info.specifications.torque if vehicle_info.specifications else ''
                } if vehicle_info.specifications else {}
            }
            
            return jsonify({
                'success': True,
                'vehicle': vehicle_dict
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not decode VIN'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

@app.route('/api/parts/<vin>')
def api_get_parts(vin):
    """REST API endpoint for parts compatibility"""
    try:
        vehicle_info = decoder.decode_vin(vin)
        
        if vehicle_info:
            search_results = decoder.search_parts_by_vehicle(vehicle_info)
            
            return jsonify({
                'success': True,
                'parts_search': search_results
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Could not decode VIN'
            }), 400
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = 5001
    print("🚗 Starting Japanese Car VIN Decoder Web Interface...")
    print(f"📱 Open your browser and go to: http://localhost:{port}")
    print("🔧 API endpoints available at:")
    print("   - GET /api/vehicle/<vin>")
    print("   - GET /api/parts/<vin>")
    print("   - POST /decode")
    print()
    print("🎯 Test with this working VIN: 4T1BE32K25U123456 (2005 Toyota Camry)")
    print("   This will show detailed parts information!")
    app.run(debug=True, host='0.0.0.0', port=port)
