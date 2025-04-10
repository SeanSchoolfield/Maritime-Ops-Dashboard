import { useEffect, useState } from "react";
import useRightClickContextMenu from "./hooks/useRightClickContextMenu";
import useLeftClickSelect from "./hooks/useLeftClickSelect";
import useDrawingHandler from "./hooks/useDrawingHandler";

/**
 * CustomGeometry component to handle geometry drawing and interaction in Cesium.
 * @param {Object} props - Component props.
 * @param {Object} props.viewer - Cesium viewer instance.
 * @param {boolean} props.viewerReady - Flag indicating if the viewer is ready.
 * @param {boolean} props.isDrawing - Flag indicating if drawing mode is active.
 * @param {Function} props.setSelectedGeometry - Function to set the selected geometry.
 * @param {Function} props.setShowContextMenu - Function to show or hide the context menu.
 * @param {Function} props.setContextMenuPosition - Function to set the context menu position.
 * @param {Function} props.setShowSettings - Function to show or hide settings.
 * @param {Array} props.geometries - Array of existing geometries.
 * @param {Function} props.setGeometries - Function to update the geometries state.
 * @returns {null}
 * @description This component sets up event handlers for drawing polygons and handling context menu interactions.
 * It uses custom hooks to manage the drawing state and interactions with the Cesium viewer.
 */

const CustomGeometry = ({
    viewer,
    viewerReady,
    isDrawing,
    setSelectedGeometry,
    setShowContextMenu,
    setContextMenuPosition,
    setShowSettings,
    geometries,
    setGeometries,
}) => {
const CustomGeometry = ({ viewer, viewerReady, isDrawing, setSelectedGeometry, setShowContextMenu, setContextMenuPosition, setShowSettings, geometries, setGeometries, setClickedCoordinates }) => {
    const [positions, setPositions] = useState([]);

    // Call hooks at the top level
    const scene = viewerReady && viewer?.current?.cesiumElement?.scene;
    
    useRightClickContextMenu(scene, setSelectedGeometry, setContextMenuPosition, setShowContextMenu);
    useLeftClickSelect(scene, setSelectedGeometry, setShowContextMenu, setShowSettings);
    useDrawingHandler(scene, isDrawing, positions, setPositions, viewer, geometries, setGeometries);
    const handlerRef = useRef(null);
    const lastClickTimeRef = useRef(0);
    const doubleClickDetectedRef = useRef(false);
    

    useEffect(() => {
        if (!scene) return;

        // Prevent default context menu
        scene.canvas.addEventListener("contextmenu", (e) => e.preventDefault());

        const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);
        handlerRef.current = handler;

        // Right-click to open context menu -> useRightClickContextMenu.js
        handler.setInputAction((click) => {
            console.log("Right-click registered at position:", click.position);
            const pickedEntity = scene.pick(click.position);
            const cartesian = scene.camera.pickEllipsoid(click.position, scene.globe.ellipsoid);
            
            if (cartesian) {
                const cartographic = Cesium.Cartographic.fromCartesian(cartesian);
                const longitude = Cesium.Math.toDegrees(cartographic.longitude);
                const latitude = Cesium.Math.toDegrees(cartographic.latitude);
                setClickedCoordinates({ lat: latitude, lon: longitude });
                console.log("Converted coordinates:", { latitude, longitude });
            }

            if (Cesium.defined(pickedEntity)) {
                console.log("Right-click on entity:", pickedEntity);
                setSelectedGeometry(pickedEntity.id);
                setContextMenuPosition({ x: click.position.x, y: click.position.y });
                setShowContextMenu(true);
            } else {
                setShowContextMenu(false);
            }
        }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);

        // Left-click to select polygons -> useSelectGeometry.js
        handler.setInputAction((click) => {
            console.log("Left-click registered at position:", click.position);
            const pickedEntity = scene.pick(click.position);
            if (Cesium.defined(pickedEntity)) {
                console.log("Left-click on entity:", pickedEntity);
                setSelectedGeometry(pickedEntity.id);
            } else {
                setShowContextMenu(false);
                setShowSettings(false);
                setSelectedGeometry(null);
            }
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

        if (isDrawing) {
            // Left-click to start geometry
            handler.setInputAction((click) => {
                const currentTime = Date.now();

                if (currentTime - lastClickTimeRef.current < 300) {
                    // double left-click detected
                    doubleClickDetectedRef.current = true;
                    return;
                }

                doubleClickDetectedRef.current = false;
                lastClickTimeRef.current = currentTime;

                setTimeout(() => {
                    if (!doubleClickDetectedRef.current) {
                        let cartesian = scene.pickPosition(click.position);
                        if (!cartesian) {
                            cartesian = scene.camera.pickEllipsoid(click.position, scene.globe.ellipsoid);
                        }
                        console.log("Drawing left-click registered at position:", click.position, "Cartesian:", cartesian);
                        if (cartesian) {
                            const { latitude, longitude } = convertCartesianToDegrees(cartesian);
                            console.log("Converted coordinates:", { latitude, longitude });
                            setPositions((prevPositions) => [...prevPositions, cartesian]);
                        }
                    }
                }, 300);
            }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

            // Double-click to complete geometry
            handler.setInputAction(() => {
                console.log("Double-click registered to complete geometry");
                if (positions.length > 2) {
                    const newPolygon = viewer.current.cesiumElement.entities.add({
                        polygon: {
                            hierarchy: new Cesium.PolygonHierarchy(positions),
                            material: Cesium.Color.RED.withAlpha(0.5),
                        },
                        name: `Zone ${geometries.length + 1}`,
                        isGeometry: true, // Add custom property to identify geometry
                    });

                    setGeometries((prevGeometries) => [
                        ...prevGeometries,
                        { id: newPolygon.id, positions: [...positions] },
                    ]);

                    setPositions([]); // Resets positions for next polygon
                }

                // Reset the double-click flag after handling the double-click
                setTimeout(() => {
                    doubleClickDetectedRef.current = false;
                }, 300);
            }, Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);
        }

        return () => {
            scene.canvas.removeEventListener("contextmenu", (e) => e.preventDefault());
        };
    }, [scene]);

    return null;
};

export default CustomGeometry;