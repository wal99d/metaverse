import serial
import time
from typing import Optional

class ArduinoController:
    def __init__(self, port: str, baud_rate: int = 9600, timeout: int = 1):
        """Initialize the Arduino controller.
        
        Args:
            port: Serial port (e.g., 'COM3' for Windows)
            baud_rate: Baud rate for serial communication
            timeout: Serial timeout in seconds
        """
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial = None

    def connect(self) -> bool:
        """Establish connection with Arduino.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baud_rate,
                timeout=self.timeout
            )
            time.sleep(2)  # Wait for Arduino to reset
            return True
        except serial.SerialException as e:
            print(f"Error connecting to Arduino: {e}")
            return False

    def disconnect(self):
        """Close the serial connection."""
        if self.serial and self.serial.is_open:
            self.serial.close()

    def send_command(self, command: str) -> Optional[str]:
        """Send a command to Arduino and get response.
        
        Args:
            command: Command to send ('LED_ON' or 'LED_OFF')
            
        Returns:
            Optional[str]: Arduino's response or None if error occurs
        """
        if not self.serial or not self.serial.is_open:
            print("Error: Not connected to Arduino")
            return None

        try:
            # Send command with newline
            self.serial.write(f"{command}\n".encode())
            # Read response
            response = self.serial.readline().decode().strip()
            return response
        except serial.SerialException as e:
            print(f"Error sending command: {e}")
            return None

    def led_on(self) -> Optional[str]:
        """Turn LED on.
        
        Returns:
            Optional[str]: Arduino's response or None if error occurs
        """
        return self.send_command("LED_ON")

    def led_off(self) -> Optional[str]:
        """Turn LED off.
        
        Returns:
            Optional[str]: Arduino's response or None if error occurs
        """
        return self.send_command("LED_OFF")