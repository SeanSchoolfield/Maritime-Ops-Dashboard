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
    - modify() fetch_filter_options()

# TODO: TEST for stuff I want to be non-nullable and unique (set via DB)!

# If we get around to impelemnting Users
- Only accepts valid DB Users
- add()/modify() fails if INSERT/UPDATE permissions fail
- query() fails if SELECT permissions fail
- delete() fails if DELETE permissions fail
"""
@pytest.mark.init
class TestInit():
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
            'geom': {"type":"Point","coordinates":[-91,30.15]},
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

        self.existing_zone = {
            'geom': {"type": "polygon",
                     "coordinates": [[
                     [-93.4067001,43.8486137], [-93.4045944,43.848114], [-93.0588989,43.8484115], [-93.049797,43.848011], [-93.0494003,43.7609138], [-93.0494995,43.7501106], [-93.0492935,43.7312126], [-93.0494995,43.6012115], [-93.0492935,43.5794105], [-93.0494995,43.5554122], [-93.0492935,43.5333137], [-93.0490951,43.5287132],[-93.0492935,43.4997138],[-93.0592956,43.4995117],[-93.2473983,43.4995117],[-93.2672958,43.4993133],[-93.3586959,43.4995117],[-93.4824981,43.4995117],[-93.4925003,43.4994125],[-93.4976959,43.4991111],[-93.5011978,43.4995117],[-93.6368942,43.4995117],[-93.6485977,43.499813],[-93.6483993,43.5542106],[-93.6483993,43.6301116],[-93.6485977,43.6445121],[-93.6483993,43.6736106],[-93.6485977,43.6883125],[-93.6485977,43.7316131],[-93.6483001,43.7752113],[-93.6483993,43.8265113],[-93.6481933,43.8406105],[-93.648796,43.848011],[-93.6245956,43.8482131],[-93.5873947,43.848011],[-93.4678955,43.848114],[-93.4269943,43.848011],[-93.4089965,43.848114],[-93.4067001,43.8486137]
                     ]] },
            'id': 'MNZ093',
            'name': 'Freeborn',
            'region': 'USA-MN',
            'src_id': 'MPX',
            'type': 'FIRE'
        }
        self.existing_event = {
            'active': True,
            'description': 'This station is currently in <a '
                "href='http://tidesandcurrents.noaa.gov/waterconditions.html#high'>high "
                'water condition</a>.',
            'effective': '2025-04-15T18:54:00',
            'end_time': '2025-04-15T19:54:00',
            'expires': '2025-04-15T19:54:00',
            'headline': 'High Water Condition',
            'id': 1,
            'instructions': 'None',
            'severity': 'low',
            'src_id': '1820000',
            'timestamp': '2025-04-15T18:54:00',
            'type': 'Marine alert',
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
            'timestamp': '2025-04-15T17:54:21',
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
            'timestamp': '2025-04-15T18:57:45',
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
            'geom': {"type":"point","coordinates":[-159.3561,21.9544]},
            'id': '1611400',
            'name': 'Nawiliwili',
            'region': 'USA',
            'timezone': 'HAST (GMT -10)',
            'type': 'NOAA-COOP'
        }

    def teardown_method(self):
        self.db.close()
        self.ZoneOp.close()
        self.EventsOp.close()
        self.WeatherOp.close()
        self.OceanOp.close()
        self.StationsOp.close()
        self.VesselOp.close()

        del self.ZoneOp
        del self.EventsOp
        del self.WeatherOp
        del self.OceanOp
        del self.StationsOp
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

    def test_query_different_tables(self):
        # testing valid entires
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

        # Now testing wrong attr/type for different tables
        with pytest.raises(UndefinedColumn): # Might be worth catching and throwing agian?
            result = self.ZoneOp.query([self.existing_zone])
            result = self.EventsOp.query([self.existing_weather])
            result = self.WeatherOp.query([self.existing_ocean])
            result = self.OceanOp.query([self.existing_station])
            result = self.StationsOp.query([self.existing_zone])

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
            'cog': None,
            'current_status': 'UNDERWAY',
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 2.8,
            'flag': 'USA',
            'geom': {"type":"Point","coordinates":[-91,30.15]},
            'heading': 356.3,
            'lat': 30.15,
            'length': 137.0,
            'lon': -91.0,
            'mmsi': 368261120,
            'predicted_path': None,
            'speed': 7.6,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:01',
            'type': 'PASSENGER',
            'vessel_name': 'VIKING MISSISSIPPI',
            'width': 23.0
        }
        self.entity_invalid_type = { 'mmsi': '368261120' }
        self.entity_invalid_attr = { 'id': '368261120' }

        self.zone = {
            'geom': {"type": "polygon",
                     "coordinates": [[
                     [-93.4067001,43.8486137], [-93.4045944,43.848114], [-93.0588989,43.8484115], [-93.049797,43.848011], [-93.0494003,43.7609138], [-93.0494995,43.7501106], [-93.0492935,43.7312126], [-93.0494995,43.6012115], [-93.0492935,43.5794105], [-93.0494995,43.5554122], [-93.0492935,43.5333137], [-93.0490951,43.5287132],[-93.0492935,43.4997138],[-93.0592956,43.4995117],[-93.2473983,43.4995117],[-93.2672958,43.4993133],[-93.3586959,43.4995117],[-93.4824981,43.4995117],[-93.4925003,43.4994125],[-93.4976959,43.4991111],[-93.5011978,43.4995117],[-93.6368942,43.4995117],[-93.6485977,43.499813],[-93.6483993,43.5542106],[-93.6483993,43.6301116],[-93.6485977,43.6445121],[-93.6483993,43.6736106],[-93.6485977,43.6883125],[-93.6485977,43.7316131],[-93.6483001,43.7752113],[-93.6483993,43.8265113],[-93.6481933,43.8406105],[-93.648796,43.848011],[-93.6245956,43.8482131],[-93.5873947,43.848011],[-93.4678955,43.848114],[-93.4269943,43.848011],[-93.4089965,43.848114],[-93.4067001,43.8486137]
                     ]] },
            'id': 'MNZ093',
            'name': 'Freeborn',
            'region': 'USA-MN',
            'src_id': 'MPX',
            'type': 'FIRE'
        }

        self.event = {
            'active': True,
            'description': 'This station is currently in <a '
                "href='http://tidesandcurrents.noaa.gov/waterconditions.html#high'>high "
                'water condition</a>.',
            'effective': '2025-04-15T18:54:00',
            'end_time': '2025-04-15T19:54:00',
            'expires': '2025-04-15T19:54:00',
            'headline': 'High Water Condition',
            'id': 1,
            'instructions': 'None',
            'severity': 'low',
            'src_id': '1820000',
            'timestamp': '2025-04-15T18:54:00',
            'type': 'Marine alert',
            'urgency': 'low'
        }

        self.weather_report = {
            'air_temperature': 76.3,
            'event_id': None,
            'forecast': None,
            'humidity': None,
            'id': 1,
            'precipitation': None,
            'src_id': '1611400',
            'timestamp': '2025-04-15T17:54:21',
            'visibility': None,
            'wind_heading': 82.0,
            'wind_speed': 10.69
        }

        self.ocean_report = {
            'conductivity': None,
            'event_id': None,
            'id': 1,
            'salinity': None,
            'src_id': '1611400',
            'timestamp': '2025-04-15T18:57:45',
            'water_level': 3.76,
            'water_physics': None,
            'water_temperature': 81.1,
            'wave_height': None
        }

        self.station = {
            'datums': ['air_temperature',
                       'wind',
                       'water_temperature',
                       'air_pressure',
                       'water_level',
                       'one_minute_water_level',
                       'predictions'],
            'geom': {"type":"point","coordinates":[-159.3561,21.9544]},
            'id': '1611400',
            'name': 'Nawiliwili',
            'region': 'USA',
            'timezone': 'HAST (GMT -10)',
            'type': 'NOAA-COOP'
        }

        self.ZoneOp = DBOperator(table='zones')
        self.EventOp = DBOperator(table='events')
        self.WeatherOp = DBOperator(table='meteorology')
        self.OceanOp = DBOperator(table='oceanography')
        self.StationOp = DBOperator(table='sources')

    def teardown_method(self):
        if len(self.db.query([self.ship])) == 0:
            ship = {
                'callsign': 'WDN2333',
                'cargo_weight': 65.0,
                'current_status': 'UNDERWAY',
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

        if len(self.ZoneOp.query([self.zone])) == 0:
            self.ZoneOp.add(self.zone)
            self.ZoneOp.commit()
        self.ZoneOp.close()

        if len(self.EventOp.query([self.event])) == 0:
            self.EventOp.add(self.event)
            self.EventOp.commit()
        self.EventOp.close()

        if len(self.WeatherOp.query([self.weather_report])) == 0:
            self.WeatherOp.add(self.weather_report)
            self.WeatherOp.commit()
        self.WeatherOp.close()

        if len(self.OceanOp.query([self.ocean_report])) == 0:
            self.OceanOp.add(self.ocean_report)
            self.OceanOp.commit()
        self.OceanOp.close()

        if len(self.StationOp.query([self.station])) == 0:
            self.StationOp.add(self.station)
            self.StationOp.commit()
        self.StationOp.close()

        del self.ZoneOp
        del self.EventOp
        del self.WeatherOp
        del self.OceanOp
        del self.StationOp
        del self.result
        del self.empty
        del self.ship
        del self.entity_many_attrs
        del self.entity_invalid_type
        del self.entity_invalid_attr
        del self.zone
        del self.event
        del self.weather_report
        del self.ocean_report
        del self.station

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

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            self.db.delete(self.entity_invalid_type)

    def test_invalid_attr(self):
        with pytest.raises(UndefinedColumn):
            self.db.delete(self.entity_invalid_attr)

    def test_del_all_tables(self):
        # events valid entity
        self.EventOp.delete(self.event)
        self.EventOp.commit()
        self.result = self.EventOp.query([self.event])
        assert len(self.result) == 0, "Query shouldn't pull anything"

        # weather valid entity
        self.WeatherOp.delete(self.weather_report)
        self.WeatherOp.commit()
        self.result = self.WeatherOp.query([self.weather_report])
        assert len(self.result) == 0, "Query shouldn't pull anything"

        # ocean valid entity
        self.OceanOp.delete(self.ocean_report)
        self.OceanOp.commit()
        self.result = self.OceanOp.query([self.ocean_report])
        assert len(self.result) == 0, "Query shouldn't pull anything"

        # sources valid entity
        self.StationOp.delete(self.station)
        self.StationOp.commit()
        self.result = self.StationOp.query([self.station])
        assert len(self.result) == 0, "Query shouldn't pull anything"

        # zones valid entity
        self.ZoneOp.delete(self.zone)
        self.ZoneOp.commit()
        self.result = self.ZoneOp.query([self.zone])
        assert len(self.result) == 0, "Query shouldn't pull anything"

        # Each one of these should throw some sort of exception
        with pytest.raises(Exception):
            self.EventOp.delete(self.zone)
            self.WeatherOp.delete(self.station)
            self.OceanOp.delete(self.event)
            self.StationOp.delete(self.weather_report)
            self.ZoneOp.delete(self.ocean_report)

@pytest.mark.add
class TestAdditions():
    def setup_method(self):
        self.db = DBOperator(table="vessels")
        self.result = None
        self.existing_entity = {
            'callsign': 'WDN2333',
            'cargo_weight': 65.0,
            'cog': None,
            'current_status': 'UNDERWAY',
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 2.8,
            'flag': 'USA',
            'geom': {"type":"Point","coordinates":[-91,30.15]},
            'heading': 356.3,
            'lat': 30.15,
            'length': 137.0,
            'lon': -91.0,
            'mmsi': 368261120,
            'predicted_path': None,
            'speed': 7.6,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:01',
            'type': 'PASSENGER',
            'vessel_name': 'VIKING MISSISSIPPI',
            'width': 23.0
        }

        self.new_entity = {
            'callsign': 'WBH6425',
            'cargo_weight': 57.0,
            'current_status': "UNKNOWN",
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 6.3,
            'flag': 'USA',
            'geom': 'Point(-74.11 40.65)',
            'heading': 258.9,
            'lat': 40.65,
            'length': 120.0,
            'lon': -74.11,
            'mmsi': 368504000,
            'speed': 4.1,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:00',
            'type': 'TUG',
            'vessel_name': 'CAPTAIN DANN',
            'width': 18.0
        }

        self.entity_geomJSON = {
            'callsign': 'WBH6425',
            'cargo_weight': 57.0,
            'current_status': "UNKNOWN",
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 6.3,
            'flag': 'USA',
            'geom': {
                'coordinates': [-74.11, 40.65],
                'type': 'Point'},
            'heading': 258.9,
            'lat': 40.65,
            'length': 120.0,
            'lon': -74.11,
            'mmsi': 368504000,
            'speed': 4.1,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:00',
            'type': 'TUG',
            'vessel_name': 'CAPTAIN DANN',
            'width': 18.0
        }

        self.entity_with_invalid_types = {
            'callsign': 'WBH6425',
            'cargo_weight': 57,
            'current_status': 15.0,
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 6.3,
            'flag': 'USA',
            'geom': {
                'coordinates': [-74.11, 40.65],
                'type': 'Point'},
            'heading': '258.9',
            'lat': '40.65',
            'length': '120.0',
            'lon': '-74.11',
            'mmsi': '368504000',
            'speed': '4.1',
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:00',
            'type': 'TUG',
            'vessel_name': 123,
            'width': 18
        }

        self.entity_missing_geom = {
            'callsign': 'WBH6425',
            'current_status': "UNKNOWN",
            'cargo_weight': 57.0,
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 6.3,
            'flag': 'USA',
            'heading': 258.9,
            'lat': 40.65,
            'length': 120.0,
            'lon': -74.11,
            'mmsi': 368504000,
            'speed': 4.1,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:00',
            'type': 'TUG',
            'vessel_name': 'CAPTAIN DANN',
            'width': 18.0
        }

        self.entity_missing_attrs = {
            'cargo_weight': 57.0,
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 6.3,
            'geom': {
                'coordinates': [-74.11, 40.65],
                'type': 'Point'},
            'heading': 258.9,
            'lat': 40.65,
            'length': 120.0,
            'lon': -74.11,
            'mmsi': 368504000,
            'speed': 4.1,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:00',
        }

        self.entity_missing_mmsi = {
            'callsign': 'WBH6425',
            'cargo_weight': 57.0,
            'current_status': "UNKNOWN",
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 6.3,
            'flag': 'USA',
            'geom': 'Point(-74.11 40.65)',
            'heading': 258.9,
            'lat': 40.65,
            'length': 120.0,
            'lon': -74.11,
            'speed': 4.1,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:00',
            'type': 'TUG',
            'vessel_name': 'CAPTAIN DANN',
            'width': 18.0
        }

        self.zone = {
            'geom': {"type": "polygon",
                     "coordinates": [[
                     [-93.4067001,43.8486137], [-93.4045944,43.848114], [-93.0588989,43.8484115], [-93.049797,43.848011], [-93.0494003,43.7609138], [-93.0494995,43.7501106], [-93.0492935,43.7312126], [-93.0494995,43.6012115], [-93.0492935,43.5794105], [-93.0494995,43.5554122], [-93.0492935,43.5333137], [-93.0490951,43.5287132],[-93.0492935,43.4997138],[-93.0592956,43.4995117],[-93.2473983,43.4995117],[-93.2672958,43.4993133],[-93.3586959,43.4995117],[-93.4824981,43.4995117],[-93.4925003,43.4994125],[-93.4976959,43.4991111],[-93.5011978,43.4995117],[-93.6368942,43.4995117],[-93.6485977,43.499813],[-93.6483993,43.5542106],[-93.6483993,43.6301116],[-93.6485977,43.6445121],[-93.6483993,43.6736106],[-93.6485977,43.6883125],[-93.6485977,43.7316131],[-93.6483001,43.7752113],[-93.6483993,43.8265113],[-93.6481933,43.8406105],[-93.648796,43.848011],[-93.6245956,43.8482131],[-93.5873947,43.848011],[-93.4678955,43.848114],[-93.4269943,43.848011],[-93.4089965,43.848114],[-93.4067001,43.8486137]
                     ]] },
            'id': 'MNZ093',
            'name': 'Freeborn',
            'region': 'USA-MN',
            'src_id': 'MPX',
            'type': 'FIRE'
        }

        self.event = {
            'active': True,
            'description': 'This station is currently in <a '
                "href='http://tidesandcurrents.noaa.gov/waterconditions.html#high'>high "
                'water condition</a>.',
            'effective': '2025-04-15T18:54:00',
            'end_time': '2025-04-15T19:54:00',
            'expires': '2025-04-15T19:54:00',
            'headline': 'High Water Condition',
            'id': 1,
            'instructions': 'None',
            'severity': 'low',
            'src_id': '1820000',
            'timestamp': '2025-04-15T18:54:00',
            'type': 'Marine alert',
            'urgency': 'low'
        }

        self.weather_report = {
            'air_temperature': 76.3,
            'event_id': None,
            'forecast': None,
            'humidity': None,
            'id': 1,
            'precipitation': None,
            'src_id': '1611400',
            'timestamp': '2025-04-15T17:54:21',
            'visibility': None,
            'wind_heading': 82.0,
            'wind_speed': 10.69
        }

        self.ocean_report = {
            'conductivity': None,
            'event_id': None,
            'id': 1,
            'salinity': None,
            'src_id': '1611400',
            'timestamp': '2025-04-15T18:57:45',
            'water_level': 3.76,
            'water_physics': None,
            'water_temperature': 81.1,
            'wave_height': None
        }

        self.station = {
            'datums': ['air_temperature',
                       'wind',
                       'water_temperature',
                       'air_pressure',
                       'water_level',
                       'one_minute_water_level',
                       'predictions'],
            'geom': {"type":"point","coordinates":[-159.3561,21.9544]},
            'id': '1611400',
            'name': 'Nawiliwili',
            'region': 'USA',
            'timezone': 'HAST (GMT -10)',
            'type': 'NOAA-COOP'
        }

        self.ZoneOp = DBOperator(table='zones')
        self.EventOp = DBOperator(table='events')
        self.WeatherOp = DBOperator(table='meteorology')
        self.OceanOp = DBOperator(table='oceanography')
        self.StationOp = DBOperator(table='sources')

    def teardown_method(self):
        if len(self.db.query([{'mmsi': 368504000}])) == 1:
            # Should account for all permutations of new_entity
            self.db.delete({'mmsi': 368504000})
            self.db.commit()
        self.db.close()

        if len(self.ZoneOp.query([self.zone])) == 1:
            self.ZoneOp.delete(self.zone)
            self.ZoneOp.commit()
        self.ZoneOp.close()

        if len(self.EventOp.query([self.event])) == 1:
            self.EventOp.delete(self.event)
            self.EventOp.commit()
        self.EventOp.close()

        if len(self.WeatherOp.query([self.weather_report])) == 1:
            self.WeatherOp.delete(self.weather_report)
            self.WeatherOp.commit()
        self.WeatherOp.close()

        if len(self.OceanOp.query([self.ocean_report])) == 1:
            self.OceanOp.delete(self.ocean_report)
            self.OceanOp.commit()
        self.OceanOp.close()

        if len(self.StationOp.query([self.station])) == 1:
            self.StationOp.delete(self.station)
            self.StationOp.commit()
        self.StationOp.close()

        del self.ZoneOp
        del self.EventOp
        del self.WeatherOp
        del self.OceanOp
        del self.StationOp

        del self.db
        del self.result
        del self.existing_entity
        del self.new_entity
        del self.entity_geomJSON
        del self.entity_missing_geom
        del self.entity_missing_attrs
        del self.entity_missing_mmsi
        del self.entity_with_invalid_types
        del self.zone
        del self.event
        del self.weather_report
        del self.ocean_report
        del self.station

    def test_add(self):
        # Should go all hunky-dory
        self.db.add(self.new_entity)
        self.db.commit()
        result = self.db.query([self.new_entity])
        assert len(result) == 1, "Entry should now exist within DB"

    def test_add_Geom_As_JSON(self):
        self.db.add(self.entity_geomJSON)
        self.db.commit()
        result = self.db.query([self.entity_geomJSON])
        assert len(result) == 1, "Entry should now exist within DB"

    def test_empty_add(self):
        # Raise some AttributeError
        with pytest.raises(AttributeError):
            self.db.add({})

    def test_add_non_dict(self):
        with pytest.raises(AttributeError):
            self.db.add([1,2,3,4,5])

    def test_conflicting_add(self):
        # Expecting to throw some pyscopg2 unique violation error
        with pytest.raises(UniqueViolation):
            self.db.add(self.existing_entity)

    # TODO: Test with other tables
    def test_add_missing_attrs(self):
        # Should work, but with missing attrs being None
        self.db.add(self.entity_missing_attrs)
        self.db.commit()
        # Missing: Weight, callsign, current status, flag, type, vessel_name
        result = self.db.query([self.entity_missing_attrs])[0]
        assert result['width'] == 0.0
        assert result['callsign'] == "NONE"
        assert result['current_status'] == "UNKNOWN"
        assert result['flag'] == "OTHER"
        assert result['type'] == "OTHER"
        assert result['vessel_name'] == "UNKNOWN"

    # TODO: Test with other tables
    def test_add_missing_necessary_attrs(self):
        # Should throw some psycopg2 error about a non-nullable value
        with pytest.raises(NotNullViolation):
            self.db.add(self.entity_missing_geom)
            self.db.add(self.entity_missing_mmsi)

    def test_add_invalid_attr(self):
        with pytest.raises(AttributeError):
            self.db.add(self.entity_wrong_attr)

    def test_add_invalid_type(self):
        with pytest.raises(AttributeError):
            self.db.add(self.entity_invalid_type)

    def test_add_all_tables(self):
        # Valid entires
        self.ZoneOp.add(self.zone)
        self.ZoneOp.rollback()
        self.EventOp.add(self.event)
        self.EventOp.rollback()
        self.WeatherOp.add(self.weather_report)
        self.WeatherOp.rollback()
        self.OceanOp.add(self.ocean_report)
        self.OceanOp.rollback()
        self.StationOp.add(self.station)
        self.StationOp.rollback()

        # Should throw some kind of error
        with pytest.raises(Exception):
            self.ZoneOp.add(self.event)
            self.EventOp.add(self.weather_report)
            self.WeatherOp.add(self.station)
            self.OceanOp.add(self.zone)
            self.StationOp.add(self.ocean_report)

@pytest.mark.modify
class TestModification():
    def setup_method(self):
        self.db = DBOperator(table="vessels")
        self.result = None

        self.id = {'mmsi': 367633000}

        self.entity = {
            'callsign': 'WLSY',
            'cog': None,
            'current_status': 'UNDERWAY',
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 11.2,
            'flag': 'USA',
            'geom': {'coordinates': [-82.88, 24.18], 'type': 'Point'},
            'heading': 88.8,
            'lat': 24.18,
            'length': 186.0,
            'lon': -82.88,
            'mmsi': 367633000,
            'predicted_path': None,
            'speed': 11.7,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:00',
            'type': 'TANKER',
            'vessel_name': 'LONESTAR STATE',
            'width': 32.0
        }

        self.non_existent_entity = {
            'callsign': 'WBH6425',
            'cargo_weight': 57.0,
            'current_status': 'UNKNOWN',
            'dist_from_port': 0.0,
            'dist_from_shore': 0.0,
            'draft': 6.3,
            'flag': 'USA',
            'geom': 'Point(-74.11 40.65)',
            'heading': 258.9,
            'lat': 40.65,
            'length': 120.0,
            'lon': -74.11,
            'mmsi': 368504000,
            'speed': 4.1,
            'src': 'MarineCadastre-AIS',
            'timestamp': '2024-09-30T00:00:00',
            'type': 'TUG',
            'vessel_name': 'CAPTAIN DANN',
            'width': 18.0
        }

        self.non_existent_id = {'mmsi': 368504000}

        self.change = {'current_status': "LIMITED MOVEMENT"}

        self.changes = {
            'lat': 24.2489,
            'lon': -82.0407,
            'geom': 'Point(-82.0407 24.2489)',
        }

        self.changes_invalid_attr = {'guh': 'GUH!'}

        self.changes_invalid_type = {'current_status': 15.0}

    def teardown_method(self):
        ship = self.db.query([self.id])[0]
        fixes = {} # changes to revert
        if ship['current_status'] == "LIMITED MOVEMENT":
            fixes.update({'current_status':'UNDERWAY'})
        if ship['lat'] == 24.2489:
            fixes.update({'lat': 24.18})
        if ship['lon'] == -82.0407:
            fixes.update({'lon': -82.88})
        if ship['geom'] == { 'coordinates': [-82.0407, 24.2489], 'type': 'Point' }:
            fixes.update({'geom':{
                'coordinates': [-82.88, 24.18],
                'type': 'Point'
            }})
        if len(fixes) > 0: # Entities were changes and fixes need to be applied
            self.db.modify(self.id,fixes)
            self.db.commit()
        self.db.close()

        del self.db
        del self.result
        del self.id
        del self.entity
        del self.non_existent_entity
        del self.non_existent_id
        del self.change
        del self.changes
        del self.changes_invalid_attr
        del self.changes_invalid_type

    # modify one value
    def test_modify(self):
        self.db.modify(self.id,self.change)
        self.db.commit()
        result = self.db.query([self.id])[0]
        assert result['current_status'] == "LIMITED MOVEMENT"

    # modify many values
    def test_modify_many_attr(self):
        self.db.modify(self.id,self.changes)
        self.db.commit()
        result = self.db.query([self.id])[0]
        assert result['lat'] == 24.2489
        assert result['lon'] == -82.0407
        assert result['geom'] == {
            'coordinates': [-82.0407, 24.2489],
            'type': 'Point'
        }

    # Modify on empty entity
    def test_modify_empty_entity(self):
        with pytest.raises(AttributeError):
            self.db.modify({},self.change)

    # Modify on entity with no data
    def test_modify_empty_data(self):
        with pytest.raises(AttributeError):
            self.db.modify(self.entity,{})

    # modify on non-existent value
    def test_modify_non_existent(self):
        self.db.modify(self.non_existent_id, self.change)
        result = self.db.query([self.non_existent_id])
        assert len(result) == 0, "No new entry should spawn despite modify() technically went through"

    # modify changing invalid attr
    def test_modify_invalid_attr(self):
        with pytest.raises(UndefinedColumn):
            self.db.modify(self.id,self.changes_invalid_attr)

    # modify adding attr with invalid datatype
    def test_modify_invalid_type(self):
        with pytest.raises(TypeError):
            self.db.modify(self.id,self.changes_invalid_type)

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
        'callsign': 'WLSY',
        'cargo_weight': 80,
        'cog': None,
        'current_status': 'UNDERWAY',
        'dist_from_port': 0,
        'dist_from_shore': 0,
        'draft': 11.2,
        'flag': 'USA',
        'geom': {'coordinates': [-82.88, 24.18], 'type': 'Point'},
        'heading': 88.8,
        'lat': 24.18,
        'length': 186,
        'lon': -82.88,
        'mmsi': 367633000,
        'predicted_path': None,
        'speed': 11.7,
        'src': 'MarineCadastre-AIS',
        'timestamp': '2024-09-30T00:00:00',
        'type': 'TANKER',
        'vessel_name': 'LONESTAR STATE',
        'width': 32
    }

    ### PR:
    target = "DON ALFREDO,VELIKA,AVENIR ACCOLADE,SANTA MARIA,SUMMER WIND,CAYO LARGO,KAREN C,OCEAN TOWER,DOROTHY MORAN,BETH M MCALLISTER,DB AVALON".split(',')

    pr_geom = {
        'type': "Polygon",
        'coordinates': [[
            [ "-67.5406", "19.0351" ],
            [ "-64.9088", "18.9670" ],
            [ "-64.8577", "17.4425" ],
            [ "-67.5700", "17.5261" ]
        ]]
    }

    VesselOp= DBOperator(table='vessels')

    result = VesselOp.within(pr_geom)
    ships = VesselOp.query([{'vessel_name':name} for name in target])
    VesselOp.close()
    print("Expected vessels:")
    print(len(target))

    pprint("Vessels retrieved:")
    print(len(result))
    input()

    """
    point [lon, lat]
    DOROTHY MORAN ('geom': '{"type":"Point","coordinates":[-66.09,18.44]}')
    BETH M MCALLISTER ('geom': '{"type":"Point","coordinates":[-66.09,18.45]}')
    """
    ZoneOp = DBOperator(table='zones')
    pprint([i['id'] for i in ZoneOp.overlaps(pr_geom)])

    for ship in ships:
        print(ship['vessel_name'])
        pprint(ship['geom'])
        print(f"Lon: {ship['lon']}")
        print(f"Lat: {ship['lat']}")
        input()
        pprint([i['id'] for i in ZoneOp.contains(ship['geom'])])

    ZoneOp.close()

























