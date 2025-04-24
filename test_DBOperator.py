from DBOperator import DBOperator
import pytest
from psycopg2.errors import *
from pprint import pprint

"""
// TODO

# Fixing ships that don't appear properly filtered when custom zoning is applied
- Test geom-based functions
    - Calling them on a table that doesn't have type 'geom' throws error
    - They get expected zones

# Fix ships flashing on app
    - Integrate Filter options into within()

# Implement modify() with API scripts

# Implement archive
- when VesselOp.modify() is called, call ArchiveOp.add()

# Functional QoS shit
- Can handle a pending request for up to a specified time
    - If timeout, then produce an output to console
    - throws error to be handled above

- functions are ubiquitous based on table
    - Can handle invalid key: values properly
    - add() appears to work for all tables rn
        - No restriction on required attrs. Should probably implement that
    - delete() modify() fetch_filter_options()

# If we get around to impelemnting Users
- Only accepts valid DB Users
- add()/modify() fails if INSERT/UPDATE permissions fail
- query() fails if SELECT permissions fail
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

    # specifying host:port is fucky for Me on Linux
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

    def test_uncallable__get_privileges(self):
        with pytest.raises(AttributeError):
            self.db.__get_privileges()

    def test_uncallable_get_privileges_agian(self):
        with pytest.raises(AttributeError):
            self.db.get_privileges()

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
         "current_status": "ANCHORED"
         },
        { "type": "RECREATIONAL",
         "current_status": "ANCHORED"
         },
    ]
        self.wrong_attr = {'status': 'anchored'} # attr doesn't exist
        self.wrong_attr_type = {'status': 15} # Type is not a string
        self.result = None
        self.existing_entity = {
            'callsign': 'WDN2333',
            'cargo_weight': 65,
            'cog': None,
            'current_status': 'UNDERWAY',
            'dist_from_port': 0,
            'dist_from_shore': 0,
            'draft': 2.8,
            'flag': 'USA',
            'geom': '{"type":"Point","coordinates":[-91,30.15]}',
            'heading': 356.3,
            'lat': 30.15,
            'length': 137,
            'lon': -91,
            'mmsi': 368261120,
            'predicted_path': None,
            'speed': 7.6,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:01',
            'type': 'PASSENGER',
            'vessel_name': 'VIKING MISSISSIPPI',
            'width': 23
        }

        self.ZoneOp = DBOperator(table='zones')
        self.EventsOp = DBOperator(table='events')
        self.WeatherOp = DBOperator(table='meteorology')
        self.OceanOp = DBOperator(table='oceanography')
        self.StationsOp = DBOperator(table='sources')
        self.VesselOp = DBOperator(table='vessels')
        self.ArchiveOp = DBOperator(table='vessel_archive')

        self.existing_zone = {
            'geom': '{"type":"polygon","coordinates":[[[-93.4067001,43.8486137],[-93.4045944,43.848114],[-93.0588989,43.8484115],[-93.049797,43.848011],[-93.0494003,43.7609138],[-93.0494995,43.7501106],[-93.04 92935,43.7312126],[-93.0494995,43.6012115],[-93.0492935,43.5794105],[-93.0494995,43.5554122],[-93.0 492935,43.5333137],[-93.0490951,43.5287132],[-93.0492935,43.4997138],[-93.0592956,43.4995117],[-93.2473983,43.4995117],[-93.2672958,43.4993133],[-93.3586959,43.4995117],[-93.4824981,43.4995117],[-93.4925003,43.4994125],[-93.4976959,43.4991111],[-93.5011978,43.4995117],[-93.6368942,43.4995117],[-93.6485977,43.499813],[-93.6483993,43.5542106],[-93.6483993,43.6301116],[-93.6485977,43.6445121],[-93.6483993,43.6736106],[-93.6485977,43.6883125],[-93.6485977,43.7316131],[-93.6483001,43.7752113],[-93.6483993,43.8265113],[-93.6481933,43.8406105],[-93.648796,43.848011],[-93.6245956,43.8482131],[-93.5873947,43.848011],[-93.4678955,43.848114],[-93.4269943,43.848011],[-93.4089965,43.848114],[-93.4067001,43.8486137]]]}',
            'id': 'mnz093',
            'name': 'freeborn',
            'region': 'usa-mn',
            'src_id': 'mpx',
            'type': 'fire'
        }
        self.existing_event = {
            'active': True,
            'description': 'this station is currently in <a '
                "href='http://tidesandcurrents.noaa.gov/waterconditions.html#high'>high "
                'water condition</a>.',
            'effective': '2025-04-15t18:54:00',
            'end_time': '2025-04-15t19:54:00',
            'expires': '2025-04-15t19:54:00',
            'headline': 'high water condition',
            'id': 1,
            'instructions': 'none',
            'severity': 'low',
            'src_id': '1820000',
            'timestamp': '2025-04-15t18:54:00',
            'type': 'marine alert',
            'urgency': 'low'
        }
        self.existing_weather = {
            'air_temperature': 76.3,
            'event_id': None,
            'forecast': None,
            'humidity': None,
            'id': 1,
            'precipitation': None,
            'src_id': '1611400',
            'timestamp': '2025-04-15t17:54:21',
            'visibility': None,
            'wind_heading': 82,
            'wind_speed': 10.69
        }
        self.existing_ocean = {
            'conductivity': None,
            'event_id': None,
            'id': 1,
            'salinity': None,
            'src_id': '1611400',
            'timestamp': '2025-04-15t18:57:45',
            'water_level': 3.76,
            'water_physics': None,
            'water_temperature': 81.1,
            'wave_height': None
        }
        self.existing_station = {
            'datums': ['air_temperature',
                       'wind',
                       'water_temperature',
                       'air_pressure',
                       'water_level',
                       'one_minute_water_level',
                       'predictions'],
            'geom': '{"type":"point","coordinates":[-159.3561,21.9544]}',
            'id': '1611400',
            'name': 'nawiliwili',
            'region': 'usa',
            'timezone': 'hast (gmt -10)',
            'type': 'noaa-coop'
        }

    def teardown_method(self):
        self.db.close()
        self.ZoneOp.close()
        self.EventsOp.close()
        self.WeatherOp.close()
        self.OceanOp.close()
        self.StationsOp.close()
        self.VesselOp.close()
        self.ArchiveOp.close()

        del self.ZoneOp
        del self.EventsOp
        del self.WeatherOp
        del self.OceanOp
        del self.StationsOp
        del self.ArchiveOp
        del self.db
        del self.present_entity
        del self.missing_entity
        del self.filter_attr
        del self.varying_one_attr
        del self.varying_many_attrs
        del self.wrong_attr
        del self.result
        del self.existing_entity
        del self.existing_zone
        del self.existing_event
        del self.existing_weather
        del self.existing_ocean
        del self.existing_station

    def test_query(self):
        self.result = self.db.query([self.present_entity])
        assert len(self.result) == 1, "Should only query 1 entity"
        assert isinstance(self.result, list), "Result returns an array"
        for i in self.result:
            assert isinstance(i, dict), "List contains dictionary items"
        assert self.result[0]['mmsi'] == self.existing_entity['mmsi'], "mmsi matches what I know exists in DB"

    def test_query_empty_arr(self): # Thinking this will throw an error when empty arr is provided
        with pytest.raises(AttributeError):
            self.result = self.db.query([])

    def test_query_empty_dict(self): # Thinking this will throw an error when empty dict in arr is provided
        with pytest.raises(AttributeError):
            self.result = self.db.query([{}])

    # FIXME: Cannot handle GeoJSON
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

    def test_wrong_attr_type(self):
        with pytest.raises(UndefinedColumn): # Might be worth catching and throwing agian?
            self.result = self.db.query([self.wrong_attr_type])

    # TODO
    # FIXME: Cannot handle GeoJSON
    def test_query_different_tables(self):
        '''
        Make sure that queries can be singular/multi
        keys are valid and the correspnding datatype is also valid
        '''
        result = self.ZoneOp.query([self.existing_zone])
        assert len(result) == 1
        result = self.EventsOp.query([self.existing_event])
        assert len(result) == 1
        result = self.WeatherOp.query([self.existing_weather])
        assert len(result) == 1
        result = self.OceanOp.query([self.existing_ocean])
        assert len(result) == 1
        result = self.StationsOp.query([self.existing_station])
        assert len(result) == 1

@pytest.mark.delete
class TestDeletions():
    def setup_method(self):
        self.db = DBOperator(table="vessels")
        self.result = None
        self.empty = {}
        self.ship = { 'mmsi': 368261120 }
        self.entity_many_attrs = {
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
        self.entity_invalid_type = { 'mmsi': '368261120' }
        self.entity_invalid_attr = { 'id': '368261120' }

        self.ZoneOp = DBOperator(table='zones')
        self.EventsOp = DBOperator(table='events')
        self.WeatherOp = DBOperator(table='meteorology')
        self.OceanOp = DBOperator(table='oceanography')
        self.StationsOp = DBOperator(table='sources')
        self.VesselOp = DBOperator(table='vessels')
        self.ArchiveOp = DBOperator(table='vessel_archive')

    def teardown_method(self):
        if len(self.db.query([self.ship])) == 0:
            ship = {
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
            self.db.add(ship)
            self.db.commit()
        self.db.close()
        self.ZoneOp.close()
        self.EventsOp.close()
        self.WeatherOp.close()
        self.OceanOp.close()
        self.StationsOp.close()
        self.VesselOp.close()
        self.ArchiveOp.close()
        del self.ZoneOp
        del self.EventsOp
        del self.WeatherOp
        del self.OceanOp
        del self.StationsOp
        del self.VesselOp
        del self.ArchiveOp
        del self.result
        del self.empty
        del self.ship
        del self.entity_many_attrs
        del self.entity_invalid_type
        del self.entity_invalid_attr

    def test_delete_nothing(self):
        with pytest.raises(AttributeError):
            self.db.delete(self.empty)

    def test_delete(self):
        self.db.delete(self.ship)
        self.db.commit()
        self.result = self.db.query([self.ship])
        assert len(self.result) == 0, "Query off mmsi shouldn't pull anything"

    def test_delete_many_attrs(self):
        self.db.delete(self.entity_many_attrs)
        self.db.commit()
        self.result = self.db.query([self.entity_many_attrs])
        assert len(self.result) == 0, "Query off mmsi shouldn't pull anything"

    # TODO: Want this to throw an error
    def test_invalid_type(self):
        self.db.delete(self.entity_invalid_type)
        self.result = self.db.query([self.entity_invalid_type])
        assert len(self.result) == 0, "Query off mmsi shouldn't pull anything"

    def test_invalid_attr(self):
        with pytest.raises(UndefinedColumn):
            self.db.delete(self.entity_invalid_attr)

    # TODO
    def test_del_all_tables(self):
        # events valid entity
        # events invalid entity
        # weather valid entity
        # weather invalid entity
        # ocean valid entity
        # ocean invalid entity
        # sources valid entity
        # sources invalid entity
        # vessel_archive valid entity
        # vessel_archive invalid entity
        # zones valid entity
        # zones invalid entity
        pass

@pytest.mark.add
class TestAdditions():
    def setup_method(self):
        self.db = DBOperator(table="vessels")
        self.result = None
        self.empty_entity = {}
        self.existing_ship = {
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

        self.new_ship = {}

        self.ship_with_invalid_types = {
            'mmsi': '367702270',
            'vessel_name': 'MS. JENIFER TRETTER',
            'callsign': 'WDI4813',
            'timestamp': '2024-09-30T00:00:00',
            'heading': '334.5',
            'speed': 6.6,
            'current_status' : 12,
            'src': 'MarineCadastre-AIS',
            'type': 'TUG',
            'type': 'USA',
            'length': 113.0,
            'width': 34.0,
            'draft': 3.1,
            'cargo_weight': 56.0,
            'lat': 26.1,
            'lon': -97.21,
            'dist_from_shore': 0.0,
            'dist_from_port': 0.0,
            'geom': 'Point(-97.21 26.1)'
        }

        self.ship_missing_geom = {
            'mmsi': 367702270,
            'vessel_name': 'MS. JENIFER TRETTER',
            'callsign': 'WDI4813',
            'timestamp': '2024-09-30T00:00:00',
            'heading': 334.5,
            'speed': 6.6,
            'current_status' : 12,
            'src': 'MarineCadastre-AIS',
            'type': 'TUG',
            'type': 'USA',
            'length': 113.0,
            'width': 34.0,
            'draft': 3.1,
            'cargo_weight': 56.0,
            'lat': 26.1,
            'lon': -97.21,
            'dist_from_shore': 0.0,
            'dist_from_port': 0.0,
        }

        self.ship_missing_attrs = {
            'mmsi': 367702270,
            'vessel_name': 'MS. JENIFER TRETTER',
            'callsign': 'WDI4813',
            'timestamp': '2024-09-30T00:00:00',
            'speed': 6.6,
            'current_status' : 12,
            'type': 'USA',
            'length': 113.0,
            'draft': 3.1,
            'lat': 26.1,
            'dist_from_shore': 0.0,
            'dist_from_port': 0.0
        }

        self.ship_missing_mmsi = {
            'vessel_name': 'MS. JENIFER TRETTER',
            'callsign': 'WDI4813',
            'timestamp': '2024-09-30T00:00:00',
            'heading': 334.5,
            'speed': 6.6,
            'current_status': 12,
            'src': 'MarineCadastre-AIS',
            'type': 'TUG',
            'type': 'USA',
            'length': 113.0,
            'width': 34.0,
            'draft': 3.1,
            'cargo_weight': 56.0,
            'lat': 26.1,
            'lon': -97.21,
            'dist_from_shore': 0.0,
            'dist_from_port': 0.0
        }

    def teardown_method(self):
        self.db.rollback()
        self.db.close()
        del self.db
        del self.result
        del self.empty_entity
        del self.existing_ship
        del self.new_ship
        del self.ship_missing_geom
        del self.ship_missing_attrs
        del self.ship_missing_mmsi

    def test_add(self):
        self.db.add(self.new_entity)

# TODO: How to mock my pre-existing database!
@pytest.mark.modify
class TestModification():
    def setup_method(self):
        self.db = DBOperator(table="vessels")
        self.result = None

@pytest.mark.within
class TestWithin():
    def setup_method(self):
        self.ZoneOp = DBOperator(table='zones')
        self.StationsOp = DBOperator(table='sources')
        self.VesselOp = DBOperator(table='vessels')
        self.ArchiveOp = DBOperator(table='vessel_archive')

    def teardown_method(self):
        self.ZoneOp.close()
        self.StationsOp.close()

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

    operator= DBOperator(table='vessel_archive')

    pprint(operator.proximity('Point(-91.02 30.13)', 1000))
    print(len(operator.get_table()))
    operator.close()



    # operator = DBOperator(table='zones')
    # operator = DBOperator(table='vessels',host='localhost',port='5432')
    # input()

    ### Get filterable items
    # pprint(operator.fetch_filter_options())
    # input()

    ### Filters
    # filters = [{'type' : 'FISHING','current_status': "anchored"}] # querying multple values for one attribute
    # pprint(operator.query(filters))
    # pprint(len(operator.query(filters)))
    # input()

    ### Add
    # operator.add(entity)
    # operator.commit()

    ### Query
    # pprint(operator.query([{"mmsi": 368261120}])) # Table should have new entity
    # pprint(len(operator.query([{"id":'ANZ650'}]))) # Table should have new entity
    
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

    # operator.close()
