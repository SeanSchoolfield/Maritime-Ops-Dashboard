from backend import utils

def test_filter_parser_empty():
    filters = {}
    queries = []
    utils.filter_parser(filters, queries)
    assert queries == []
