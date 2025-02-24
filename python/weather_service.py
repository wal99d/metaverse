import requests
from datetime import datetime
from typing import Optional, Dict, Any
import os
from dataclasses import dataclass

@dataclass
class WeatherForecast:
    temp_min: float
    temp_max: float
    condition: str
    timestamp: datetime

class WeatherService:
    def __init__(self, api_key: str = None):
        """Initialize WeatherService with OpenWeatherMap API key.
        
        Args:
            api_key: OpenWeatherMap API key. If None, tries to read from environment variable.
        """
        self.api_key = api_key or os.getenv('OPENWEATHER_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set OPENWEATHER_API_KEY environment variable or pass it directly.")
        
        self.base_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.last_forecast: Optional[WeatherForecast] = None

    def get_forecast(self, city: str) -> str:
        """Get weather forecast for specified city.
        
        Args:
            city: City name (e.g., 'London,UK')
            
        Returns:
            str: Formatted weather forecast string
        """
        try:
            params = {
                'q': city,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': 4  # Limit to next few hours
            }
            
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            
            forecast = self._parse_forecast(response.json())
            self.last_forecast = forecast
            
            return self._format_forecast(forecast)
            
        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return self._get_fallback_forecast()
        except (KeyError, ValueError) as e:
            print(f"Error parsing weather data: {e}")
            return self._get_fallback_forecast()

    def _parse_forecast(self, data: Dict[str, Any]) -> WeatherForecast:
        """Parse JSON response into WeatherForecast object."""
        if not data.get('list'):
            raise ValueError("Invalid forecast data")
            
        forecasts = data['list']
        temps = [item['main']['temp'] for item in forecasts]
        conditions = [item['weather'][0]['description'] for item in forecasts]
        
        return WeatherForecast(
            temp_min=min(temps),
            temp_max=max(temps),
            condition=max(set(conditions), key=conditions.count),  # most common condition
            timestamp=datetime.now()
        )

    def _format_forecast(self, forecast: WeatherForecast) -> str:
        """Format WeatherForecast into display string."""
        return f"{forecast.temp_min:.0f}°C-{forecast.temp_max:.0f}°C, {forecast.condition}"

    def _get_fallback_forecast(self) -> str:
        """Return fallback message or last known forecast if available."""
        if self.last_forecast:
            time_diff = (datetime.now() - self.last_forecast.timestamp).total_seconds() / 60
            if time_diff < 30:  # Use cached data if less than 30 minutes old
                return f"{self._format_forecast(self.last_forecast)} (Data stale)"
        return "Weather data unavailable"