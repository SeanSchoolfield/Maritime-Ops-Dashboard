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

document.addEventListener("DOMContentLoaded", function () {
    console.log("DOM fully loaded");
    const raster = new TileLayer({
        source: new OSM(),
    });

    const source = new VectorSource({ wrapX: false });
    const vector = new VectorLayer({
        source: source,
    });

    const typeSelect = document.getElementById('zone-sidebar');

    const map = new Map({
        layers: [raster, vector],
        target: 'map',
        view: new View({
            center: [-11000000, 4600000],
            zoom: 4,
        }),
    });

    let draw;
    function addInteraction() {
        const selectedRadio = document.querySelector('input[name="geometry"]:checked');
        const value = selectedRadio ? selectedRadio.value : null;
        if (draw) {
            map.removeInteraction(draw);
        }
        if (value && value !== "None") {
            draw = new Draw({
                source: source,
                type: value,
            });
            map.addInteraction(draw);
        }
    }

    document.querySelectorAll('input[name="geometry"]').forEach(radio => {
        radio.addEventListener("change", function () {
            addInteraction();
        });
    });

    document.getElementById('undo').addEventListener('click', function () {
        if (draw) {
            draw.removeLastPoint();
        }
    });

    //DragBox implementation

    const dragBox = new DragBox({
        condition: platformModifierKeyOnly, //CTRL key
    });

    let selectedFeatures = new Select();
    map.addInteraction(selectedFeatures);

    function showMessage(message) {
        let msgBox = document.getElementById('message-box');
        if (!msgBox) {
            msgBox = document.createElement('div');
            msgBox.id = 'message-box';
            msgBox.style.position = 'fixed';
            msgBox.style.bottom = '20px';
            msgBox.style.left = '50%';
            msgBox.style.transform = 'translateX(-50%)';
            msgBox.style.padding = '10px 20px';
            msgBox.style.backgroundColor = 'rgba(0,0,0,0.7)';
            msgBox.style.color = '#fff';
            msgBox.style.borderRadius = '5px';
            document.body.appendChild(msgBox);
        }
        msgBox.innerText = message;
        msgBox.style.display = 'block';
        setTimeout(() => {
            msgBox.style.display = 'none';
        }, 3000);
    }

    dragBox.on('boxend', function () {
        const extent = dragBox.getGeometry().getExtent();

        selectedFeatures.getFeatures().clear();

        source.forEachFeatureIntersectingExtent(extent, function (feature) {
            selectedFeatures.getFeatures().push(feature);
        });

        const numSelected = selectedFeatures.getFeatures().getLength();
        if (numSelected > 0) {
            showMessage(numSelected + ' feature(s) selected.');
            deleteButton.disabled = false;
        } else {
            showMessage("No features selected.");
            deleteButton.disabled = true;
        }
    });

    const selectModeButton = document.getElementById('select-mode');

    selectModeButton.addEventListener('click', function () {
        if (!map.getInteractions().getArray().includes(dragBox)) {
            map.addInteraction(dragBox);
            showMessage("Hold CTRL and drag to select features.");
            //this.disabled = true;
            console.log("Selection mode activated.")
        }
    });
    const cancelModeButton = document.getElementById('cancel-selection');
    if (cancelModeButton) {
        cancelModeButton.addEventListener('click', function () {
            if (map.getInteractions().getArray().includes(dragBox)) {
                map.removeInteraction(dragBox);
                showMessage("Selection mode canceled.")
                console.log("Selection mode deactivated");
            }
        });
    }

    const deleteButton = document.getElementById('delete-selected');
    deleteButton.addEventListener('click', function () {
        if (confirm("Are you sure you want to delete the selected features?")) {
            console.log("Delete button activated.")
            selectedFeatures.getFeatures().forEach(function (feature) {
                source.removeFeature(feature);
            });
            selectedFeatures.getFeatures().clear();
            deleteButton.disabled = true;
            showMessage("Selected features deleted.");
            console.log("Features deleted.")

        } else {
            showMessage("Deletion canceled.");
            console.log("Deletion canceled.")
        }
    });


    const sidenav = document.getElementById("sidenav");
    const filterButton = document.getElementById("filter-button");
    const closeButton = document.getElementById("close-sidenav");

    filterButton.addEventListener("click", function () {
        sidenav.classList.add("active");
    });

    closeButton.addEventListener("click", function () {
        sidenav.classList.remove("active");
    });

    document.addEventListener("click", function (event) {
        setTimeout(() => {
            if (!sidenav.contains(event.target) && event.target !== filterButton) {
                sidenav.classList.remove("active");
            }
        }, 200);
    });

    const zoneSidebar = document.getElementById("zone-sidebar");
    const zoneButton = document.getElementById("zone-button");
    const closeZoneButton = document.getElementById("close-zone-sidebar");

    zoneButton.addEventListener("click", function () {
        zoneSidebar.classList.toggle("active");
    });
    if (closeZoneButton) {
        closeZoneButton.addEventListener("click", function () {
            zoneSidebar.classList.remove("active");
        });
    }
});
