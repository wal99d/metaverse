@echo off
echo Starting Home Automation System...
echo.
echo Make sure:
echo 1. Arduino is connected
echo 2. OPENWEATHER_API_KEY environment variable is set
echo 3. COM port in app.py matches your Arduino
echo.
python main.py
pause