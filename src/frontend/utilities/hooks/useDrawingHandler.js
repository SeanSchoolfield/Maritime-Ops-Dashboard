import { useEffect, useRef, useState } from "react";
import * as Cesium from "cesium";
import { convertCartesianToDegrees } from "../coordUtils";

/**
 * Custom hook to handle drawing polygons on a Cesium scene.
 * @param {Object} scene - The Cesium scene object.
 * @param {boolean} isDrawing - Flag to indicate if drawing mode is active.
 * @param {Array} positions - Array of positions for the polygon.
 * @param {Function} setPositions - Function to update the positions state.
 * @param {Object} viewer - The Cesium viewer object.
 * @param {Array} geometries - Array of existing geometries.
 * @param {Function} setGeometries - Function to update the geometries state.
 * @returns {void}
 * @description This hook sets up event handlers for drawing polygons on the Cesium canvas.
 * It handles left-click for adding points and double-click for completing the polygon.
 */

const useDrawingHandler = (scene, isDrawing, positions, setPositions, viewer, geometries, setGeometries) => {
    const lastClickTimeRef = useRef(0);
    const doubleClickDetectedRef = useRef(false);
    const [activeZone, setActiveZone] = useState(null); // Track the active zone being created

    useEffect(() => {
        if (!scene || !isDrawing) return;

        const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);

        // Left-click to draw
        handler.setInputAction((click) => {
            const currentTime = Date.now();

            if (currentTime - lastClickTimeRef.current < 300) {
                // Double left-click detected
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

                        // Create the active zone if it doesn't exist
                        if (!activeZone) {
                            const zoneEntity = viewer.current.cesiumElement.entities.add({
                                polygon: {
                                    hierarchy: new Cesium.PolygonHierarchy([]), // Empty hierarchy for now
                                    material: Cesium.Color.RED.withAlpha(0.5),
                                },
                                name: `Zone ${geometries.length + 1}`,
                                isGeometry: true, // Add custom property to identify geometry
                            });

                            // Use a local variable to reference the active zone immediately
                            const newActiveZone = { id: zoneEntity.id, entity: zoneEntity, points: [] };
                            setActiveZone(newActiveZone);

                            // Add the first point to the new active zone
                            const pointEntity = viewer.current.cesiumElement.entities.add({
                                position: cartesian,
                                point: {
                                    pixelSize: 10,
                                    color: Cesium.Color.RED,
                                    outlineColor: Cesium.Color.WHITE,
                                    outlineWidth: 2,
                                },
                                name: `Point ${positions.length + 1}`,
                                parent: zoneEntity, // Use the local variable for the parent
                            });

                            console.log("Point entity created:", pointEntity);

                            // Update the positions and active zone points
                            setPositions((prevPositions) => [...prevPositions, cartesian]);
                            setActiveZone((prevZone) => ({
                                ...newActiveZone,
                                points: [...(prevZone?.points || []), pointEntity],
                            }));

                            console.log("Active Zone Points:", newActiveZone.points);
                        } else {
                            // Add subsequent points to the existing active zone
                            const pointEntity = viewer.current.cesiumElement.entities.add({
                                position: cartesian,
                                point: {
                                    pixelSize: 10,
                                    color: Cesium.Color.RED,
                                    outlineColor: Cesium.Color.WHITE,
                                    outlineWidth: 2,
                                },
                                name: `Point ${positions.length + 1}`,
                                parent: activeZone.entity, // Use the existing active zone
                            });

                            console.log("Point entity created:", pointEntity);

                            // Update the positions and active zone points
                            setPositions((prevPositions) => [...prevPositions, cartesian]);
                            setActiveZone((prevZone) => ({
                                ...prevZone,
                                points: [...(prevZone?.points || []), pointEntity],
                            }));

                            console.log("Active Zone Points:", activeZone.points);
                        }
                    }
                }
            }, 300);
        }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

        // Double-click to complete geometry
        handler.setInputAction(() => {
            console.log("Double-click registered to complete geometry");
            if (positions.length > 2 && activeZone) {
                // Update the active zone's polygon hierarchy
                activeZone.entity.polygon.hierarchy = new Cesium.PolygonHierarchy(positions);

                // Add the completed zone to the geometries state
                setGeometries((prevGeometries) => [
                    ...prevGeometries,
                    { id: activeZone.id, entity: activeZone.entity, positions: [...positions], points: activeZone.points },
                ]);

                // Reset the active zone and positions
                setActiveZone(null);
                setPositions([]);
            }

            // Reset the double-click flag after handling the double-click
            setTimeout(() => {
                doubleClickDetectedRef.current = false;
            }, 300);
        }, Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);

        return () => {
            handler.destroy();
        };
    }, [scene, isDrawing, positions, setPositions, viewer, geometries, setGeometries, activeZone]);

    return activeZone; // Return the active zone if needed elsewhere
};

export default useDrawingHandler;