import { useEffect } from "react";
import * as Cesium from "cesium";

/**
 * Custom hook to handle left-click selection in Cesium.
 * @param {Object} scene - The Cesium scene object.
 * @param {Function} setSelectedGeometry - Function to set the selected geometry.
 * @param {Function} setShowContextMenu - Function to show or hide the context menu.
 * @param {Function} setShowSettings - Function to show or hide settings.
 * @returns {void}
 * @description This hook sets up a left-click event handler on the Cesium canvas.
 * It handles left-click to select entities and updates the selected geometry state.
 */

const useLeftClickSelect = (scene, setSelectedGeometry, setShowContextMenu, setShowSettings) => {
    useEffect(() => {
        if (!scene) return;

        const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);

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

        return () => {
            handler.destroy();
        };
    }, [scene, setSelectedGeometry, setShowContextMenu, setShowSettings]);
};

export default useLeftClickSelect;