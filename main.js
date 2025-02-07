import './style.css';
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import Draw from 'ol/interaction/Draw.js';
import TileLayer from 'ol/layer/Tile.js';
import VectorLayer from 'ol/layer/Vector.js';
import OSM from 'ol/source/OSM';
import VectorSource from 'ol/source/Vector.js';

const raster = new TileLayer({
    source: new OSM(),
});

const source = new VectorSource({ wrapX: false });
const vector = new VectorLayer({
    source: source,
});

const map = new Map({
    layers: [raster, vector],
    target: 'map',
    view: new View({
        center: [-11000000, 4600000],
        zoom: 4,
    }),
});

const typeSelect = document.getElementById('type');

let draw;
function addInteraction() {
    const val = typeSelect.value;
    if (val !== 'None') {
        draw = new Draw({
            source: source,
            type: typeSelect.value,
        });
        map.addInteraction(draw);
    }
}

typeSelect.onchange = function () {
    map.removeInteraction(draw);
    addInteraction();
};

document.getElementById('undo').addEventListener('click', function () { draw.removeLastPoint(); });

addInteraction();
