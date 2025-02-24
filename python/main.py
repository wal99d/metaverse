from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from arduino_controller import ArduinoController
from weather_service import WeatherService
import atexit
import signal
import sys
from app import app, arduino, weather

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
            next_run_time=None  # Don't run immediately
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
        
        # Stop scheduler
        self.scheduler.shutdown()
        
        # Disconnect Arduino
        if arduino.serial:
            arduino.led_off()  # Turn off LED before disconnecting
            arduino.disconnect()
        
        # Stop Flask (if running in main thread)
        if not signum:  # Normal shutdown
            sys.exit(0)
        else:  # Signal handler
            self.is_running = False

def create_app(system_manager):
    """Configure Flask app with system manager."""
    
    # Override weather endpoint to use cached forecast
    @app.route('/api/weather')
    def get_weather():
        return {'forecast': system_manager.latest_forecast}
    
    return app

if __name__ == '__main__':
    # Initialize system manager
    system_manager = SystemManager()
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, system_manager.cleanup)
    signal.signal(signal.SIGTERM, system_manager.cleanup)
    
    # Register cleanup on normal exit
    atexit.register(system_manager.cleanup)
    
    # Initialize system
    system_manager.initialize()
    
    # Configure and start Flask app
    app = create_app(system_manager)
    
    # Start Flask server
    try:
        app.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting Flask server: {e}")
        system_manager.cleanup()