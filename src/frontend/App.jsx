import { useState, useRef, useEffect } from "react";
import CustomGeometry from "./utilities/CustomGeometry";
import ToolsUI from "./utilities/ToolsUI";
import ZoneSettingsUI from "./utilities/ZoneSettingsUI";
import FiltersUI from "./utilities/filters/FiltersUI";
import ConfirmationDialog from "./utilities/ConfirmationDialog";
import { ToastContainer, toast } from "react-toastify";
import "react-toastify/ReactToastify.css";
import "./App.css";
import { placeVessel } from "./utilities/shippingVessels/Vessels";
import { Viewer } from "resium";
// import { SceneMode, Cartographic, Math } from "cesium";
// import axios from "axios";
import OverlaysUI from "./utilities/overlays/OverlaysUI";
import { fetchVessels } from "./utilities/apiFetch";
import { zoning } from "./utilities/zoning"; import {
  handleUndo,
  handleToggleDrawing,
  handleToggleOverlays,
  handleToggleFilters,
  handleClear,
  handleClearConfirmed,
  handleClearCancelled,
  handleRename,
  handleDelete,
  handleDeleteConfirm,
  handleDeleteCancel,
  handleSave,
} from "./utilities/eventHandlers";
import { useCesiumViewer } from "./utilities/hooks/useCesiumViewer";
import "./App.css";
import PredictedPath from "./utilities/PredictedPath";
import { Cartesian3, Color, HeightReference } from "cesium";
import { Entity } from "resium";

