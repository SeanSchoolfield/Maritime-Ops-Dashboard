# backend/tests/coop/test_met_api.py
import sys
import importlib
import pytest
from types import SimpleNamespace
from datetime import datetime, timedelta

MODULE = "backend.processors.coop.met_api"

class DummyResp:
    def __init__(self, status, json_data=None, text=""):
        self.status_code = status
        self._json = json_data or {}
        self.text = text

    def json(self):
        return self._json

@pytest.fixture(autouse=True)
def freeze_time(monkeypatch):
    fixed = datetime(2025, 5, 1, 12, 0, 0)
    monkeypatch.setattr("backend.processors.coop.met_api.datetime", datetime)
    return fixed

def reload_module():
    if MODULE in sys.modules:
        del sys.modules[MODULE]
    return importlib.import_module(MODULE)

def test_request_success(monkeypatch):
    from backend.processors.coop.met_api import request

    monkeypatch.setattr("requests.get", lambda url: DummyResp(200, {"foo": "bar"}))
    result = request("ST1", "air_temperature")
    assert isinstance(result, dict)
    assert result["foo"] == "bar"

def test_request_error(monkeypatch):
    from backend.processors.coop.met_api import request

    bad = DummyResp(500, None, "oops")
    monkeypatch.setattr("requests.get", lambda url: bad)
    result = request("ST1", "wind")
    assert result is bad

def test_full_run_one_station(monkeypatch):
    fake_station = {
        "id": "ST1",
        "name": "Station One",
        "datums": ["air_temperature", "wind", "visibility", "humidity"]
    }
    class DummyDB:
        def __init__(self, table):
            self.table = table
            self.added = []
        def query(self, criteria):
            return [fake_station] if self.table == "sources" else []
        def add(self, entity):
            self.added.append((self.table, entity.copy()))
        def commit(self): pass
        def rollback(self): pass
        def close(self): pass

    monkeypatch.setattr(
        "backend.processors.coop.met_api.DBOperator",
        lambda table: DummyDB(table)
    )

    monkeypatch.setattr("backend.processors.coop.met_api.sleep", lambda _=0: None)

    def fake_get(url, *args, **kwargs):
        if "datagetter" in url:
            return DummyResp(200, {"data":[{"v":21,"d":90,"s":7}]})
        elif url.endswith("/notices.json"):
            return DummyResp(200, {"notices":[{"text":"Test notice","name":"Notice Headline"}]})
        else:
            pytest.fail(f"Unexpected URL {url}")
    import backend.processors.coop.met_api as met_mod
    monkeypatch.setattr(met_mod, "requests", SimpleNamespace(get=fake_get))

    met_mod.main()

    sources_db = met_mod.DBOperator("sources")
    met_db     = met_mod.DBOperator("meteorology")
    evt_db     = met_mod.DBOperator("events")

    added_records = []
    def capture_db(table):
        db = DummyDB(table)
        added_records.append(db)
        return db

    monkeypatch.setattr(
        "backend.processors.coop.met_api.DBOperator",
        capture_db
    )

    met_mod.main()

    met_instance = next(db for db in added_records if db.table=="meteorology")
    evt_instance = next(db for db in added_records if db.table=="events")

    assert len(met_instance.added) == 1
    assert met_instance.added[0][1]["src_id"] == "ST1"
    assert met_instance.added[0][1]["air_temperature"] == 21

    assert len(evt_instance.added) == 1
    assert evt_instance.added[0][1]["description"] == "Test notice"
