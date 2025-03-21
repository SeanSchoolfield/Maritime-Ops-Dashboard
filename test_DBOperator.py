from DBOperator import DBOperator
import pytest
from psycopg2.errors import *
from pprint import pprint

"""
// TODO
- Items to test
    - DBOperator
        - feed it all sorts of data and reqeusts to push/pull

- Things to test for
    - Initializing DB connection and cursor
    - Can handle a pending request for up to a specified time
        - If timeout, then produce an output to console
        - throws error to be handled above
    - Can properly package PostGIS stuff for client to process
    - Can handle invalid key: values properly
    - Can properly add/remove/change entries inside DB
    - Can properly call PostGIS commands by providing valid entities, or interpretable errors
    - Only accepts valid DB Users
    - add()/modify() fails if INSERT permissions fail
    - delete() fails if DELETE permissions fail
"""
@pytest.mark.init
class TestInit:
    def test_valid_table(self):
        db = DBOperator(table="vessels")
        assert isinstance(db, DBOperator), "instance connects to existing DB 'vessels'"

    def test_no_arg(self):
        with pytest.raises(TypeError):
            db = DBOperator()

    def test_invalid_table(self):
        with pytest.raises(RuntimeError):
            db = DBOperator(table="some dumb table")

    # TODO: Figure out why specifying host:port is fucky
    # def test_valid_host(self): # My system hates specifying host:port for some reason
    #     db = DBOperator(table="vessels",host='localhost',port='5432')
    #     assert isinstance(db, DBOperator), "instance connects to existing DB 'vessels'"

    def test_invalid_host(self): # My system hates specifying host:port for some reason?
        with pytest.raises(OperationalError):
            db = DBOperator(table="vessels",host='localhost',port='5432')

    def test_valid_credentials(self):
        db = DBOperator(table="vessels",user='sdj81')
        assert isinstance(db, DBOperator), "instance connects to existing DB 'vessels'"

    def test_invalid_credentials(self):
        with pytest.raises(OperationalError):
            db = DBOperator(table="vessels",user='postgres')

@pytest.mark.hidden_methods
class TestHiddenMethods():
    def setup_method(self):
        self.db = DBOperator(table="vessels")

    def teardown_method(self):
        self.db.close()
        del self.db

    def test_uncallable__get_tables(self):
        with pytest.raises(AttributeError):
            self.db.__get_tables()

    def test_uncallable_get_tables_agian(self):
        with pytest.raises(AttributeError):
            self.db.get_tables()

@pytest.mark.queries
class TestQueries():
    def setup_method(self):
        self.db = DBOperator(table="vessels")
        self.present_entity = { 'mmsi': 368261120 }
        self.missing_entity = {'mmsi': 1} # Querying a valid attribute for an entity that doesn't exist
        self.filter_attr= {'type' : 'FISHING'} # querying multple values for one attribute
        self.varying_one_attr = [{'type' : 'RECREATIONAL'},{'type':'FISHING'}] # querying multple values for one attribute
        self.varying_many_attrs = [
        { "type": "FISHING",
         "current_status": "anchored"
         },
        { "type": "RECREATIONAL",
         "current_status": "anchored"
         },
    ]
        self.wrong_attr = {'status': 'anchored'} # attr doesn't exist
        self.result = None
        self.existing_entity = {
            'callsign': 'WDN2333',
            'cargo_weight': 65.0,
            'current_status': '0',
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 2.8,
            'flag': 'USA',
            'geom': 'Point(-91.0 30.15)',
            'heading': 356.3,
            'lat': 30.15,
            'length': 137.0,
            'lon': -91.0,
            'mmsi': 368261120,
            'speed': 7.6,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:01',
            'type': 'PASSENGER',
            'vessel_name': 'VIKING MISSISSIPPI',
            'width': 23.0
        }

    def teardown_method(self):
        self.db.close()
        del self.db
        del self.present_entity
        del self.missing_entity
        del self.filter_attr
        del self.varying_one_attr
        del self.varying_many_attrs
        del self.wrong_attr
        del self.result
        del self.existing_entity

    def test_query(self):
        self.result = self.db.query([self.present_entity])
        assert len(self.result) == 1, "Should only query 1 entity"
        assert isinstance(self.result, list), "Result returns an array"
        for i in self.result:
            assert isinstance(i, dict), "List contains dictionary items"
        assert self.result[0]['mmsi'] == self.existing_entity['mmsi'], "mmsi matches what I know exists in DB"

    def test_absolute_query(self):
        self.result = self.db.query([self.existing_entity])
        assert len(self.result) == 1, "Should only query 1 entity"
        assert isinstance(self.result, list), "Result returns an array"
        for i in self.result:
            assert isinstance(i, dict), "List contains dictionary items"
        assert self.result[0]['mmsi'] == self.existing_entity['mmsi'], "mmsi matches what I know exists in DB"

    def test_empty_value(self):
        self.result = self.db.query([self.missing_entity])
        assert len(self.result) == 0, "Should return an empty array"

    def test_one_filter(self):
        self.result = self.db.query([self.filter_attr])
        assert len(self.result) > 0, "Should return an array of entities, since these values are known to exist"
        assert isinstance(self.result, list), "Result returns an array"
        for i in self.result:
            assert isinstance(i, dict), "List contains dictionary items"

    def test_many_filters_one_attr(self):
        
        self.result = self.db.query(self.varying_one_attr)
        assert len(self.result) > 0, "Should return an array of entities, since these values are known to exist"

    def test_many_filters_many_attrs(self):
        self.result = self.db.query(self.varying_many_attrs)
        assert len(self.result) == 6, "Pretty sure the union of anchored fishing vessels and anchored rec vessels is yields 6"

    def test_wrong_attr(self):
        with pytest.raises(UndefinedColumn): # Might be worth catching and throwing agian?
            self.result = self.db.query([self.wrong_attr])

if __name__ == "__main__":
    entity = {
        'callsign': 'WDN2333',
        'cargo_weight': 65.0,
        'current_status': '0',
        'dist_from_port': 0.0,
        'dist_from_shore': 0.0,
        'draft': 2.8,
        'flag': 'USA',
        'geom': 'Point(-91.0 30.15)',
        'heading': 356.3,
        'lat': 30.15,
        'length': 137.0,
        'lon': -91.0,
        'mmsi': 368261120,
        'speed': 7.6,
        'src': 'MarineCadastre-AIS',
        'timestamp': '2024-09-30T00:00:01',
        'type': 'PASSENGER',
        'vessel_name': 'VIKING MISSISSIPPI',
        'width': 23.0
    }

    operator = DBOperator(table='vessels')
    # operator = DBOperator(table='vessels',host='localhost',port='5432')
    # input()

    ### Get filterable items
    # pprint(operator.fetch_filter_options())
    # input()

    ### Filters
    filters = [
        { "status": "FISHING",
         },
    ]
    # pprint(len(operator.query(filters)))
    # input()

    ### Add
    # operator.add(entity)
    # operator.commit()

    ### Query
    # pprint(operator.query({"mmsi":368261120})) # Table should have new entity
    # input()
    
    ### Modify
    # operator.modify(("mmsi",368261120),{'speed':0.0})
    # operator.commit()
    # print("Changed entry:")
    # pprint(operator.query(("mmsi",368261120)))
    # input()

    ### Delete
    # operator.delete(("mmsi",368261120))
    # operator.commit()
    # pprint(operator.query(("mmsi",368261120)))

