from pprint import pprint
from DBOperator import DBOperator

sources = DBOperator(table='sources')

pprint(sources.permissions)
pprint(sources.attrs)
pprint(sources.get_table())

entity = {
    # id is autogenerated hash
    'name': "<API Resource name>",
    'type': "API",
    'datums': ["<API_url>"]
}
