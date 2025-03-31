/* 
    Consider: Creating hook files for current handlers and logic
    - useEventHandler.js
    - useSelectGeometry.js
    - useDoubleClickToComplete.js
    - useRightClickContextMenu.js
*/

import { useEffect, useRef, useState } from "react";
import { convertCartesianToDegrees } from "./coordUtils";
import * as Cesium from "cesium";

const CustomGeometry = ({ viewer, viewerReady, isDrawing, setSelectedGeometry, setShowContextMenu, setContextMenuPosition, setShowSettings, geometries, setGeometries, setClickedCoordinates }) => {
    const [positions, setPositions] = useState([]);
    const handlerRef = useRef(null);
    const lastClickTimeRef = useRef(0);
    const doubleClickDetectedRef = useRef(false);
    

    useEffect(() => {
        console.log("useEffect executed", { viewerReady, isDrawing });

        if (!viewerReady || !viewer?.current.cesiumElement) return; // -> !viewer?.current.cesiumElement -> useEventHandler.js

        const scene = viewer.current.cesiumElement.scene;

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
            if (handlerRef.current) {
                handlerRef.current.destroy();
                handlerRef.current = null;
            }
        };
    }, [viewerReady, isDrawing, positions, viewer, setGeometries, setSelectedGeometry, setShowContextMenu, setContextMenuPosition, setShowSettings]);

    return null;
};

export default CustomGeometry;

// Previous implementation, KEEP!! (for now)
// import { useEffect } from "react";

// import { Entity, PolylineGraphics, PolygonGraphics, PointGraphics, pick } from "resium";
// import * as Cesium from "cesium";

// const CustomGeometry = ({ viewer, viewerReady, isDrawing, shapeType, geometries, setGeometries, setSelectedGeometry, setShowContextMenu, setContextMenuPosition, setShowSettings }) => {
//     useEffect(() => {
//         if (!viewerReady || !viewer.current?.cesiumElement) return;

//         const scene = viewer.current.cesiumElement.scene;

//         // Disables native browser context menu.
//         scene.canvas.addEventListener("contextmenu", (e) => e.preventDefault());

//         const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);

//         // Right-click context menu
//         handler.setInputAction((click) => {
//             const pickedEntity = scene.pick(click.position);
//             console.log("Right-click registered at position:", click.position);
//             if (Cesium.defined(pickedEntity)) {
//                 console.log("Right-click on entity:", pickedEntity);
//                 // const selectedGeo = geometries.find(geo => geo === pickedEntity);
//                 setSelectedGeometry(pickedEntity);
//                 setContextMenuPosition({ x: click.position.x, y: click.position.y });
//                 setShowContextMenu(true);
//                 console.log("Context menu should be displayed");
//             } else {
//                 setShowContextMenu(false);
//             }
//         }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);

//         // Left-click to select entities (geometries ATM)
//         handler.setInputAction((click) => {
//             const pickedEntity = scene.pick(click.position);
//             console.log("Left-click registered at position:", click.position);
//             if (Cesium.defined(pickedEntity)) {
//                 console.log("Left-click on entity:", pickedEntity);
//                 // const selectedGeo = geometries.find(geo => geo === pickedEntity);
//                 setSelectedGeometry(pickedEntity);
//             } else {
//                 setShowContextMenu(false);
//                 setShowSettings(false);
//                 setSelectedGeometry(null);
//             }
//         }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

//         if (isDrawing) {
//             // Left click to start geometry
//             handler.setInputAction((click) => {
//                 let cartesian = scene.pickPosition(click.position);
//                 if (!cartesian) {
//                     cartesian = scene.camera.pickEllipsoid(click.position, scene.globe.ellipsoid);
//                 }
//                 console.log("Drawing left-click registered at position:", click.position, "Cartesian:", cartesian);
//                 if (cartesian) {
//                     setGeometries((prev) => {
//                         if (prev.length === 0 || prev[prev.length - 1].completed) {
//                             const newZoneId = `zone-${Date.now()}`;
//                             const newZoneName = `Zone ${prev.length + 1}`;
//                             console.log("Starting new geometry:", newZoneName);
//                             return [...prev, { id: newZoneId, shapeType, positions: [cartesian], completed: false, name: newZoneName }];
//                         } else {
//                             const updated = [...prev];
//                             updated[updated.length - 1].positions.push(cartesian);
//                             console.log("Adding point to existing geometry:", updated[updated.length - 1]);
//                             return updated;
//                         }
//                     });
//                 }
//             }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

//             // Double click to complete geometry
//             handler.setInputAction(() => {
//                 console.log("Double-click registered to complete geometry");
//                 setGeometries((prev) => {
//                     if (prev.length === 0) return prev;
//                     const updated = [...prev];
//                     updated[updated.length - 1].completed = true;
//                     console.log("Completed geometry:", updated[updated.length - 1]);
//                     return updated;
//                 });
//             }, Cesium.ScreenSpaceEventType.LEFT_DOUBLE_CLICK);
//         }

//         return () => {
//             handler.destroy();
//         };
//     }, [viewer, viewerReady, isDrawing, shapeType, geometries, setGeometries, setSelectedGeometry, setShowContextMenu, setContextMenuPosition, setShowSettings]);

//     return (
//         <div>
//             {geometries.map((geometry) => (
//                 <Entity key={geometry.id} name={geometry.name}>
//                     {geometry.shapeType === "polyline" && (
//                         <PolylineGraphics positions={geometry.positions} material={Cesium.Color.RED} width={3} />
//                     )}
//                     {geometry.shapeType === "polygon" && (
//                         <PolygonGraphics
//                             hierarchy={new Cesium.PolygonHierarchy(geometry.positions)}
//                             material={Cesium.Color.RED.withAlpha(0.5)}
//                         />
//                     )}
//                     {geometry.shapeType === "point" &&
//                         geometry.positions.map((pos, i) => (
//                             <Entity key={`${geometry.id}-${i}`} position={pos}>
//                                 <PointGraphics pixelSize={10} color={Cesium.Color.BLACK} />
//                             </Entity>
//                         ))}
//                 </Entity>
//             ))}
//         </div>
//     );
// };

// export default CustomGeometry;