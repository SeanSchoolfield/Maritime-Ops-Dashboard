import { useState } from "react";
import Overlays from "./overlays/OverlaysUI";
import FiltersUI from "./filters/FiltersUI";
import useFetchFilters from "./filters/Filters";

/**
* ToolsUI component that provides a user interface for various tools and overlays.
* It includes buttons for toggling drawing, undoing actions, clearing the canvas,
* selecting shapes, and applying filters.
*
* @param {function} onToggleDrawing - Function to toggle drawing mode.
* @param {function} onUndo - Function to undo the last action.
* @param {function} onClear - Function to clear the canvas.
* @param {function} onSelectShape - Function to select a shape type.
* @param {string} apiEndpoint - API endpoint for fetching filter options.
* @param {function} onFilterApply - Function to apply selected filters.
*
* @returns {JSX.Element} The rendered ToolsUI component.
* @description This component manages the state of the UI controls,
* including the visibility of different panels (tools, overlays, filters).
* It uses the useFetchFilters hook to fetch filter options from the API.
*/

const ToolsUI = ({ onToggleDrawing, onUndo, onClear, onSelectShape, apiEndpoint, onFilterApply }) => {
    const [openPanel, setOpenPanel] = useState(false);
    // const [selectedShape, setSelectedShape] = useState("polygon");
    const { loading, error } = useFetchFilters(apiEndpoint);

    // const handleShapeChange = (event) => {
    //     setSelectedShape(event.target.value);
    //     onSelectShape(event.target.value);
    // };

    const handleToggle = (panel) => {
        setOpenPanel((prev) => (prev === panel ? null : panel));
    };

    return (
        <div className="ui-controls">
            {/*Button to expand/collapse sidebars*/}
            <button onClick={() => handleToggle("tools")}>
                {openPanel === "tools" ? "Tools" : "Tools"}
            </button>

            <button onClick={() => handleToggle("overlays")}>
                {openPanel === "overlays" ? "Overlays" : "Overlays"}
            </button>

            <button onClick={() => handleToggle("filters")}>
                {openPanel === "filters" ? "Filters" : "Filters"}
            </button>

            {/* Sidebar Content */}
            {openPanel === "tools" && (
                <div className="tools-panel">
                    <h4>Zoning Tools</h4>

                    <button onClick={onToggleDrawing}>Toggle Zoning Tool</button>
                    <button onClick={onUndo}>Undo</button>
                    <button onClick={onClear}>Clear</button>

                    {/* non-functional buttons */}
                    {/* <h4>Select Shape</h4>
                    <label>
                        <input
                            type="radio"
                            value="polygon"
                            checked={selectedShape === "polygon"}
                            onChange={handleShapeChange}
                        />
                        Polygon
                    </label>
                    <label>
                        <input
                            type="radio"
                            value="polyline"
                            checked={selectedShape === "polyline"}
                            onChange={handleShapeChange}
                        />
                        Polyline
                    </label>
                    <label>
                        <input
                            type="radio"
                            value="point"
                            checked={selectedShape === "point"}
                            onChange={handleShapeChange}
                        />
                        Point
                    </label> */}
                </div>
            )}

            {openPanel === "overlays" && (
                <div className="overlay-panel">
                    <h3>Overlays</h3>
                    <button>Weather</button>
                    <button>Ocean Conditions</button>
                    <button>Traffic Heatmap</button>
                    <button onClick={() => handleToggle(null)}>Close</button>
                </div>
            )}

            {openPanel === "filters" && (
                <div className="filter-panel">
                    <h3>Filters</h3>
                    {loading && <div>Loading...</div>}
                    {error && <div>{error}</div>}
                    {!loading && !error && (
                        <FiltersUI
                            apiEndpoint={apiEndpoint}
                            onFilterApply={onFilterApply}
                        />
                    )}
                    <button onClick={() => handleToggle(null)}>Close</button>
                </div>
            )}
        </div>
    );
};

export default ToolsUI;
