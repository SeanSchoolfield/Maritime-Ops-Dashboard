import os
import sys
from unittest.mock import MagicMock
import pytest
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

import kafka
kafka.KafkaProducer = MagicMock()

import backend.processors.nws.met_api as met_module
from backend.processors.nws.met_api import nws_weather

@pytest.fixture(autouse=True)
def reset_producer():
    met_module.producer.send.reset_mock()
    yield

class DummyResp:
    def __init__(self, status, json_data=None, text=""):
        self.status_code = status
        self._json = json_data or {}
        self.text = text
    def json(self):
        return self._json

@pytest.fixture(autouse=True)
def patch_db(monkeypatch):
    fake_db = MagicMock()
    fake_db.contains.return_value = ["zone-A"]
    monkeypatch.setattr(met_module, "DBOperator", lambda **kw: fake_db)
    return fake_db

def test_nws_weather_success(monkeypatch):
    station = {
        "id": "ST123",
        "name": "Test Station",
        "geom": json.dumps({"coordinates": [100.0, 45.0]})
    }

    point_payload = {"properties": {"forecast": "http://fake/forecast"}}
    resp_point = DummyResp(200, point_payload)
    forecast_payload = {
        "geometry": {"type": "Point", "coordinates": [100.0, 45.0]},
        "properties": {
            "generatedAt": "2025-05-01T10:00:00+00:00",
            "periods": [{
                "temperature": 68,
                "windSpeed": "5 to 12 mph",
                "windDirection": "NE",
                "probabilityOfPrecipitation": {"value": 40}
            }]
        }
    }
    resp_forecast = DummyResp(200, forecast_payload)

    calls = []
    def fake_get(url, *args, **kwargs):
        calls.append(url)
        return resp_point if "points/" in url else resp_forecast

    monkeypatch.setattr(met_module.requests, "get", fake_get)

    out = nws_weather(station)

    assert any("points/45.0,100.0" in u for u in calls)
    assert any("fake/forecast" in u for u in calls)

    assert out["src_id"] == "ST123"
    assert out["air_temperature"] == 68
    assert out["wind_heading"] == 45.0
    assert out["wind_speed"] == pytest.approx(12.0)
    assert out["precipitation"] == pytest.approx(0.4)

    met_module.producer.send.assert_called_once_with("NWS", key="ST123", value=out)

def test_nws_weather_point_error(monkeypatch):
    station = {
        "id": "ERR1",
        "name": "Error Station",
        "geom": json.dumps({"coordinates": [0.0, 0.0]})
    }
    monkeypatch.setattr(
        met_module.requests, "get",
        lambda url, *a, **k: DummyResp(500, None, "fail")
    )

    result = nws_weather(station)
    assert result is None

    met_module.producer.send.assert_not_called()
