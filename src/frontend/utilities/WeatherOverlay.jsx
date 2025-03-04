import { ImageryLayer, WebMapServiceImageryProvider } from "cesium";
import { useCesium } from "resium";
import { useEffect, useState } from "react";


/* 
    Explore weather APIs,
    and figure out how to add weather data to the globe
    Ideally it would be in Cesium Geometries, with color for severity of weather
    red for severe, yellow for moderate, green for mild
    and the weather data would be updated in real time. 
    The specific information about a storm or weather event would be displayed in a popup
    when the user clicks on the weather data. 
    It would provide wind speed, direction, and other relevant information.
    Ocean conditions should also be included, such as wave height and direction.

*/
const WeatherOverlay = ({ showWeather }) => {
    // const { viewer } = useCesium;
    // const [weatherLayer, setWeatherLayer] = useState(null);

    useEffect(() => {
        // if (viewer && showWeather) {

        //     const layer = viewer.imageryLayers.addImageryProvider(
        //         new WebMapServiceImageryProvider({
        //             // Figure out the API URL, and if needed, where the Key goes
        //             url: "",
        //             layers: "1",
        //             parameters: {
        //                 transparent: true,
        //                 format: "image/png",
        //             },
        //         })
        //     );
        //     console.log("Weather layer added");
        //     setWeatherLayer(layer);

        //     return () => {
        //         if (layer) {
        //             viewer.imageryLayers.remove(layer);
        //             console.log("Weather layer removed");
        //         }
        //     };
        // }
    }, []);

    return null;
};

export default WeatherOverlay