function App() {
  const [isDrawing, setIsDrawing] = useState(false);
  const [geometries, setGeometries] = useState([]);
  const [selectedGeometry, setSelectedGeometry] = useState(null);
  const [showContextMenu, setShowContextMenu] = useState(false);
  const [contextMenuPosition, setContextMenuPosition] = useState({ x: 0, y: 0 });
  const [showSettings, setShowSettings] = useState(false);
  const [showOverlays, setShowOverlays] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [vessels, setVessels] = useState([]);
  const [viewerReady, setViewerReady] = useState(false);
  const [showClearDialog, setShowClearDialog] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [clickedCoordinates, setClickedCoordinates] = useState({ lat: null, lon: null });
  const [predictions, setPredictions] = useState([]);

  const viewerRef = useRef(null);
  const URL = window.location.href.split(":");
  const vesselsAPI = "http:" + URL[1] + ":8000/vessels/";
  const filtersAPI = "http:" + URL[1] + ":8000/filters/";

  useCesiumViewer(viewerRef, setViewerReady);

  const handleFilterApply = async (filters) => {
    console.log("Filters selected:");
    console.log(filters);
    await fetchVessels(vesselsAPI, filters, setVessels);
    await selectedGeometry ? zoning(polygonData, filters, setVessels) : console.log("NO ZONE SELECTED");
  };
    const polygonData = geometries?.find(
        (geo) => geo.id === selectedGeometry?.id
    );

  useEffect(() => {
    fetchVessels();
    
    selectedGeometry ? zoning(polygonData, setVessels) : console.log("NO ZONE SELECTED"); // Dunno whether or not this actually does anything...

    if (viewerRef.current && viewerRef.current.cesiumElement) {
      const viewer = viewerRef.current.cesiumElement;
      setViewerReady(true);
      // Create a scene mode change event handler
      const sceneModeChangeHandler = () => {
        // If there's a selected entity, re-select it to update the info box position
        if (viewer.selectedEntity) {
          const currentEntity = viewer.selectedEntity;
          viewer.selectedEntity = undefined; // Deselect
          setTimeout(() => {
            viewer.selectedEntity = currentEntity; // Re-select after a brief delay
          }, 100);
        }
      };

      // Add event listener for scene mode changes
      viewer.scene.morphComplete.addEventListener(sceneModeChangeHandler);

      // Clean up event listener when component unmounts
      return () => {
        if (viewer && viewer.scene && !viewer.isDestroyed()) {
          viewer.scene.morphComplete.removeEventListener(
            sceneModeChangeHandler
          );
        }
      };
    }
  }, [viewerRef.current]);

  // Handler for ToolUI 'Toggle Zoning'
  const handleToggleDrawing = () => {
    console.log("Toggled Zoning:", !isDrawing);
    setIsDrawing((prev) => {
      const newState = !prev;

      // notification of tool state
      toast.info(`Zoning Tool ${newState ? "Enabled" : "Disabled"}`, {
        position: "bottom-right",
        autoClose: 2000,
        hideProgressBar: true,
        closeOnClick: true,
        pauseOnHover: false,
        draggable: false,
      });
      return newState;
    });
  };

  const handleToggleOverlays = () => {
    setShowOverlays((prev) => !prev);
    console.log("Overlays toggled:", !showOverlays);
  };

  const handleToggleFilters = () => setShowFilters((prev) => !prev);

  // Undos previous point placed, will undo until the stack is empty
  const handleUndo = () => {
    setGeometries((prev) => {
      if (prev.length === 0) return prev;
      const updated = [...prev];
      updated[updated.length - 1].positions.pop();
      return updated;
    });
  };

  // Clears entire cesium viewer of geometries
  const handleClear = () => {
    setShowClearDialog(true);
  };

  const handleClearConfirmed = () => {
    const entities = viewerRef.current.cesiumElement.entities.values;
    for (let i = entities.length - 1; i >= 0; i--) {
      if (entities[i].isGeometry) {
        viewerRef.current.cesiumElement.entities.remove(entities[i]);
      }
    }
    setGeometries([]);
    setSelectedGeometry(null);
    setShowContextMenu(false);
    setShowClearDialog(false);
  };

  const handleClearCancelled = () => {
    setShowClearDialog(false);
  };

  const handleRename = (newName) => {
    // Update the name in the Cesium viewer
    const entity = viewerRef.current.cesiumElement.entities.getById(selectedGeometry.id);
    if (entity) {
        entity.name = newName;
    }

    // Update the name in the state
    setGeometries((prev) =>
      prev.map((geo) =>
        geo.id === selectedGeometry.id ? { ...geo, name: newName } : geo
      )
    );
    setSelectedGeometry((prev) => ({ ...prev, name: newName }));
  };

  const handleDelete = () => {
    setShowContextMenu(false);
    setShowDeleteDialog(true);
  };

  const handleDeleteConfirm = () => {
    if (selectedGeometry) {
      // Remove the selected geometry from the Cesium viewer
      viewerRef.current.cesiumElement.entities.removeById(selectedGeometry.id);

      // Update the state to remove the selected geometry
      setGeometries((prev) => prev.filter((geo) => geo.id !== selectedGeometry.id));
      setSelectedGeometry(null);
    }
    setShowDeleteDialog(false);
  };

  const handleDeleteCancel = () => {
    setShowDeleteDialog(false);
  };

  // Placeholder for save functionality
  const handleSave = () => {
    console.log("Zone settings saved.");
    setShowSettings(false);
  };

  const handleFilterApply = async (filters) => {
    console.log("Filters selected:");
    console.log(filters);
    await fetchVessels(filters);
  }

  const handlePathPrediction = async () => {
    if (clickedCoordinates.lat !== null && clickedCoordinates.lon !== null) {
      toast.info(`Lon: ${clickedCoordinates.lon}, Lat: ${clickedCoordinates.lat}`);
    } else {
      toast.info("No coordinates available");
    }
    var lon = clickedCoordinates.lon;
    var lat = clickedCoordinates.lat;
    var url = "http://127.0.0.1:8000/prediction/" + String(lon) + "/" + String(lat);
    const res = await axios.get(url);
    setPredictions(res.data);
    placeDot(res.data)
  }

  function placeDot(data) {
    // Validate and extract values from the data object
    console.log(data)
    const { 'Predicted LAT': latitude, 'Predicted LON': longitude, 'Hours Ahead': hoursAhead } = data;

    const numLongitude = Number(longitude);
    const numLatitude = Number(latitude);

    if (isNaN(numLongitude) || isNaN(numLatitude)) {
        console.warn(`Invalid coordinates for prediction at T+${hoursAhead}h`, { longitude, latitude });
        return null;
    }

    const position = Cartesian3.fromDegrees(numLongitude, numLatitude);

    return (
      <Entity
          key={`dot-${hoursAhead}-${longitude}-${latitude}`}
          position={position}
          point={{
              pixelSize: 10,
              color: Color.YELLOW,
              outlineWidth: 2,
              heightReference: HeightReference.CLAMP_TO_GROUND,
          }}
          label={{
              text: `T+${hoursAhead}h`,
              font: "10pt sans-serif",
              fillColor: Color.LIGHTBLUE,
              outlineColor: Color.BLACK,
              outlineWidth: 2,
              pixelOffset: new Cartesian3(0, -25, 15),
          }}
      />
    );
}

  // Debug
  // console.log("Show Context Menu:", showContextMenu);
  // console.log("Context Menu Position:", contextMenuPosition);
  // console.log("showSettings:", showSettings);

  // console.log("Selected Geometry:", selectedGeometry);
  // console.log("selectedGeometry Name: ", selectedGeometry?.name);
  // console.log("Selected Geometry ID:", selectedGeometry?.id);
  // console.log("Selected Geometry Positions:");
  // console.log(
  //   geometries.find((geo) => geo.id === selectedGeometry?.id)?.positions.map((point) =>
  //     convertCartesianToDegrees(point)
  //   )
  // );

  // SHIP DATA
  console.log("SHIP DATA:");
  console.log(vessels);
  console.log("SHIP NAME:");
  if (selectedGeometry?.name) {
    console.log(selectedGeometry.name.split(": ")[1]);
  } else {
    console.log("No ship selected.");
  }
  const vesselData = vessels.find(
    (vessel) => vessel.vessel_name === selectedGeometry?.name.split(": ")[1]
  );
  console.log("Selected Ship data: ", vesselData);
  console.log("Selected ship position:");
  console.log(vesselData?.geom);

  return (
    <div className="cesium-viewer">
      <ToastContainer />

      <Viewer
        ref={viewerRef}
        full
        timeline={false}
        animation={false}
        homeButton={true}
        baseLayerPicker={true}
        navigationHelpButton={false}
        sceneModePicker={true}
        geocoder={true}
        infoBox={true}
        selectionIndicator={true}
      >
        {vessels.map((vessel) =>
          placeVessel(
            vessel["lon"],
            vessel["lat"],
            vessel["heading"],
            0,
            vessel["type"],
            vessel["vessel_name"]
          ) || <div key={vessel["mmsi"]}>Invalid Vessel Data</div>
        )}

        {predictions && predictions.map((item, index) => placeDot(item))}

        <CustomGeometry
          viewer={viewerRef}
          viewerReady={viewerReady}
          isDrawing={isDrawing}
          geometries={geometries}
          setGeometries={setGeometries}
          setSelectedGeometry={setSelectedGeometry}
          setShowContextMenu={setShowContextMenu}
          setContextMenuPosition={setContextMenuPosition}
          setShowSettings={setShowSettings}
          setClickedCoordinates={setClickedCoordinates}
        />
      </Viewer>

      <ToolsUI
        onToggleFilters={() => handleToggleFilters(setShowFilters)}
        apiEndpoint={filtersAPI}
        onFilterApply={handleFilterApply}
        onToggleDrawing={() => handleToggleDrawing(isDrawing, setIsDrawing)}
        onUndo={() => handleUndo(setGeometries)}
        onClear={() => handleClear(setShowClearDialog)}
        onToggleOverlays={() => handleToggleOverlays(showOverlays, setShowOverlays)}
      />

      {showContextMenu && selectedGeometry && (
        <div
          className="context-menu"
          style={{ top: contextMenuPosition.y, left: contextMenuPosition.x }}
        >
          <button onClick={() => {setShowSettings(true); setShowContextMenu(false);}}>Settings</button>
          <button onClick={() => handleDelete(setShowContextMenu, setShowDeleteDialog)}>
            Delete
          </button>
          <button onClick={() => setShowSettings(true)}>Rename</button>
          <button onClick={() => {handlePathPrediction()}}>Predict Path</button>
        </div>
      )}

      {showSettings && selectedGeometry && (
        <ZoneSettingsUI
          zoneName={selectedGeometry.name}
          positions={
            geometries.find((geo) => geo.id === selectedGeometry.id)?.positions
          }
          onRename={(newName) =>
            handleRename(newName, selectedGeometry, viewerRef, setGeometries, setSelectedGeometry)
          }
          onDelete={() => handleDelete(setShowContextMenu, setShowDeleteDialog)}
          onSave={() => handleSave(setShowSettings)}
        />
      )}

      {/* {showFilters && (
        <FiltersUI apiEndpoint={filtersAPI} onFilterApply={handleFilterApply} />
      )} */}

      {showOverlays && (
        <OverlaysUI
          onClose={() => handleToggleOverlays(showOverlays, setShowOverlays)}
          onToggleWeather={() => console.log("Weather Overlay Toggled")}
        />
      )}

      {showClearDialog && (
        <ConfirmationDialog
          message="Are you sure you want to clear all geometries?"
          onConfirm={() =>
            handleClearConfirmed(
              viewerRef,
              setGeometries,
              setSelectedGeometry,
              setShowContextMenu,
              setShowClearDialog
            )
          }
          onCancel={() => handleClearCancelled(setShowClearDialog)}
        />
      )}

      {showDeleteDialog && (
        <ConfirmationDialog
          message="Are you sure you want to delete the selected geometry?"
          onConfirm={() =>
            handleDeleteConfirm(
              selectedGeometry,
              viewerRef,
              setGeometries,
              setSelectedGeometry,
              setShowDeleteDialog
            )
          }
          onCancel={() => handleDeleteCancel(setShowDeleteDialog)}
        />
      )}
    </div>
  );
}

export default App;
