import './style.css';
import Map from 'ol/Map.js';
import View from 'ol/View.js';
import Draw from 'ol/interaction/Draw.js';
import TileLayer from 'ol/layer/Tile.js';
import VectorLayer from 'ol/layer/Vector.js';
import OSM from 'ol/source/OSM';
import VectorSource from 'ol/source/Vector.js';
import DragBox from 'ol/interaction/DragBox.js';
import Select from 'ol/interaction/Select.js';
import { platformModifierKeyOnly } from 'ol/events/condition.js';

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

//DragBox implementation

const dragBox = new DragBox({
    condition: platformModifierKeyOnly, //CTRL key
});

let selectedFeatures = new Select();
map.addInteraction(selectedFeatures);

dragBox.on('boxend', function () {
    const extent = dragBox.getGeometry().getExtent();

    selectedFeatures.getFeatures().clear();

    source.forEachFeatureIntersectingExtent(extent, function (feature) {
        selectedFeatures.getFeatures().push(feature);
    });

    const numSelected = selectedFeatures.getFeatures().getLength();
    if (numSelected > 0) {
        alert(numSelected + ' feature(s) selected.');                               //swap out alert for something else that doesn't require confirmation
        deleteButton.disabled = false;
    } else {
        alert("No features selected.");                                             //swap out alert for something else that doesn't require confirmation
        deleteButton.disabled = true;
    }
});

document.getElementById('select-mode').addEventListener('click', function () {
    if (!map.getInteractions().getArray().includes(dragBox)) {
        map.addInteraction(dragBox);
        alert("Hold CTRL and drag to select features.");                            //swap out alert for something else that doesn't require confirmation
    }
});

const deleteButton = document.getElementById('delete-selected');
deleteButton.addEventListener('click', function () {
    selectedFeatures.getFeatures().forEach(function (feature) {
        source.removeFeature(feature);
    });
    selectedFeatures.getFeatures().clear();
    deleteButton.disabled = true;
    alert("Selected features deleted.");                                            // modify this to allow for a cancel
});
