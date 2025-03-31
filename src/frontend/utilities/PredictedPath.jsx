import { Entity } from "resium";
import { Cartesian3, Color, HeightReference } from "cesium";

export function placeDot(longitude, latitude, hoursAhead) {
    // Convert values to numbers and validate
    const numLongitude = Number(longitude);
    const numLatitude = Number(latitude);

    if (isNaN(numLongitude) || isNaN(numLatitude)) {
        console.warn(`Invalid coordinates for prediction at T+${hoursAhead}h`, {
            longitude, latitude
        });
        return null;
    }

    const position = Cartesian3.fromDegrees(numLongitude, numLatitude);

    return (
        <Entity
            key={`dot-${hoursAhead}-${longitude}-${latitude}`}
            position={position}
            point={{
                pixelSize: 10,
                color: Color.RED,
                outlineColor: Color.BLACK,
                outlineWidth: 2,
                heightReference: HeightReference.CLAMP_TO_GROUND,
            }}
            label={{
                text: `T+${hoursAhead}h`,
                font: "14pt sans-serif",
                fillColor: Color.YELLOW,
                outlineColor: Color.BLACK,
                outlineWidth: 2,
                pixelOffset: Cartesian3.ZERO,
            }}
        />
    );
}

const PredictedPath = ({ predictions }) => {
    return (
        <>
{Array.isArray(predictions) && predictions.length > 0 &&
    predictions.map((point) =>
        placeDot(
            point['Predicted LON'],
            point['Predicted LAT'],
            point['Hours Ahead']
        ) || <div key={point['Hours Ahead']}>Invalid Prediction Data</div>
    )
}
        </>
    );
};

export default PredictedPath;
