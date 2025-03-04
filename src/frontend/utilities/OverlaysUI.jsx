import { useState } from "react";

const OverlaysUI = ({ onClose, onToggleWeather }) => {
    const [showWeather, setShowWeather] = useState(false);

    const handleWeatherToggle = () => {
        setShowWeather((prev) => !prev);
        onToggleWeather();
    };

    return (
        // placeholder values and buttons
        <div className="overlay-panel">
            <h3>Overlays</h3>
            <button onClick={onClose}>Close</button>
            <button onClick={handleWeatherToggle}>
                {showWeather ? "Hide Weather Overlay" : "ShowWeatherOverlay"}
            </button>
            <button> Ocean Conditions </button>
            <button> Traffic Heatmaps</button>
        </div>
    );
};

export default OverlaysUI