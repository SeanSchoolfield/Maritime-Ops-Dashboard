import { useEffect } from "react";
import * as Cesium from "cesium";

/**
 * Custom hook to handle right-click context menu in Cesium.
 * @param {Object} scene - The Cesium scene object.
 * @param {Function} setSelectedGeometry - Function to set the selected geometry.
 * @param {Function} setContextMenuPosition - Function to set the context menu position.
 * @param {Function} setShowContextMenu - Function to show or hide the context menu.
 * @returns {void}
 * @description This hook sets up a right-click event handler on the Cesium canvas.
 */

const useRightClickContextMenu = (scene, setSelectedGeometry, setContextMenuPosition, setShowContextMenu) => {
    useEffect(() => {
        if (!scene) return;
        
        const handler = new Cesium.ScreenSpaceEventHandler(scene.canvas);
        
        handler.setInputAction((click) => {
            console.log("Right-click registered at position:", click.position);
            const pickedEntity = scene.pick(click.position);
            if (Cesium.defined(pickedEntity)) {
                console.log("Right-click on entity:", pickedEntity);
                setSelectedGeometry(pickedEntity.id);
                setContextMenuPosition({ x: click.position.x, y: click.position.y });
                setShowContextMenu(true);
            } else {
                setShowContextMenu(false);
            }
        }, Cesium.ScreenSpaceEventType.RIGHT_CLICK);

        return () => {
            handler.destroy();
        };
    }, [scene, setSelectedGeometry, setContextMenuPosition, setShowContextMenu]);
};

export default useRightClickContextMenu;