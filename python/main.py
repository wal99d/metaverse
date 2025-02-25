from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from arduino_controller import ArduinoController
from weather_service import WeatherService
import atexit
import signal
import sys
from app import app, arduino, weather
from flask import Flask, jsonify
import socket

class SystemManager:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.latest_forecast = "Initializing weather data..."
        self.is_running = True

    def initialize(self):
        """Initialize all system components."""
        # Connect to Arduino
        if not arduino.connect():
            print("Warning: Failed to connect to Arduino. LED control will be unavailable.")

        # Schedule weather updates
        self.scheduler.add_job(
            self.update_weather,
            'interval',
            minutes=10,
            id='weather_update',
            next_run_time=None
        )

        # Initial weather update
        self.update_weather()

        # Start the scheduler
        self.scheduler.start()

    def update_weather(self):
        """Update weather forecast."""
        try:
            self.latest_forecast = weather.get_forecast('London,UK')
            print(f"Weather updated: {self.latest_forecast}")
        except Exception as e:
            print(f"Error updating weather: {e}")

    def cleanup(self, signum=None, frame=None):
        """Clean up system resources."""
        print("\nShutting down system...")
        self.scheduler.shutdown()
        
        if arduino.serial:
            arduino.led_off()
            arduino.disconnect()
        
        if not signum:
            sys.exit(0)
        else:
            self.is_running = False

if __name__ == '__main__':
    # Initialize system manager
    system_manager = SystemManager()
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, system_manager.cleanup)
    signal.signal(signal.SIGTERM, system_manager.cleanup)
    
    # Register cleanup
    atexit.register(system_manager.cleanup)
    
    # Initialize system
    system_manager.initialize()
    
    # Start Flask server
    ports = [5001, 5002, 5003, 5000]
    
    for port in ports:
        try:
            app.run(host='0.0.0.0', port=port)
            break
        except socket.error as e:
            print(f"Port {port} is in use, trying next port...")
            if port == ports[-1]:
                print("No available ports found. Please free up a port and try again.")
                system_manager.cleanup()
        except Exception as e:
            print(f"Error starting Flask server: {e}")
            system_manager.cleanup()