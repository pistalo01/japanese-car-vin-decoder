# Japanese Car VIN Decoder & Parts Identification System

A comprehensive system for decoding VINs and identifying compatible parts specifically for Japanese vehicles. This system uses the NHTSA API and provides both a command-line interface and a web-based user interface.

## 🚗 Features

- **VIN Decoding**: Decode 17-character VINs to extract vehicle information
- **Japanese Vehicle Focus**: Specialized for Japanese manufacturers
- **Parts Identification**: Identify compatible parts based on vehicle specifications
- **Engine & Transmission Matching**: Specific parts recommendations based on engine and transmission types
- **Safety Features Detection**: Extract safety features from VIN data
- **Web Interface**: User-friendly web application
- **REST API**: Programmatic access to VIN decoding and parts identification

## 🏭 Supported Japanese Manufacturers

- Toyota (including Lexus)
- Honda (including Acura)
- Nissan (including Infiniti)
- Mazda
- Mitsubishi
- Subaru
- Suzuki
- Isuzu
- Daihatsu
- Scion
- Datsun

## 📋 Requirements

- Python 3.7+
- Internet connection (for NHTSA API access)

## 🚀 Installation

1. **Clone or download the files**:
   ```bash
   # If you have the files locally
   cd /path/to/japanese-car-vin-decoder
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

### Command Line Interface

Run the main VIN decoder script:

```bash
python japanese_car_vin_decoder.py
```

This will test the system with example VINs and show the results.

### Web Interface

Start the web application:

```bash
python web_interface.py
```

Then open your browser and go to: `http://localhost:5000`

### REST API

The system provides several API endpoints:

#### Decode VIN
```bash
GET /api/vehicle/{vin}
```

Example:
```bash
curl http://localhost:5000/api/vehicle/1HGBH41JXMN109186
```

#### Get Parts Compatibility
```bash
GET /api/parts/{vin}
```

Example:
```bash
curl http://localhost:5000/api/parts/1HGBH41JXMN109186
```

#### Decode VIN (POST)
```bash
POST /decode
Content-Type: application/json

{
    "vin": "1HGBH41JXMN109186"
}
```

## 🔧 Parts Categories

The system identifies compatible parts in the following categories:

### Engine Parts
- Air filters
- Oil filters
- Spark plugs
- Timing belts
- Water pumps
- Thermostats

### Brake System
- Brake pads
- Brake rotors
- Brake calipers
- Brake lines
- Master cylinders

### Suspension
- Shocks
- Struts
- Springs
- Control arms
- Bushings
- Ball joints

### Transmission
- Transmission filters
- Transmission fluid
- Clutch components
- Flywheels

### Electrical
- Batteries
- Alternators
- Starters
- Ignition coils
- Spark plug wires

### Cooling System
- Radiators
- Hoses
- Coolant
- Fans
- Temperature sensors

### Fuel System
- Fuel filters
- Fuel pumps
- Injectors
- Fuel lines

### Exhaust System
- Catalytic converters
- Mufflers
- Exhaust pipes
- Oxygen sensors

## 📊 Example Output

### Vehicle Information
```json
{
  "vin": "1HGBH41JXMN109186",
  "make": "HONDA",
  "model": "ACCORD",
  "year": "1991",
  "engine": "F22A1",
  "transmission": "Automatic",
  "body_style": "Passenger Car",
  "fuel_type": "Gasoline",
  "drive_type": "FWD",
  "safety_features": ["ABS", "Traction Control"]
}
```

### Parts Compatibility
```json
{
  "engine": ["timing_belt", "water_pump", "thermostat", "oil_filter", "air_filter"],
  "transmission": ["transmission_filter", "transmission_fluid", "transmission_pan_gasket"],
  "year_specific": ["ignition_coil", "spark_plug_wires", "oxygen_sensors"],
  "model_specific": ["accord_specific_trim", "accord_engine_mounts"]
}
```

## 🔍 VIN Validation

The system validates VINs using the following criteria:
- Exactly 17 characters long
- No invalid characters (I, O, Q)
- Valid character set (A-H, J-N, P-Z, 0-9)
- Basic pattern validation

## 🌐 Data Sources

- **NHTSA API**: Primary source for VIN decoding and vehicle information
- **Manufacturer Patterns**: Japanese manufacturer-specific VIN patterns
- **Parts Database**: Built-in parts compatibility database

## 🛠️ Customization

### Adding New Manufacturers

To add support for additional Japanese manufacturers, modify the `japanese_manufacturers` set in the `JapaneseCarVINDecoder` class:

```python
self.japanese_manufacturers = {
    'TOYOTA', 'HONDA', 'NISSAN', 'MAZDA', 'MITSUBISHI', 'SUBARU', 
    'SUZUKI', 'ISUZU', 'DAIHATSU', 'LEXUS', 'ACURA', 'INFINITI',
    'SCION', 'DATSUN', 'NEW_MANUFACTURER'  # Add here
}
```

### Adding New Parts Categories

To add new parts categories, modify the `parts_categories` dictionary:

```python
self.parts_categories = {
    'engine': ['air_filter', 'oil_filter', 'spark_plugs', 'timing_belt', 'water_pump', 'thermostat'],
    'new_category': ['part1', 'part2', 'part3'],  # Add here
    # ... existing categories
}
```

### Engine-Specific Parts

To add engine-specific parts, modify the `get_engine_specific_parts` method:

```python
engine_parts = {
    '2JZ': ['timing_belt', 'water_pump', 'thermostat', 'oil_filter', 'air_filter'],
    'NEW_ENGINE': ['specific_part1', 'specific_part2'],  # Add here
    # ... existing engines
}
```

## 🚨 Error Handling

The system includes comprehensive error handling for:
- Invalid VIN formats
- Network connectivity issues
- API rate limiting
- Missing vehicle data
- Invalid responses from external APIs

## 📝 Logging

The system uses Python's logging module to track:
- VIN validation errors
- API request failures
- Parts identification processes
- General system operations

## 🔒 Security Considerations

- No sensitive data is stored locally
- All API requests use HTTPS
- Input validation prevents injection attacks
- Rate limiting is implemented for API calls

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Troubleshooting

### Common Issues

1. **"Could not decode VIN"**
   - Check if the VIN is exactly 17 characters
   - Verify the VIN doesn't contain invalid characters (I, O, Q)
   - Ensure internet connectivity for API access

2. **"Network error"**
   - Check your internet connection
   - Verify the NHTSA API is accessible
   - Check firewall settings

3. **"No parts compatibility found"**
   - This is normal for some vehicles
   - The system may not have specific data for that make/model/year
   - Try a different VIN for testing

### Getting Help

If you encounter issues:
1. Check the console output for error messages
2. Verify your Python version (3.7+ required)
3. Ensure all dependencies are installed
4. Check the NHTSA API status

## 🔮 Future Enhancements

Planned features for future versions:
- Integration with additional parts databases
- Real-time parts pricing
- Vehicle maintenance schedules
- Parts interchangeability data
- Mobile application
- Database caching for improved performance
- Multi-language support
- Advanced search filters

---

**Note**: This system is designed for educational and informational purposes. Always verify parts compatibility with your specific vehicle before making purchases.
