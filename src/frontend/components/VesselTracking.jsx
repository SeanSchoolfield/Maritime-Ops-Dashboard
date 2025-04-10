// Component for tracking, need to fetch 

import { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { SceneMode } from 'cesium';

/**
 * Custom hook for vessel tracking and view mode changes
 * @param {Object} viewerRef - Reference to the Cesium viewer
 * @param {string} apiEndpoint - API endpoint for vessel data
 * @returns {Object} - Vessel state and control functions
 */
const useVesselTracking = (viewerRef, apiEndpoint) => {
  const [vessels, setVessels] = useState([]);
  const [viewerReady, setViewerReady] = useState(false);
  const [currentSceneMode, setCurrentSceneMode] = useState(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  
  // Fetch vessels from API
  const fetchVessels = async (filters = {}, showToast = true) => {
    try {
      const response = await axios.get(apiEndpoint, { params: filters });

      if (response.data.length === 0) {
        if (showToast) {
          toast.info("No vessels found matching your filters.", {
            position: "bottom-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: false,
            draggable: false,
          });
        }
        setVessels([]);  // Clear vessels
        return;
      }

      console.log("Fetched Vessels (Raw Data):", response.data);

      const transformedVessels = response.data.map((vessel) =>
        Array.isArray(vessel)
          ? {
            id: vessel['mmsi'],
            name: vessel['vessel_name'],
            type: vessel['type'],
            country_of_origin: vessel['flag'],
            status: vessel['current_status'],
            latitude: vessel['lat'],
            longitude: vessel['lon']
          }
          : vessel
      );

      console.log("Transformed Vessels:", transformedVessels);
      setVessels(transformedVessels);

    } catch (error) {
      if (error.response?.status === 500) {
        if (showToast) {
          toast.error("Server error occurred. Please try again later.", {
            position: "bottom-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: false,
            draggable: false,
          });
        }
      } else {
        if (showToast) {
          toast.info("No vessels found matching your filters.", {
            position: "bottom-right",
            autoClose: 3000,
            hideProgressBar: true,
            closeOnClick: true,
            pauseOnHover: false,
            draggable: false,
          });
        }
      }

      console.error("Error fetching vessels:", error.message);
      setVessels([]);  // Clear vessels
    }
  };

  // Setup viewer and event listeners
  useEffect(() => {
    fetchVessels({}, false);  // Initial fetch without toast notification

    if (viewerRef.current && viewerRef.current.cesiumElement) {
      const viewer = viewerRef.current.cesiumElement;
      setViewerReady(true);
      
      // Initialize current scene mode
      setCurrentSceneMode(viewer.scene.mode);
      
      // Set up event listeners for scene mode transition
      const sceneModeStartHandler = () => {
        setIsTransitioning(true);
        console.log("Scene mode transition starting");
      };
      
      const sceneModeCompleteHandler = () => {
        // Update the current scene mode
        const newSceneMode = viewer.scene.mode;
        setCurrentSceneMode(newSceneMode);
        
        
        // Handle selected entity
        if (viewer.selectedEntity) {
          const currentEntity = viewer.selectedEntity;
          viewer.selectedEntity = undefined;
          setTimeout(() => {
            viewer.selectedEntity = currentEntity;
          }, 100);
        }
        
        // Recreate all vessel entities with the new scene mode
        if (vessels.length > 0) {
          console.log(`View mode changed to ${getSceneModeName(newSceneMode)} - recreating vessel entities`);
          
          // Use a longer timeout to ensure the mode change is fully complete
          setTimeout(() => {
            // First remove all existing vessel entities
            const entities = viewer.entities.values.filter(entity => 
              entity.name && entity.name.includes('Vessel:')
            );
            
            console.log(`Removing ${entities.length} existing vessel entities`);
            entities.forEach(entity => {
              viewer.entities.remove(entity);
            });
            
            // Force a complete recreation by creating a new array with the current scene mode
            const vesselsCopy = [...vessels];
            console.log(`Recreating ${vesselsCopy.length} vessel entities in ${getSceneModeName(newSceneMode)} mode`);
            setVessels(vesselsCopy);
            
            // Reset transition flag after recreation is complete
            setIsTransitioning(false);
          }, 700); // Increased timeout for more reliable transition
        } else {
          setIsTransitioning(false);
        }
      };

      // Add listeners for both transition start and completion
      viewer.scene.morphStart.addEventListener(sceneModeStartHandler);
      viewer.scene.morphComplete.addEventListener(sceneModeCompleteHandler);

      return () => {
        if (viewer && viewer.scene && !viewer.isDestroyed()) {
          viewer.scene.morphStart.removeEventListener(sceneModeStartHandler);
          viewer.scene.morphComplete.removeEventListener(sceneModeCompleteHandler);
        }
      };
    }
  }, [viewerRef.current]);

  // Helper function to get scene mode name for logging
  const getSceneModeName = (sceneMode) => {
    switch(sceneMode) {
      case SceneMode.SCENE3D: return "3D";
      case SceneMode.SCENE2D: return "2D";
      case SceneMode.COLUMBUS_VIEW: return "Columbus View";
      default: return "Unknown";
    }
  };

  return {
    vessels,
    viewerReady,
    currentSceneMode,
    isTransitioning,
    fetchVessels,
    getSceneModeName
  };
};

export default useVesselTracking;
