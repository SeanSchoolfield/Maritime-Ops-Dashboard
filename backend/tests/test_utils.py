from backend import utils

def test_filter_parser_empty():
    filters = {}
    queries = []
    utils.filter_parser(filters, queries)
    assert queries == []

def test_filter_parser_single_category():
    filters = {"ship_types": ["CARGO", "TANKER"]}
    queries = []
    utils.filter_parser(filters, queries)
    assert queries == ["type IN ('CARGO','TANKER')"]

def test_filter_parser_multiple_categories():
    filters = {
        "ship_types": ["CARGO"],
        "flags": ["USA", "CHN"]
    }
    queries = []
    utils.filter_parser(filters, queries)
    assert "type IN ('CARGO')" in queries
    assert "flag IN ('USA','CHN')" in queries
    assert len(queries) == 2

def test_filter_parser_ignores_unknown_keys():
    filters = {"unknown_filter": ["foo", "bar"]}
    queries = []
    utils.filter_parser(filters, queries)
    assert queries == []


def test_filter_parser_with_none_or_nonlist():
    filters = {"ship_types": None, "flags": "USA"}
    queries = []
    utils.filter_parser(filters, queries)
    assert queries == ["flag IN ('USA')"]
