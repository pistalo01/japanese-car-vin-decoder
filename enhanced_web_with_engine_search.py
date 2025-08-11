#!/usr/bin/env python3
"""
Enhanced Web Interface with Engine Search Support
=================================================

Supports both VIN and Engine Code searches with detailed parts information.
"""

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json
from engine_search_enhanced import EnhancedEngineVINDecoder, PartInformation

app = Flask(__name__)
CORS(app)

# Initialize the enhanced decoder with engine search
decoder = EnhancedEngineVINDecoder()

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
    """Main page with enhanced VIN/Engine decoder interface"""
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Japanese Car VIN & Engine Decoder</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            }
            h1 {
                color: #2c3e50;
                text-align: center;
                margin-bottom: 10px;
                font-size: 2.5em;
            }
            .subtitle {
                text-align: center;
                color: #7f8c8d;
                margin-bottom: 30px;
                font-size: 1.2em;
            }
            .search-modes {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
                gap: 20px;
            }
            .mode-btn {
                padding: 10px 20px;
                border: 2px solid #3498db;
                background: white;
                color: #3498db;
                border-radius: 25px;
                cursor: pointer;
                transition: all 0.3s ease;
                font-weight: bold;
            }
            .mode-btn.active {
                background: #3498db;
                color: white;
            }
            .mode-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(52, 152, 219, 0.3);
            }
            .input-section {
                margin-bottom: 30px;
            }
            .form-group {
                margin-bottom: 20px;
            }
            label {
                display: block;
                margin-bottom: 8px;
                font-weight: bold;
                color: #34495e;
                font-size: 1.1em;
            }
            input[type="text"] {
                width: 100%;
                padding: 15px;
                border: 2px solid #ddd;
                border-radius: 8px;
                font-size: 16px;
                box-sizing: border-box;
                transition: border-color 0.3s ease;
            }
            input[type="text"]:focus {
                border-color: #3498db;
                outline: none;
                box-shadow: 0 0 10px rgba(52, 152, 219, 0.2);
            }
            button {
                background: linear-gradient(135deg, #3498db, #2ecc71);
                color: white;
                padding: 15px 30px;
                border: none;
                border-radius: 8px;
                cursor: pointer;
                font-size: 18px;
                font-weight: bold;
                width: 100%;
                transition: all 0.3s ease;
            }
            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 25px rgba(52, 152, 219, 0.3);
            }
            .examples {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
                border-left: 4px solid #3498db;
            }
            .examples h3 {
                margin-top: 0;
                color: #2c3e50;
            }
            .example-item {
                margin: 10px 0;
                padding: 8px 12px;
                background: white;
                border-radius: 5px;
                cursor: pointer;
                transition: all 0.2s ease;
            }
            .example-item:hover {
                background: #e3f2fd;
                transform: translateX(5px);
            }
            .results {
                margin-top: 30px;
                display: none;
            }
            .vehicle-info, .engine-info {
                background: #ecf0f1;
                padding: 25px;
                border-radius: 8px;
                margin-bottom: 25px;
            }
            .parts-section {
                background: #e8f5e8;
                padding: 25px;
                border-radius: 8px;
            }
            .part-item {
                background: #f8f9fa;
                padding: 15px;
                margin: 15px 0;
                border-radius: 8px;
                border-left: 4px solid #28a745;
            }
            .part-item h5 {
                color: #28a745;
                margin: 0 0 10px 0;
                font-size: 1.2em;
            }
            .part-detail {
                margin: 8px 0;
                padding: 5px 0;
            }
            .error {
                background: #f8d7da;
                color: #721c24;
                padding: 20px;
                border-radius: 8px;
                margin-top: 20px;
                border-left: 4px solid #dc3545;
            }
            .loading {
                text-align: center;
                color: #7f8c8d;
                margin: 20px 0;
                font-size: 1.1em;
            }
            .search-type-indicator {
                background: #17a2b8;
                color: white;
                padding: 10px 20px;
                border-radius: 25px;
                display: inline-block;
                margin-bottom: 15px;
                font-weight: bold;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚗 Japanese Car VIN & Engine Decoder</h1>
            <p class="subtitle">Universal search for VINs and Engine Codes with detailed parts database</p>
            
            <div class="examples">
                <h3>📋 Try These Examples:</h3>
                <div class="example-item" onclick="setSearchValue('4T1BE32K25U123456')">
                    <strong>VIN:</strong> 4T1BE32K25U123456 → 2005 Toyota Camry (Full Parts DB)
                </div>
                <div class="example-item" onclick="setSearchValue('D16W73005025')">
                    <strong>Engine:</strong> D16W73005025 → Honda D16W7 VTEC (Your Original Input)
                </div>
                <div class="example-item" onclick="setSearchValue('D16W7')">
                    <strong>Engine:</strong> D16W7 → Honda Civic SOHC VTEC 1.6L
                </div>
                <div class="example-item" onclick="setSearchValue('1HGEM21503L123456')">
                    <strong>VIN:</strong> 1HGEM21503L123456 → 2003 Honda Civic
                </div>
            </div>
            
            <div class="input-section">
                <div class="form-group">
                    <label for="searchInput">Enter VIN (17 characters) or Engine Code:</label>
                    <input type="text" id="searchInput" name="searchInput" placeholder="e.g., 4T1BE32K25U123456 or D16W7 or D16W73005025">
                </div>
                <button onclick="performSearch()">🔍 Search Vehicle or Engine Data</button>
            </div>
            
            <div id="loading" class="loading" style="display: none;">
                🔄 Searching database for vehicle and parts information...
            </div>
            
            <div id="results" class="results">
                <div id="search-type" class="search-type-indicator"></div>
                <div id="vehicle-details"></div>
                <div id="engine-details"></div>
                <div id="parts-details"></div>
            </div>
            
            <div id="error" class="error" style="display: none;"></div>
        </div>

        <script>
            function setSearchValue(value) {
                document.getElementById('searchInput').value = value;
                performSearch();
            }

            async function performSearch() {
                const searchInput = document.getElementById('searchInput').value.trim();
                
                if (!searchInput) {
                    showError('Please enter a VIN or engine code');
                    return;
                }
                
                // Show loading
                document.getElementById('loading').style.display = 'block';
                document.getElementById('results').style.display = 'none';
                document.getElementById('error').style.display = 'none';
                
                try {
                    const response = await fetch('/search', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ search_input: searchInput })
                    });
                    
                    const data = await response.json();
                    
                    if (data.success) {
                        displayResults(data);
                    } else {
                        showError(data.error + (data.suggestion ? '<br><br>💡 ' + data.suggestion : ''));
                    }
                } catch (error) {
                    showError('Network error: ' + error.message);
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }
            
            function displayResults(data) {
                const searchType = document.getElementById('search-type');
                const vehicleDetails = document.getElementById('vehicle-details');
                const engineDetails = document.getElementById('engine-details');
                const partsDetails = document.getElementById('parts-details');
                
                if (data.search_type === 'engine_code') {
                    const engineData = data.data;
                    
                    searchType.innerHTML = '🔧 Engine Code Search Result';
                    searchType.style.background = '#28a745';
                    
                    // Display engine information
                    engineDetails.innerHTML = `
                        <div class="engine-info">
                            <h3>🔧 Engine: ${engineData.engine_code}</h3>
                            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 15px;">
                                <div>
                                    <p><strong>Displacement:</strong> ${engineData.engine_info.displacement}</p>
                                    <p><strong>Type:</strong> ${engineData.engine_info.type}</p>
                                    <p><strong>Fuel System:</strong> ${engineData.engine_info.fuel_system}</p>
                                    <p><strong>Compression:</strong> ${engineData.engine_info.compression_ratio}</p>
                                </div>
                                <div>
                                    <p><strong>Max Power:</strong> ${engineData.engine_info.max_power}</p>
                                    <p><strong>Max Torque:</strong> ${engineData.engine_info.max_torque}</p>
                                    <p><strong>Valves/Cylinder:</strong> ${engineData.engine_info.valves_per_cylinder}</p>
                                    <p><strong>Fuel Type:</strong> ${engineData.engine_info.fuel_type}</p>
                                </div>
                            </div>
                            <h4>🚗 Common Vehicles:</h4>
                            ${engineData.engine_info.common_vehicles.map(v => 
                                `<p>• ${v.years} ${v.make} ${v.model}</p>`
                            ).join('')}
                        </div>
                    `;
                    
                    vehicleDetails.innerHTML = '';
                    
                    // Display parts
                    displayPartsForEngine(engineData);
                    
                } else if (data.search_type === 'vin') {
                    const vehicleInfo = data.data;
                    
                    searchType.innerHTML = '🚗 VIN Decode Result';
                    searchType.style.background = '#17a2b8';
                    
                    // Display vehicle information (existing VIN logic)
                    vehicleDetails.innerHTML = `
                        <div class="vehicle-info">
                            <h3>🚙 Vehicle Information</h3>
                            <p><strong>Make:</strong> ${vehicleInfo.make || 'N/A'}</p>
                            <p><strong>Model:</strong> ${vehicleInfo.model || 'N/A'}</p>
                            <p><strong>Year:</strong> ${vehicleInfo.year || 'N/A'}</p>
                            <p><strong>Engine:</strong> ${vehicleInfo.engine || 'N/A'}</p>
                            <p><strong>Transmission:</strong> ${vehicleInfo.transmission || 'N/A'}</p>
                            <p><strong>Body Style:</strong> ${vehicleInfo.body_style || 'N/A'}</p>
                            <p><strong>Fuel Type:</strong> ${vehicleInfo.fuel_type || 'N/A'}</p>
                        </div>
                    `;
                    
                    engineDetails.innerHTML = '';
                    
                    // Display parts (existing VIN logic)
                    displayPartsForVIN(vehicleInfo);
                }
                
                // Show results
                document.getElementById('results').style.display = 'block';
            }
            
            function displayPartsForEngine(engineData) {
                const partsDetails = document.getElementById('parts-details');
                let partsHTML = `
                    <div class="parts-section">
                        <h3>🔧 Compatible Parts (${engineData.total_parts} parts)</h3>
                `;
                
                for (const [category, parts] of Object.entries(engineData.parts_compatibility)) {
                    if (parts && Object.keys(parts).length > 0) {
                        partsHTML += `
                            <h4>${category.replace('_', ' ').toUpperCase()}</h4>
                        `;
                        
                        for (const [partKey, partInfo] of Object.entries(parts)) {
                            partsHTML += `
                                <div class="part-item">
                                    <h5>${partInfo.part_name}</h5>
                                    <div class="part-detail"><strong>Part Number:</strong> ${partInfo.part_number}</div>
                                    <div class="part-detail"><strong>Brand:</strong> ${partInfo.brand}</div>
                                    <div class="part-detail"><strong>Price Range:</strong> ${partInfo.price_range}</div>
                                    <div class="part-detail"><strong>Maintenance:</strong> ${partInfo.maintenance_interval}</div>
                                    ${partInfo.compatibility_notes ? 
                                        `<div class="part-detail"><strong>Notes:</strong> ${partInfo.compatibility_notes}</div>` : ''}
                                    ${partInfo.alternatives && partInfo.alternatives.length > 0 ? 
                                        `<div class="part-detail"><strong>Alternatives:</strong> ${partInfo.alternatives.slice(0, 3).join(', ')}</div>` : ''}
                                </div>
                            `;
                        }
                    }
                }
                
                partsHTML += '</div>';
                partsDetails.innerHTML = partsHTML;
            }
            
            function displayPartsForVIN(vehicleInfo) {
                // Existing VIN parts display logic (simplified for now)
                const partsDetails = document.getElementById('parts-details');
                partsDetails.innerHTML = `
                    <div class="parts-section">
                        <h3>🔧 Compatible Parts</h3>
                        <p>VIN-based parts lookup - showing basic compatibility information.</p>
                        <p>For detailed OEM parts, try the working VIN: 4T1BE32K25U123456</p>
                    </div>
                `;
            }
            
            function showError(message) {
                const errorDiv = document.getElementById('error');
                errorDiv.innerHTML = message;
                errorDiv.style.display = 'block';
                document.getElementById('results').style.display = 'none';
            }
            
            // Allow Enter key to search
            document.getElementById('searchInput').addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    performSearch();
                }
            });
        </script>
    </body>
    </html>
    '''

@app.route('/search', methods=['POST'])
def universal_search():
    """Universal search endpoint for VIN or engine code"""
    try:
        data = request.get_json()
        search_input = data.get('search_input', '').strip()
        
        if not search_input:
            return jsonify({'success': False, 'error': 'Search input is required'})
        
        # Use the enhanced decoder's universal search
        result = decoder.search(search_input)
        
        if result['success'] and result['search_type'] == 'engine_code':
            # Convert PartInformation objects for JSON serialization
            engine_data = result['data']
            if 'parts_compatibility' in engine_data:
                engine_data['parts_compatibility'] = convert_parts_to_dict(engine_data['parts_compatibility'])
        
        return jsonify(result)
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

# Keep existing VIN-only endpoints for backward compatibility
@app.route('/decode', methods=['POST'])
def decode_vin():
    """Legacy VIN-only decode endpoint"""
    try:
        data = request.get_json()
        vin = data.get('vin', '').strip()
        
        result = decoder.search(vin)
        
        if result['success'] and result['search_type'] == 'vin':
            return jsonify({
                'success': True,
                'vehicle_info': result['data'].__dict__ if hasattr(result['data'], '__dict__') else result['data']
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Could not decode VIN')
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        })

@app.route('/api/engine/<engine_code>')
def api_engine_search(engine_code):
    """REST API endpoint for engine code search"""
    try:
        result = decoder.search_by_engine_code(engine_code)
        
        if result:
            # Convert PartInformation objects for JSON
            if 'parts_compatibility' in result:
                result['parts_compatibility'] = convert_parts_to_dict(result['parts_compatibility'])
            
            return jsonify({
                'success': True,
                'engine_data': result
            })
        else:
            return jsonify({
                'success': False,
                'error': f'Engine code not found: {engine_code}'
            }), 404
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Server error: {str(e)}'
        }), 500

if __name__ == '__main__':
    port = 5002
    print("🚗 Starting Enhanced Japanese Car VIN & Engine Decoder...")
    print(f"📱 Open your browser: http://localhost:{port}")
    print("🔧 NEW: Now supports Engine Code search!")
    print("🧪 Test Engine Code: D16W73005025 (your original input)")
    print("🧪 Test VIN: 4T1BE32K25U123456 (detailed parts)")
    print()
    print("🆕 API Endpoints:")
    print("   - POST /search (universal VIN or engine search)")
    print("   - GET /api/engine/<engine_code>")
    print("   - POST /decode (legacy VIN-only)")
    app.run(debug=True, host='0.0.0.0', port=port)