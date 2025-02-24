import unittest
from unittest.mock import patch, MagicMock
from weather_service import WeatherService
import json
from datetime import datetime

class TestWeatherService(unittest.TestCase):
    def setUp(self):
        self.api_key = "test_key"
        self.weather_service = WeatherService(self.api_key)

    def test_successful_forecast(self):
        mock_response = {
            "list": [
                {
                    "main": {"temp": 23.5},
                    "weather": [{"description": "partly cloudy"}]
                },
                {
                    "main": {"temp": 25.8},
                    "weather": [{"description": "partly cloudy"}]
                },
                {
                    "main": {"temp": 24.2},
                    "weather": [{"description": "clear sky"}]
                },
                {
                    "main": {"temp": 22.9},
                    "weather": [{"description": "partly cloudy"}]
                }
            ]
        }

        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()

            forecast = self.weather_service.get_forecast("London,UK")
            self.assertEqual(forecast, "23°C-26°C, partly cloudy")

    def test_api_failure(self):
        with patch('requests.get') as mock_get:
            mock_get.side_effect = requests.RequestException()
            
            forecast = self.weather_service.get_forecast("London,UK")
            self.assertEqual(forecast, "Weather data unavailable")

    def test_invalid_data(self):
        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = {"list": []}
            mock_get.return_value.raise_for_status = MagicMock()
            
            forecast = self.weather_service.get_forecast("London,UK")
            self.assertEqual(forecast, "Weather data unavailable")

    def test_fallback_with_cached_data(self):
        # First, get successful forecast
        mock_response = {
            "list": [
                {
                    "main": {"temp": 23.5},
                    "weather": [{"description": "sunny"}]
                },
                {
                    "main": {"temp": 25.8},
                    "weather": [{"description": "sunny"}]
                }
            ]
        }

        with patch('requests.get') as mock_get:
            mock_get.return_value.json.return_value = mock_response
            mock_get.return_value.raise_for_status = MagicMock()
            
            # Get initial forecast
            self.weather_service.get_forecast("London,UK")
            
            # Simulate API failure
            mock_get.side_effect = requests.RequestException()
            
            # Should return stale data
            forecast = self.weather_service.get_forecast("London,UK")
            self.assertTrue("(Data stale)" in forecast)

if __name__ == '__main__':
    unittest.main()