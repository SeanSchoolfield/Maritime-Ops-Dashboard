import { toast } from "react-toastify";

/** 
 * @description Handles the toggling of the drawing tool.
 * @param {boolean} isDrawing - The current state of the drawing tool.
 * @param {Function} setIsDrawing - Function to update the drawing tool state.
 * @returns {void}
*/
export const handleToggleDrawing = (isDrawing, setIsDrawing) => {
  console.log("Toggled Zoning:", !isDrawing);
  setIsDrawing((prev) => {
    const newState = !prev;

    toast.info(`Zoning Tool ${newState ? "Enabled" : "Disabled"}`, {
      position: "bottom-right",
      autoClose: 2000,
      hideProgressBar: true,
      closeOnClick: true,
      pauseOnHover: false,
      draggable: false,
    });

    if (newState) {
      toast.info(
        `Click on the map to add points. Right click to finish the polygon.`,
        {
          position: "bottom-right",
          autoClose: 5000,
          hideProgressBar: false,
          closeOnClick: true,
          pauseOnHover: true,
          draggable: false,
        }
      );
    }
    return newState;
  });
};

/**
 * @description Handles the toggling of overlays.
 * @param {boolean} showOverlays - The current state of the overlays.
 * @param {Function} setShowOverlays - Function to update the overlays state.
 * @returns {void}
*/
export const handleToggleOverlays = (showOverlays, setShowOverlays) => {
  setShowOverlays((prev) => !prev);
  console.log("Overlays toggled:", !showOverlays);
};

/**
 * @description Handles the toggling of filters.
 * @param {Function} setShowFilters - Function to update the filters state.
 * @returns {void}
*/
export const handleToggleFilters = (setShowFilters) => {
  setShowFilters((prev) => !prev);
};

/**
 * @description Handles the undo action for geometries in progress.

 * @returns {void}
 */
export const handleUndo = (undoLastPoint) => {
  console.log("Undo function passed to handleUndo:", undoLastPoint);
  if(undoLastPoint) {
    undoLastPoint();
  } else {
    console.log("No active zone or points to undo.");
  }
};

/**
 * @description Handles the clearing of geometries.
 * @param {Function} setShowClearDialog - Function to update the clear dialog state.
 * @returns {void}
*/
export const handleClear = (setShowClearDialog) => {
  setShowClearDialog(true);
};

/**
 * @description Handles the confirmation of clearing geometries.
 * @param {Object} viewerRef - Reference to the Cesium viewer.
 * @param {Function} setGeometries - Function to update the geometries state.
 * @param {Function} setSelectedGeometry - Function to update the selected geometry state.
 * @param {Function} setShowContextMenu - Function to update the context menu state.
 * @param {Function} setShowClearDialog - Function to update the clear dialog state.
 * @returns {void}
*/
export const handleClearConfirmed = (
  viewerRef,
  setGeometries,
  setSelectedGeometry,
  setShowContextMenu,
  setShowClearDialog
) => {
  const viewer = viewerRef.current.cesiumElement;
  const entities = viewer.entities.values;
  for (let i = entities.length - 1; i >= 0; i--) {
    const entity = entities[i];
    if (entity.isGeometry || entity.parent) {
      viewer.entities.remove(entity);
      console.log("Removed entity:", entity.id);
    }
  }
  setGeometries([]);
  setSelectedGeometry(null);
  setShowContextMenu(false);
  setShowClearDialog(false);
};

/**
 * @description Handles the cancellation of the clear dialog.
 * @param {Function} setShowClearDialog - Function to update the clear dialog state.
 * @returns {void}
*/
export const handleClearCancelled = (setShowClearDialog) => {
  setShowClearDialog(false);
};

/**
 * @description Handles the renaming of a geometry.
 * @param {string} newName - The new name for the geometry.
 * @param {Object} selectedGeometry - The currently selected geometry.
 * @param {Object} viewerRef - Reference to the Cesium viewer.
 * @param {Function} setGeometries - Function to update the geometries state.
 * @param {Function} setSelectedGeometry - Function to update the selected geometry state.
 * @returns {void}
*/
export const handleRename = (
  newName,
  selectedGeometry,
  viewerRef,
  setGeometries,
  setSelectedGeometry
) => {
  const entity = viewerRef.current.cesiumElement.entities.getById(
    selectedGeometry.id
  );
  if (entity) {
    entity.name = newName;
  }

  setGeometries((prev) =>
    prev.map((geo) =>
      geo.id === selectedGeometry.id ? { ...geo, name: newName } : geo
    )
  );
  setSelectedGeometry((prev) => ({ ...prev, name: newName }));
};

/**
 * @description Handles the deletion of a geometry.
 * @param {Function} setShowContextMenu - Function to update the context menu state.
 * @param {Function} setShowDeleteDialog - Function to update the delete dialog state.
 * @returns {void}
*/
export const handleDelete = (setShowContextMenu, setShowDeleteDialog) => {
  setShowContextMenu(false);
  setShowDeleteDialog(true);
};

/**
 * @description Handles the confirmation of deleting a geometry.
 * @param {Object} selectedGeometry - The currently selected geometry.
 * @param {Object} viewerRef - Reference to the Cesium viewer.
 * @param {Function} setGeometries - Function to update the geometries state.
 * @param {Function} setSelectedGeometry - Function to update the selected geometry state.
 * @param {Function} setShowDeleteDialog - Function to update the delete dialog state.
 * @returns {void}
*/
export const handleDeleteConfirm = (
  selectedGeometry,
  viewerRef,
  setGeometries,
  setSelectedGeometry,
  setShowDeleteDialog
) => {
  if (selectedGeometry) {
    const viewer = viewerRef.current.cesiumElement;
    viewer.entities.removeById(selectedGeometry.id);

    const childEntities = viewer.entities.values;
    for (let i = childEntities.length - 1; i >= 0; i--) {
      const child = childEntities[i];
      if (child.parent && child.parent.id === selectedGeometry.id) {
        viewer.entities.remove(child);
      }
    }

    setGeometries((prev) =>
      prev.filter((geo) => geo.id !== selectedGeometry.id)
    );
    setSelectedGeometry(null);
  }
  setShowDeleteDialog(false);
};

/**
 * @description Handles the cancellation of the delete dialog.
 * @param {Function} setShowDeleteDialog - Function to update the delete dialog state.
 * @returns {void}
*/
export const handleDeleteCancel = (setShowDeleteDialog) => {
  setShowDeleteDialog(false);
};

/**
 * @description Handles the toggling of settings.
 * @param {Function} setShowSettings - Function to update the settings state.
 * @returns {void}
*/
export const handleSave = (setShowSettings) => {
  console.log("Zone settings saved.");
  setShowSettings(false);
};