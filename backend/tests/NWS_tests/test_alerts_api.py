import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))

from unittest.mock import MagicMock
import pytest
import datetime
import pytz

import kafka
kafka.KafkaProducer = MagicMock()

from backend.processors.nws.alerts_api import nws_alerts, utc, now as module_now

@pytest.fixture(autouse=True)
def freeze_time(monkeypatch):
    fixed = datetime.datetime(2025, 5, 1, 12, 0, 0)
    monkeypatch.setattr('backend.processors.nws.alerts_api.now', fixed)
    monkeypatch.setattr('backend.processors.nws.alerts_api.utc', pytz.UTC)

class DummyResp:
    def __init__(self, status, json_data=None, text=""):
        self.status_code = status
        self._json = json_data
        self.text = text
    def json(self):
        return self._json

def test_http_error(monkeypatch):
    monkeypatch.setattr(
        'backend.processors.nws.alerts_api.requests.get',
        lambda url: DummyResp(500, None, "server error")
    )
    assert nws_alerts({'id': 'ZONE1'}) is None

def test_empty_features(monkeypatch):
    monkeypatch.setattr(
        'backend.processors.nws.alerts_api.requests.get',
        lambda url: DummyResp(200, {"features": []})
    )
    assert nws_alerts({'id': 'ZONE2'}) is None

def test_valid_alert(monkeypatch):
    props = {
        "sent":        "2025-05-01T11:30:00+00:00",
        "effective":   "2025-05-01T11:00:00+00:00",
        "ends":        "2025-05-01T13:00:00+00:00",
        "expires":     "2025-05-01T13:00:00+00:00",
        "category":    "met",
        "messageType": "alert",
        "description": "Test description",
        "instruction": "Take cover",
        "urgency":     "immediate",
        "severity":    "severe",
        "headline":    "Test Headline"
    }
    dummy = DummyResp(200, {"features": [{"properties": props}]})
    monkeypatch.setattr(
        'backend.processors.nws.alerts_api.requests.get',
        lambda url: dummy
    )

    out = nws_alerts({'id': 'Z3'})
    assert isinstance(out, dict)
    assert out["timestamp"]  == props["sent"]
    assert out["effective"]  == props["effective"]
    assert out["end_time"]   == props["ends"]
    assert out["active"]     is True
    assert out["type"]       == "MET-ALERT"
    assert out["description"]== props["description"]
    assert out["instructions"]== props["instruction"]
    assert out["urgency"]    == props["urgency"]
    assert out["severity"]   == props["severity"]
    assert out["headline"]   == props["headline"]
