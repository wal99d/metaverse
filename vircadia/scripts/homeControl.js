(function() {
    // Configuration
    const BACKEND_URL = "http://localhost:5001";  // Match the port we set in Flask
    const UPDATE_INTERVAL = 10 * 60 * 1000;  // 10 minutes in milliseconds
    
    // UI Elements
    var button;
    var weatherText;
    var isLedOn = false;

    // Initialize the control panel
    function init() {
        createControlPanel();
        startWeatherUpdates();
    }

    function createControlPanel() {
        // Create a simple panel
        const panel = Entities.addEntity({
            type: "Box",
            name: "ControlPanel",
            dimensions: { x: 1, y: 0.6, z: 0.1 },
            position: Vec3.sum(MyAvatar.position, Vec3.multiplyQbyV(MyAvatar.orientation, { x: 0, y: 1.5, z: -2 })),
            color: { red: 200, green: 200, blue: 200 },
            userData: JSON.stringify({ "type": "control-panel" })
        });

        // Add LED control button
        button = Entities.addEntity({
            type: "Text",
            name: "LedButton",
            parentID: panel,
            dimensions: { x: 0.4, y: 0.2, z: 0.01 },
            position: Vec3.sum(Entities.getEntityProperties(panel).position, { x: 0, y: 0.1, z: 0.1 }),
            text: "LED: OFF",
            lineHeight: 0.1,
            alignment: "center",
            backgroundColor: { red: 100, green: 100, blue: 100 },
            userData: JSON.stringify({ "type": "led-button" })
        });

        // Add weather display
        weatherText = Entities.addEntity({
            type: "Text",
            name: "WeatherDisplay",
            parentID: panel,
            dimensions: { x: 0.8, y: 0.2, z: 0.01 },
            position: Vec3.sum(Entities.getEntityProperties(panel).position, { x: 0, y: -0.15, z: 0.1 }),
            text: "Loading weather...",
            lineHeight: 0.08,
            alignment: "center",
            userData: JSON.stringify({ "type": "weather-display" })
        });

        // Add click handler
        Entities.clickReleaseOnEntity.connect(onEntityClicked);
    }

    function onEntityClicked(entityID, event) {
        if (entityID === button) {
            toggleLED();
        }
    }

    function toggleLED() {
        const newState = !isLedOn;
        fetch(`${BACKEND_URL}/api/led`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ state: newState ? 'on' : 'off' })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                isLedOn = newState;
                Entities.editEntity(button, {
                    text: `LED: ${isLedOn ? 'ON' : 'OFF'}`,
                    backgroundColor: isLedOn ? 
                        { red: 100, green: 255, blue: 100 } : 
                        { red: 100, green: 100, blue: 100 }
                });
            }
        })
        .catch(error => {
            print("Error controlling LED:", error);
        });
    }

    function updateWeather() {
        fetch(`${BACKEND_URL}/api/weather`)
            .then(response => response.json())
            .then(data => {
                if (data.forecast) {
                    Entities.editEntity(weatherText, {
                        text: data.forecast
                    });
                }
            })
            .catch(error => {
                print("Error updating weather:", error);
                Entities.editEntity(weatherText, {
                    text: "Weather update failed"
                });
            });
    }

    function startWeatherUpdates() {
        updateWeather();  // Initial update
        Script.setInterval(updateWeather, UPDATE_INTERVAL);
    }

    function cleanup() {
        Entities.clickReleaseOnEntity.disconnect(onEntityClicked);
        if (button) Entities.deleteEntity(button);
        if (weatherText) Entities.deleteEntity(weatherText);
    }

    // Script lifecycle
    Script.scriptEnding.connect(cleanup);
    init();
}());