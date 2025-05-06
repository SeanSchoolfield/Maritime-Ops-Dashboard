import os
import sys
import importlib
import pytest

MODULE = 'backend.processors.nws.offices_api'

def reload_offices_api():
    if MODULE in sys.modules:
        del sys.modules[MODULE]
    return importlib.import_module(MODULE)

def test_exits_when_no_token(monkeypatch):
    monkeypatch.delenv('TOKEN', raising=False)
    with pytest.raises(SystemExit) as exc:
        __import__(MODULE, fromlist=['*'])
    assert "No API Token provided." in str(exc.value)

def test_all_requests_fail_yields_empty_stations(monkeypatch):
    monkeypatch.setenv('TOKEN', 'dummy-token')

    class DummyResp:
        def __init__(self):
            self.status_code = 500
            self.text = "server error"
        def json(self):
            return {}
    import requests
    monkeypatch.setattr(requests, 'get', lambda *args, **kwargs: DummyResp())

    import builtins
    monkeypatch.setattr(builtins, 'input', lambda *args, **kwargs: "")

    import backend.DBOperator as dbo
    class DummyDB:
        def __init__(self, *args, **kwargs): pass
        def add(self, *args, **kwargs): pass
        def commit(self, *args, **kwargs): pass
        def close(self, *args, **kwargs): pass
    monkeypatch.setattr(dbo, 'DBOperator', DummyDB)

    mod = reload_offices_api()

    assert hasattr(mod, 'stations')
    assert mod.stations == [], "All HTTP calls failed, so no stations should have been collected"
