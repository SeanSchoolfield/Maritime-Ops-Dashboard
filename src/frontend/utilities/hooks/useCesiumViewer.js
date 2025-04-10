import { useEffect } from "react";

/**
 * Custom hook to manage Cesium viewer lifecycle and scene mode change events.
 *
 * @param {Object} viewerRef - Reference to the Cesium viewer.
 * @param {Function} setViewerReady - Function to set the viewer ready state.
 * @returns {void}
 * @description This hook sets up an event listener for scene mode changes in the Cesium viewer.
 */

export const useCesiumViewer = (viewerRef, setViewerReady) => {
  useEffect(() => {
    if (viewerRef.current && viewerRef.current.cesiumElement) {
      const viewer = viewerRef.current.cesiumElement;
      setViewerReady(true);

      const sceneModeChangeHandler = () => {
        if (viewer.selectedEntity) {
          const currentEntity = viewer.selectedEntity;
          viewer.selectedEntity = undefined;
          setTimeout(() => {
            viewer.selectedEntity = currentEntity;
          }, 100);
        }
      };

      viewer.scene.morphComplete.addEventListener(sceneModeChangeHandler);

      return () => {
        if (viewer && viewer.scene && !viewer.isDestroyed()) {
          viewer.scene.morphComplete.removeEventListener(sceneModeChangeHandler);
        }
      };
    }
  }, [viewerRef.current]);
};