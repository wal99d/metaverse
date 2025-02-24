import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import json
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import SystemManager
from app import app
from arduino_controller import ArduinoController
from weather_service import WeatherService

class TestSystemIntegration(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.system = SystemManager()
        
    def tearDown(self):
        self.system.cleanup()

    @patch('arduino_controller.ArduinoController.connect')
    @patch('arduino_controller.ArduinoController.led_on')
    def test_led_control_endpoint(self, mock_led_on, mock_connect):
        """Test LED control through Flask endpoint."""
        # Setup mocks
        mock_connect.return_value = True
        mock_led_on.return_value = "LED turned on"

        # Test LED ON request
        response = self.app.post('/api/led', 
                               json={'state': 'on'},
                               content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(mock_led_on.called)
        
        data = json.loads(response.data)
        self.assertEqual(data['message'], "LED turned on")

    @patch('weather_service.WeatherService.get_forecast')
    def test_weather_endpoint(self, mock_get_forecast):
        """Test weather endpoint and update mechanism."""
        test_forecast = "20°C-25°C, sunny"
        mock_get_forecast.return_value = test_forecast

        # Initialize system to trigger weather update
        self.system.initialize()
        
        # Test weather endpoint
        response = self.app.get('/api/weather')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['forecast'], test_forecast)

    @patch('serial.Serial')
    def test_arduino_communication(self, mock_serial):
        """Test Arduino communication flow."""
        # Setup mock serial
        mock_serial.return_value.is_open = True
        mock_serial.return_value.readline.return_value = b"LED turned on\n"

        # Initialize Arduino controller
        arduino = ArduinoController('COM3')
        arduino.connect()

        # Test LED control
        response = arduino.led_on()
        self.assertEqual(response, "LED turned on")

        # Verify correct command was sent
        mock_serial.return_value.write.assert_called_with(b"LED_ON\n")

    def test_system_initialization(self):
        """Test complete system initialization."""
        with patch('arduino_controller.ArduinoController.connect') as mock_connect, \
             patch('weather_service.WeatherService.get_forecast') as mock_forecast:
            
            mock_connect.return_value = True
            mock_forecast.return_value = "22°C-24°C, cloudy"

            # Initialize system
            self.system.initialize()

            # Verify components were initialized
            self.assertTrue(mock_connect.called)
            self.assertTrue(mock_forecast.called)
            self.assertTrue(self.system.scheduler.running)