import { useState, useEffect } from "react";
import { convertCartesianToDegrees } from "./coordUtils";

/**
 * ZoneSettingsUI component
 * @param {Object} props - Component props.
 * @param {string} props.zoneName - Name of the zone.
 * @param {Array} props.positions - Array of positions in the zone.
 * @param {Function} props.onSave - Callback function to save the zone settings.
 * @param {Function} props.onDelete - Callback function to delete the zone.
 * @param {Function} props.onRename - Callback function to rename the zone.
 * @returns {JSX.Element} - Rendered component.
 * @description This component displays the settings for a zone, including coordinates and options to save, delete, or rename the zone.
 */
const ZoneSettingsUI = ({ zoneName, positions = [], onSave, onDelete, onRename }) => {
    const [isRenaming, setIsRenaming] = useState(false);
    const [newName, setNewName] = useState(zoneName);

    useEffect(() => {
        setNewName(zoneName);
    }, [zoneName]);

    const handleKeyPress = (e) => {
        if (e.key === "Enter") {
            onRename(newName);
            setIsRenaming(false);
        }
    };

    return (
        <div className="zone-settings-ui">
            <div className="settings-header">
                <h5>
                    Settings for zone '{zoneName}'
                    <button
                        className="rename-button"
                        onClick={() => setIsRenaming(true)}
                        title="Renaming Zone"
                    >
                        Rename
                    </button>
                </h5>
            </div>

            {isRenaming && (
                <div className="rename-section">
                    <input
                        type="text"
                        value={newName}
                        onChange={(e) => setNewName(e.target.value)}
                        onKeyDown={handleKeyPress}
                        placeholder="Edit zone name"
                        autoFocus
                    />
                    <button onClick={() => { onRename(newName); setIsRenaming(false); }}>
                        Save Name
                    </button>
                    <button onClick={() => setIsRenaming(false)}>Cancel</button>
                </div>
            )}

            <div className="settings-body">
                <h5>Coordinates:</h5>
                <ul>
                    {positions.map((pos, index) => {
                        // console.log("Position:", pos);
                        const { latitude, longitude } =
                            pos.latitude !== undefined && pos.longitude !== undefined
                                ? pos
                                : convertCartesianToDegrees(pos);
                        // console.log("Converted Position:", { latitude, longitude });
                        return (
                            <li key={index}>
                                <strong>Point {index + 1}:</strong>
                                Lat: {latitude}, Lon: {longitude}
                            </li>
                        );
                    })}
                </ul>
                <button className="save-btn" onClick={onSave}>Save</button>
                <button className="delete-btn" onClick={onDelete}>Delete</button>
            </div>
        </div>
    );
};

export default ZoneSettingsUI;
