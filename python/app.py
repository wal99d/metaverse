from flask import Flask, render_template, jsonify, request
from arduino_controller import ArduinoController
from weather_service import WeatherService
import os
from threading import Lock

app = Flask(__name__)

# Initialize controllers with thread safety
arduino = ArduinoController('COM3')  # Adjust port as needed
weather = WeatherService()
arduino_lock = Lock()

@app.route('/')
def index():
    """Serve the main interface page."""
    return render_template('index.html')

@app.route('/api/led', methods=['POST'])
def control_led():
    """Handle LED control requests."""
    try:
        state = request.json.get('state')
        if state not in ['on', 'off']:
            return jsonify({'error': 'Invalid state'}), 400

        with arduino_lock:
            if not arduino.serial:
                arduino.connect()
            
            if state == 'on':
                response = arduino.led_on()
            else:
                response = arduino.led_off()

        if response:
            return jsonify({'status': 'success', 'message': response})
        return jsonify({'error': 'Failed to control LED'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/weather')
def get_weather():
    """Get current weather forecast."""
    try:
        forecast = weather.get_forecast('London,UK')  # Adjust location as needed
        return jsonify({'forecast': forecast})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)