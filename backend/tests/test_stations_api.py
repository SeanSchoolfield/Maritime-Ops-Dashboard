import pytest
from types import SimpleNamespace

import backend.processors.coop.stations_api as stations_api

class DummyResp:
    def __init__(self, status_code, json_data=None):
        self.status_code = status_code
        self._json = json_data or {}
    def json(self):
        return self._json

def test_fetch_available_datums(monkeypatch):
    monkeypatch.setattr(stations_api, "ALL_PRODUCTS", ["p1","p2","p3","p4"])
    calls = []
    def fake_get(url):
        calls.append(url)
        if "product=p1" in url:
            return DummyResp(200, {"data":[{}]})
        if "product=p2" in url:
            return DummyResp(200, {"error":"gone"})
        if "product=p3" in url:
            return DummyResp(500, {})
        return DummyResp(200, {"foo":"bar"})

    avail = stations_api._fetch_available_datums("S1", http_get=fake_get)
    assert set(avail) == {"p1","p4"}
    assert any("product=p1" in u for u in calls)
    assert any("product=p4" in u for u in calls)

def test_run_success(monkeypatch):
    fake_station = {
        "id":"STX","name":"XY","state":"NY",
        "timezone":"EST","timezonecorr":"-5","lng":-74.0,"lat":40.7
    }
    def fake_http_get(url):
        if stations_api.COOP_STATIONS_URL in url:
            return DummyResp(200, {"stations":[fake_station]})
        return DummyResp(200, {})

    inserted = []
    class DummyDB:
        def __init__(self, table):
            self.table = table
        def add(self, entity):
            inserted.append(entity.copy())
        def commit(self): pass
        def rollback(self): pass
        def close(self): pass

    ins, fails = stations_api.run(
        DBOperatorClass=DummyDB,
        http_get=fake_http_get,
        sleep_fn=lambda _: None
    )

    assert len(ins) == 1
    assert fails == []

    ent = ins[0]
    assert ent["id"] == "STX"
    assert ent["region"] == "NY"
    assert ent["type"] == "NOAA-COOP"
    assert ent["timezone"] == "EST (GMT -5)"
    assert ent["datums"] == stations_api.ALL_PRODUCTS
    assert ent["geom"] == "Point(-74.0 40.7)"

def test_run_db_failure(monkeypatch):
    fake_station = {"id":"FAIL","name":"F","state":"TX",
                    "timezone":"CST","timezonecorr":"-6","lng":-96,"lat":32}
    def fake_http_get(url):
        if stations_api.COOP_STATIONS_URL in url:
            return DummyResp(200, {"stations":[fake_station]})
        return DummyResp(200, {})

    class BrokenDB:
        def __init__(self, table): pass
        def add(self, entity):
            raise RuntimeError("boom")
        def commit(self): pass
        def rollback(self): pass
        def close(self): pass

    ins, fails = stations_api.run(
        DBOperatorClass=BrokenDB,
        http_get=fake_http_get,
        sleep_fn=lambda _: None
    )

    assert ins == []
    assert len(fails) == 1
    assert fails[0]["id"] == "FAIL"
