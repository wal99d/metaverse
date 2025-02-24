import unittest
from arduino_controller import ArduinoController

class TestArduinoController(unittest.TestCase):
    def setUp(self):
        # Replace 'COM3' with your actual port
        self.controller = ArduinoController('COM3')
        self.connected = self.controller.connect()

    def tearDown(self):
        self.controller.disconnect()

    def test_led_control(self):
        if not self.connected:
            self.skipTest("Arduino not connected")

        # Test LED ON
        response = self.controller.led_on()
        self.assertEqual(response, "LED turned on")

        # Test LED OFF
        response = self.controller.led_off()
        self.assertEqual(response, "LED turned off")

    def test_invalid_command(self):
        if not self.connected:
            self.skipTest("Arduino not connected")

        # Test invalid command
        response = self.controller.send_command("INVALID")
        self.assertEqual(response, "Unknown command")

if __name__ == '__main__':
    unittest.main()