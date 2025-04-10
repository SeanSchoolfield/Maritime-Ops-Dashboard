import axios from "axios";
import { convertCartesianToDegrees } from "./coordUtils";
import { toast } from "react-toastify";

const URL = window.location.href.split(":");

export const zoning = async (polygonData, filters = {}, setVessels) => {
    const payload = {};

    // If zone is selected, apply geospatial filtering
    console.log("ZONE SELECTED:");
    // console.log(polygonData);

    let polygonVerticies = polygonData?.positions.map((point) =>
        convertCartesianToDegrees(point) // This is sick tho
    );

    let geom = { 'type' : "Polygon",
        "coordinates": [polygonVerticies?.map((point) => [point.longitude, point.latitude])],
    }

    console.log("Zone GeoJSON:");
    console.log(geom);
    payload.geom = geom;

    // Apply filters to query
    if (filters.types && filters.types.length > 0) {
        payload.type = filters.types.join(",");
    }
    if (filters.origin) {
        payload.origin = filters.origin;
    }
    if (filters.statuses && filters.statuses.length > 0) {
        payload.status = filters.statuses.join(",");
    }

    try {
        const zoneAPI = "http:" + URL[1] + ":8000/zoning/";
        const response = await axios.post(zoneAPI, payload);

        console.log("Zoning response:");
        console.log(response);
        console.log("Table privileges");
        console.log(response.data.privileges);
        console.log("Response Timestamp");
        console.log(response.data.retrieved);

        console.log("Size of payload");
        console.log(response.data.size);
        console.log("Payload:");
        console.log(response.data.payload);
        if (response.data.length === 0) {
            toast.info("No vessels found matching your filters.");
            setVessels([]);
            return;
        }

        const transformedVessels = response.data.payload.vessels?.map((vessel) =>
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
