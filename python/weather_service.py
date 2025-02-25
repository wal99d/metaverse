import requests
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass

@dataclass
class WeatherForecast:
    temp_min: float
    temp_max: float
    condition: str
    timestamp: datetime

class WeatherService:
    def __init__(self):
        """Initialize WeatherService using Open-Meteo API."""
        self.base_url = "https://api.open-meteo.com/v1/forecast"
        self.last_forecast: Optional[WeatherForecast] = None

    def get_forecast(self, city: str) -> str:
        """Get weather forecast for specified city."""
        try:
            # First, get coordinates for the city using Nominatim
            geocoding_url = f"https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1"
            geo_response = requests.get(geocoding_url, headers={'User-Agent': 'WeatherService/1.0'})
            geo_response.raise_for_status()
            
            location_data = geo_response.json()
            if not location_data:
                raise ValueError(f"Could not find coordinates for {city}")
            
            lat = location_data[0]['lat']
            lon = location_data[0]['lon']
            
            # Get weather forecast using coordinates
            params = {
                'latitude': lat,
                'longitude': lon,
                'hourly': 'temperature_2m,weathercode',
                'forecast_days': 1
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
        if not data.get('hourly'):
            raise ValueError("Invalid forecast data")
            
        temps = data['hourly']['temperature_2m'][:24]  # Next 24 hours
        codes = data['hourly']['weathercode'][:24]
        
        # Convert weather code to condition text
        condition = self._get_condition_from_code(max(set(codes), key=codes.count))
        
        return WeatherForecast(
            temp_min=min(temps),
            temp_max=max(temps),
            condition=condition,
            timestamp=datetime.now()
        )

    def _get_condition_from_code(self, code: int) -> str:
        """Convert Open-Meteo weather code to condition text."""
        conditions = {
            0: "clear sky",
            1: "mainly clear",
            2: "partly cloudy",
            3: "overcast",
            45: "foggy",
            48: "depositing rime fog",
            51: "light drizzle",
            53: "moderate drizzle",
            55: "dense drizzle",
            61: "slight rain",
            63: "moderate rain",
            65: "heavy rain",
            71: "slight snow",
            73: "moderate snow",
            75: "heavy snow",
            77: "snow grains",
            80: "slight rain showers",
            81: "moderate rain showers",
            82: "violent rain showers",
            95: "thunderstorm"
        }
        return conditions.get(code, "unknown")

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