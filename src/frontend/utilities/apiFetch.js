import axios from "axios";
import { toast } from "react-toastify";

/**
 * Fetches vessels from the API and sets the state.
 * @param {string} vesselsAPI - The API endpoint for fetching vessels.
 * @param {Object} filters - The filters to apply when fetching vessels.
 * @param {Function} setVessels - The state setter function for vessels.
 * @returns {Promise<void>}
 * @description This function constructs the query parameters based on the provided filters,
 */

export const fetchVessels = async (vesselsAPI, filters = {}, setVessels) => {
  const queryParams = {};

  if (filters.types && filters.types.length > 0) {
    queryParams.type = filters.types.join(",");
  }
  if (filters.origin) {
    queryParams.origin = filters.origin;
  }
  if (filters.statuses && filters.statuses.length > 0) {
    queryParams.status = filters.statuses.join(",");
  }

  try {
    const response = await axios.get(vesselsAPI, { params: queryParams });

    if (response.data.length === 0) {
      toast.info("No vessels found matching your filters.");
      setVessels([]);
      return;
    }

    const transformedVessels = response.data.payload?.map((vessel) =>
      Array.isArray(vessel)
        ? {
            id: vessel["mmsi"],
            name: vessel["vessel_name"],
            type: vessel["type"],
            country_of_origin: vessel["flag"],
            status: vessel["current_status"],
            latitude: vessel["lat"],
            longitude: vessel["lon"],
          }
        : vessel
    );

    setVessels(transformedVessels);
  } catch (error) {
    console.error("Error fetching vessels:", error.message);
    toast.error("Failed to load vessels.");
    setVessels([]);
  }
};
