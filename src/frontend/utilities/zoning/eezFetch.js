import axios from "axios";
import { toast } from "react-toastify";
import { Color, GeoJsonDataSource } from "cesium";

/**
 * Fetches EEZ data from API
 * @param {Object} viewer - The Cesium viewer instance
 * @returns {Promise<void>}
 */

export const fetchEEZZones = async (eezAPI) => {
  try {
    const response = await axios.get(eezAPI);

    if (
      !response.data ||
      !response.data.payload ||
      response.data.payload.length === 0
    ) {
      toast.info("No EEZ zones found.");
      return [];
    }

    return response.data.payload;
  } catch (error) {
    console.error("Error fetching EEZ zones:", error.message);
    toast.error("Failed to load EEZ zones.");
    return [];
  }
};

/**
 * Loads EEZ zones onto the Cesium globe
 * @param {Object} viewer - The Cesium viewer instance
 * @param {Array} zones - The EEZ zone data
 * @returns {Promise<Object>} - The data source containing the EEZ zones
 */

export const loadEEZZonesToGlobe = async (viewer, zones) => {
  if (!viewer || !zones || zones.length === 0) return null;

  try {
    // Create a data source for EEZ zones
    const dataSource = new GeoJsonDataSource("EEZ Zones");

    // Define EEZ color {Chose Purple}
    const brightPurple = Color.PURPLE;
    const brightPurpleTransparent = Color.PURPLE.withAlpha(0.4);

    // Process each zone
    for (const zone of zones) {
      // Parse the geometry if it's a string
      const geometry =
        typeof zone.geom === "string" ? JSON.parse(zone.geom) : zone.geom;

      // Create a GeoJSON feature
      // Takes GeoJSON data and converts into Cesium entities
      const feature = {
        type: "Feature",
        properties: {
          id: zone.id,
          name: zone.name || `EEZ Zone ${zone.id}`,
          type: "EEZ",
        },
        geometry: geometry,
      };

      // Load the feature
      // With colored polygon on globe
      const featureDataSource = await GeoJsonDataSource.load(feature, {
        stroke: brightPurple,
        fill: brightPurpleTransparent,
        strokeWidth: 3,
      });

      // Add entities to our main data source
      const entities = featureDataSource.entities.values;
      for (let i = 0; i < entities.length; i++) {
        const entity = entities[i];

        // Style the entity with bright purple
        entity.polygon.material = brightPurpleTransparent;
        entity.polygon.outlineColor = brightPurple;
        entity.polygon.outlineWidth = 3;

        // IMPORTANT: Add this to differentiate EEZ from user polygons
        // CODE HAS BEEN CHANGFD
        entity.properties = entity.properties || {};
        entity.properties.isEEZ = true;

        // Add to the main data source
        dataSource.entities.add(entity);
      }
    }

    // Add the data source to the viewer
    await viewer.dataSources.add(dataSource);

    console.log("EEZ data source added successfully: ", dataSource);
    return dataSource;
  } catch (error) {
    console.error("Error loading EEZ zones to globe:", error);
    toast.error("Failed to display EEZ zones on the globe.");
    return null;
  }
};

/**
 * Toggles the visibility of EEZ zones
 * @param {Object} viewer - The Cesium viewer instance
 * @param {boolean} currentVisibility - The current visibility state
 * @param {Function} setVisibility - State setter for visibility
 * @param {string} eezAPI - API endpoint for EEZ data
 */
export const toggleEEZVisibility = async (
  viewer,
  currentVisibility,
  setVisibility,
  eezAPI
) => {
  if (!viewer) return;

  // Find the EEZ data source
  const eezDataSources = viewer.dataSources.getByName("EEZ Zones");

  if (eezDataSources && eezDataSources.length > 0) {
    // Toggle visibility of existing data source
    eezDataSources[0].show = !currentVisibility;
    setVisibility(!currentVisibility);
    toast.info(`EEZ zones ${!currentVisibility ? "shown" : "hidden"}`);
  } else if (!currentVisibility) {
    // If toggling on and data source doesn't exist, load it
    try {
      setVisibility(true);
      const zones = await fetchEEZZones(eezAPI);

      console.log("Fetched EEZ ZONES: ", zones);

      await loadEEZZonesToGlobe(viewer, zones);
      toast.success("EEZ zones loaded successfully!");
    } catch (error) {
      console.error("Error loading EEZ zones:", error);
      toast.error("Failed to load EEZ zones.");
      setVisibility(false);
    }
  }
};
