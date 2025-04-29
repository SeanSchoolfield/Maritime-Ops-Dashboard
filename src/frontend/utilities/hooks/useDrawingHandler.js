import { useEffect, useRef, useState } from "react";
import * as Cesium from "cesium";
import { convertCartesianToDegrees } from "../coordUtils";
import { generateZoneDescription } from "../zoning/ZoneInfobox";

/**
 * Custom hook to handle drawing polygons on a Cesium scene.
 * @param {Object} scene - The Cesium scene object.
 * @param {boolean} isDrawing - Flag to indicate if drawing mode is active.
 * @param {Array} positions - Array of positions for the polygon.
 * @param {Function} setPositions - Function to update the positions state.
 * @param {Object} viewer - The Cesium viewer object.
 * @param {Array} geometries - Array of existing geometries.
 * @param {Function} setGeometries - Function to update the geometries state.
 * @param {Object} activeZone - The currently active zone for drawing.
 * @param {Function} setActiveZone - Function to update the active zone state.
 * @returns {void}
 * @description This hook sets up event handlers for drawing polygons on the Cesium canvas.
 * It handles left-click for adding points and right-click for completing the polygon.
 */

const useDrawingHandler = (
  scene,
  isDrawing,
  positions,
  setPositions,
  viewer,
  geometries,
  setGeometries,
  activeZone,
  setActiveZone
) => {
  const lastClickTimeRef = useRef(0);
  const doubleClickDetectedRef = useRef(false);

  useEffect(() => {
    console.log("useDrawingHandler activeZone:", activeZone);
    console.log("useDrawingHandler positions:", positions);
  }, [activeZone, positions]);

  useEffect(() => {
    if (!scene || !isDrawing) return;

    const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);

    // Left-click to draw
    handler.setInputAction((click) => {
      let cartesian = scene.pickPosition(click.position);
      if (!cartesian) {
        cartesian = scene.camera.pickEllipsoid(
          click.position,
          scene.globe.ellipsoid
        );
      }
      if (cartesian) {
        convertCartesianToDegrees(cartesian);

        if (!activeZone) {
          // Create a new zone entity when we start drawing
          const zoneEntity = viewer.current.cesiumElement.entities.add({
            polygon: {
              hierarchy: new Cesium.PolygonHierarchy([]),
              material: Cesium.Color.RED.withAlpha(0.5),

              // Add height
              height: 1,
              heightReference: Cesium.HeightReference.RELATIVE_TO_GROUND,
            },
            name: `Zone ${geometries.length + 1}`,
            description: generateZoneDescription(
              `Zone ${geometries.length + 1}`,
              null
            ),
            isGeometry: true,
            // Mark as user drawn entity
            properties: {
              isUserDrawn: true,
            },
          });

          const newActiveZone = {
            id: zoneEntity.id,
            entity: zoneEntity,
            points: [],
          };
          setActiveZone(newActiveZone);
          console.log("New active zone created:", newActiveZone);

          const pointEntity = viewer.current.cesiumElement.entities.add({
            position: cartesian,
            point: {
              pixelSize: 10,
              color: Cesium.Color.RED,
              outlineColor: Cesium.Color.WHITE,
              outlineWidth: 2,
            },
            name: `Point ${positions.length + 1}`,
            label: {
              text: `Point ${positions.length + 1}`,
              font: "14px Helvetica",
              scale: 0.8,
              pixelOffset: new Cesium.Cartesian2(0, -20),
            },
            parent: zoneEntity,
          });

          setPositions((prevPositions) => [...prevPositions, cartesian]);
          setActiveZone((prevZone) => ({
            ...newActiveZone,
            points: [...(prevZone?.points || []), pointEntity],
          }));
        } else {
          const pointEntity = viewer.current.cesiumElement.entities.add({
            position: cartesian,
            point: {
              pixelSize: 10,
              color: Cesium.Color.RED,
              outlineColor: Cesium.Color.WHITE,
              outlineWidth: 2,
            },
            name: `Point ${positions.length + 1}`,
            label: {
              text: `Point ${positions.length + 1}`,
              font: "14px Helvetica",
              scale: 0.8,
              pixelOffset: new Cesium.Cartesian2(0, -20),
            },
            parent: activeZone.entity,
          });

          setPositions((prevPositions) => [...prevPositions, cartesian]);
          setActiveZone((prevZone) => ({
            ...prevZone,
            points: [...(prevZone?.points || []), pointEntity],
          }));
        }
      }
    }, Cesium.ScreenSpaceEventType.LEFT_CLICK);

    // Right-click to complete geometry
    handler.setInputAction((click) => {
      console.log("Right click detected");
      console.log("Current positions array:", positions);
      console.log("Current activeZone:", activeZone);

      if (positions.length > 2 && activeZone) {
        console.log("Completing polygon with positions:", positions);

        // // Ensure the polygon renders above EEZ zones
        // activeZone.entity.polygon.heightReference =
        //   Cesium.HeightReference.RELATIVE_TO_GROUND;
        activeZone.entity.polygon.height = 1;

        // Update the polygon hierarchy with the current positions
        activeZone.entity.polygon.hierarchy = new Cesium.PolygonHierarchy(
          positions
        );

        // Make sure the entity has a description
        if (!activeZone.entity.description) {
          activeZone.entity.description = generateZoneDescription(
            activeZone.entity.name,
            null
          );
        }

        // Add to geometries collection
        setGeometries((prevGeometries) => [
          ...prevGeometries,
          {
            id: activeZone.id,
            entity: activeZone.entity,
            positions: [...positions],
            points: activeZone.points,
          },
        ]);

        // Reset for the next drawing
        setActiveZone(null);
        setPositions([]);
        console.log("Zone completed successfully");
      } else {
        console.log("Not enough points to complete polygon or no active zone");
        console.log("Positions length:", positions.length);
        console.log("Active zone exists:", !!activeZone);
        console.log("Not enough points to complete polygon or no active zone");
      }

      setTimeout(() => {
        doubleClickDetectedRef.current = false;
      }, 300);
    }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);

    return () => {
      handler.destroy();
    };
  }, [
    scene,
    isDrawing,
    positions,
    setPositions,
    viewer,
    geometries,
    setGeometries,
    activeZone,
    setActiveZone,
  ]);
};

export default useDrawingHandler;
