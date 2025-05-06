import pytest
from types import SimpleNamespace
from datetime import datetime,timezone

import backend.processors.coop.oce_api as oce_module

class DummyResp:
    def __init__(self, status, json_data=None):
        self.status_code = status
        self._json = json_data or {}
    def json(self):
        return self._json

def test_request_success(monkeypatch):
    dummy = DummyResp(200, {"data":[{"v":42,"d":99,"s":7}]})
    monkeypatch.setattr(oce_module.requests, "get", lambda url: dummy)
    result = oce_module.request("123", "water_level")
    assert isinstance(result, dict)
    assert result["data"][0]["v"] == 42

def test_request_error(monkeypatch):
    dummy = DummyResp(500)
    monkeypatch.setattr(oce_module.requests, "get", lambda url: dummy)
    result = oce_module.request("123", "water_level")
    assert result is dummy

def test_run_one_station(monkeypatch):
    fake_station = {"id": "S1", "datums": ["water_temperature","salinity","water_level"]}
    added = []
    class DummyDB:
        def __init__(self, table):
            self.table = table
        def query(self, _):
            return [fake_station] if self.table == "sources" else []
        def add(self, entity):
            if self.table == "oceanography":
                added.append(entity.copy())
        def commit(self): pass
        def rollback(self): pass
        def close(self): pass
    monkeypatch.setattr(oce_module, "DBOperator", DummyDB, raising=False)

    def fake_get(url, *args, **kwargs):
        if "product=water_temperature" in url:
            return DummyResp(200, {"data":[{"v":10.1}]})
        if "product=salinity" in url:
            return DummyResp(200, {"data":[{"s":3.14}]})
        if "product=water_level" in url:
            return DummyResp(200, {"data":[{"v":2.5}]})
        return DummyResp(200, {"error":"no data"})
    monkeypatch.setattr(oce_module.requests, "get", fake_get)

    reports, fails = oce_module.run(DummyDB, sleep_fn=lambda s: None)

    assert fails == []
    assert len(reports) == 1
    rpt = reports[0]
    assert rpt["src_id"] == "S1"
    assert rpt["water_temperature"] == 10.1
    assert rpt["salinity"] == 3.14
    assert rpt["water_level"] == 2.5
    assert len(added) == 1
    assert added[0] == rpt
