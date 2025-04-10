import React from 'react'
import { Entity } from 'resium'
import { Cartesian3, DistanceDisplayCondition, NearFarScalar, HeightReference } from 'cesium'
import ReactDOMServer from 'react-dom/server'
import BoatIcon from "../../assets/icons/boatIcon";

export function placeVessel(longitude, latitude, heading, elevation = 0, type = "OTHER", name = "UNKOWN") {
    // Convert values to numbers and validate
    const numLongitude = Number(longitude);
    const numLatitude = Number(latitude);
    const numElevation = Number(elevation);

    if (isNaN(numLongitude) || isNaN(numLatitude)) {
        console.warn(`Invalid coordinates for vessel "${name}":`, {
            longitude, latitude, elevation
        });
        return null;
    }

    const position = Cartesian3.fromDegrees(numLongitude, numLatitude, numElevation);

    const svgString = ReactDOMServer.renderToStaticMarkup(
        <BoatIcon type={type} size={25} heading={heading} />
    );

    const encodedSvg = encodeURIComponent(svgString);
    const dataUrl = `data:image/svg+xml;charset=utf-8,${encodedSvg}`;

    return (
        <Entity
            key={`${name}-${longitude}-${latitude}`}
            position={position}
            billboard={{
                image: dataUrl,
                scale: 2.0,
                distanceDisplayCondition: new DistanceDisplayCondition(0, 20.0e6),
                scaleByDistance: new NearFarScalar(1.5e5, 1.5, 1.5e6, 0.5),
                heightReference: HeightReference.None,
                verticalOrigin: 1,
                horizontalOrigin: 0,
                eyeOffset: new Cartesian3(0, 0, -500),
                pixelOffset: new Cartesian3(0, 0, 0),
            }}
            name={`${type.charAt(0).toUpperCase() + type.slice(1)} Vessel: ${name}`}
            description={`This is a ${type} vessel named "${name}".`}
        />
    );
}
