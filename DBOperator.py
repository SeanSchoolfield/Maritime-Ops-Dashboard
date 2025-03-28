from pprint import pprint
from psycopg2 import *
from psycopg2.errors import *
from json import loads, dumps

class DBOperator():
    """
    A basic Class that will directly interface with a PostGIS database on
    behalf of the Maritime Dashboard

    DBOperator will implicitly connect to 'capstone' database unless specified
    otherwise
    """
    # FIXME: All queries assume tables have geometry, and some will not have them!
    #   - expected fix: take table's attr.keys() and replace the 'SELECT *' with SELECT {attrs}
    #       - If geom is in attr.keys(), append with ST_GeomAsJson()
    # FIXME: add() accepts WKT, but doesn't like GeoJSON
    #   - Just threw in a couple lines to convert the geom as needed.
    #   - Want a better fix than that^ !!!
    # WARN: Expecting fetch_filter_options() to not work with tables other than vessels

    """
    // POSTGIS
        - Storing as Geography, likely will have to conver to geography
        - SRID = 4326 !!!
        - Zone stuff
            - ST_Equals() (to check zone existence)
            - ST_Within() (Possibly good for ships encroaching on a zone for warning, or ships near others)
            - ST_Touches() (For bordering ships/zones)
            - ST_DWithin() (FOR SHIPS WITHIN ANY ZONE)!!
            - ST_Contians() (FOR SHIPS WITHIN ZONES)
            - ST_Intersect() (for a custom zone on EEZ/NOAA?)
            - ST_Overlaps(for a custom zone intersecting with EEZ/NOAA, to pull data wrt EEZ/NOAA)
        - Vessel prediction
            - ST_Crosses() (If a projected route crosses another, or if a ship enters a zone)
            - ST_Distance() path prediction
        - Things I think might be useful
            - ST_Disjoint() for zones
            - ST_Area()
            - ST_NRing() == 0
            - ST_ExteriorRing()
            - ST_Perimeter()
    """

    ''' For Yolvin :) 
    def __init__(self, table: str, host='localhost', port='5432', user='postgres',
                 passwd='1234', schema='public', db='capstone') -> None:
    '''
    def __init__(self, table: str, host='', port='', user='',
                 passwd='', schema='public', db='capstone') -> None:
        self.table = table
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd

        try:
            self.__db = connect(
                dbname=db,
                user=user,
                password=passwd,
                host=host,
                port=port
            )
            self.__cursor = self.__db.cursor()
            if table not in self.__get_tables():
                raise RuntimeError(f"Table does not exist")
            print("### DBOperator: Connected to DB")
            self.permissions = self.__get_privileges()
            self.attrs = self.__get_attributes()
        except OperationalError as e:
            print(f"### DBOperator: Error connecting to database:\n{e}")
            raise OperationalError

    ### Mutators ###
    def add(self, entity: dict) -> None:
        """
        Adds entry to connected table
        Expects a dict = {key: value} to enter as attribute and value
        Expects keys to match attrs. If attr is missing from key, ''/0/0.0 is provided.
        Unnacceptable Missing Attrs:
            ID reference values (vessels.mmsi, user.id, user.hash, zone.id, event.id, report.id)
            Geometry
        """
        # TODO: Handle multiple entities for bulk additions
        # I might want to track relations, and organize entity values based off of it.
        # An entity might be added by a source, but then the entity will be immediately updated. It might be worth tracking what the values are so everything is up to date as fast as possible
        #       - Linked List? RoundRobin Queue? Hash table?
        # IDK how I want this to handle a bulk add, but I know it will include cursor.executemany()
        #   - Prolly have entity become entities = [dict]
        #   - Pretty sure this will replicate for modify() and delete() too
        
        #   i.e. JSON is provided, with all values, and data that is unkown/un-needed is given default or NULL value

        geom = None
        # If Geometry element exists, pop it to be added at the end
        if 'geom' in entity.keys():
            geom = entity.pop('geom')
            # print(f"Geometry: {geom}")

        # Format keys as attributes for INSERT INTO cmd
        attrs = ','.join(entity.keys())
        if geom != None: # If geometry was popped, append geom key to attrs
            attrs += ',geom'

        # Define values array for pruning LATER...
        values = [value for value in entity.values()]

        # Pre-formatting SQL command.
        #   Add table, formatted attributes string, and the number of %s to add for values
        cmd = f'''
            INSERT INTO {self.table} ({attrs})
            VALUES ({'%s,' * (len(values))}'''

        if geom != None: # if geom was popped, append value to values array
            values += [geom]
            # values += [dumps(geom)] # NOTE: USING to convert GeoJSON into PostGIS Geography

        # NOW we convert values into tuples
        values = tuple(values)

        # If geom was popped, finish off cmd string formatting append 'ST_GeomFromText()'
        #   Otherwise, just add a ')'
        if geom != None:
            cmd += 'ST_GeographyFromText(%s))'
            # cmd += 'ST_GeogFromWKB(ST_GeomFromGeoJSON(%s)))' # NOTE: USING to convert GeoJSON into PostGIS Geography
        else:
            cmd = cmd[:-1] + ')'

        try:
            self.__cursor.execute(cmd,(values))
            print("### DBOperator: Entry added to commands queue")
        except UniqueViolation as e:
            print(f"### DBOperator ERROR: Unable to add entity: {e}")
            raise UniqueViolation

    def modify(self, entity: tuple, data: dict) -> None:
        """
        Modifys a singular exisitng entity
        """
        # Disgusting
        cmd = f"UPDATE {self.table} SET "
        for i, (key, val) in enumerate(data.items()):
            cmd += f"{key} = {val}" if type(val) != str else f"{key} = '{val}'"
            if i < (len(data.items()) - 1):
                cmd += ","

        self.__cursor.execute(cmd + f" WHERE {entity[0]} = %s", (entity[1],))

    def delete(self, entity: dict) -> None:
        """
        deletes entry that has matching attributes ONLY.
        ONLY deletes from connected table, tables inheriting from connected are NOT processed
            - I'm highly tempted to have it wipe inherited entries as well, but that defeats the purpose of this object
        """
        # NOTE: NO indication that delete is called on non-existent values.
        # Assumes value exists, and just deletes nothing

        if len(entity) == 0:
            raise AttributeError("### DBOperator: Error. Provided entity is empty.")

        print(f"### DBOperator: Deleting {entity}")

        conditions = []
        values = []

        for attr,value in entity.items():
            if attr == 'geom':
                print(f"Geom provided: {attr}:{value}")
                conditions.append(f"{attr} = ST_GeographyFromText(%s)")
            else:
                conditions.append(f"{attr} = %s")
            values.append(value)

        if not conditions:
            return []

        query = f"""
            DELETE FROM ONLY {self.table}
            WHERE {' AND '.join(conditions)}
        """
        print(f"### DBOperator: Query:\n{query}")
        print(f"### DBOperator: Values: {tuple(values)}")

        # input()

        try: 
            self.__cursor.execute(query, tuple(values))
            print("### DBOperator: Deletion reqeust added to queue.")
        except UndefinedColumn as e:
            print(f"{e}\n### DBOperator: Error deleting item.")
            self.rollback() # Uhm... Why are you necessary so other commands don't break?
            raise UndefinedColumn

    def clear(self) -> tuple:
        """
        Clears all entries from table
        """
        self.__cursor.execute(f"DELETE FROM {self.table}")
        return ("message", "table cleared.")

    def custom_cmd(self, cmd: str, call: str) -> list:
        """
        This is here in case you wanna submit custom SQL commands that are not currently supported
        Specify if the command is to read (r) or write (w) from database, so command is committed properly
        """
        # NOTE: WILL IMPLICITLY COMMIT COMMAND
        self.__cursor.execute(cmd)
        if call == 'w':
            self.__db.commit()
            return [("Messge", "Committed.")]
        else:
            return self.__cursor.fetchall()

    # commit command
    def commit(self) -> tuple:
        # NOTE: Currently just want this to be manually executed rn, so changes are user-aware
        self.__db.commit()
        print("### DBOperator: Commands submitted.")
        return ("message", "Committed.")

    # rollback command
    def rollback(self) -> tuple:
        self.__db.rollback()
        print("### DBOperator: Dumped cursor commands.")
        return ("message", "Rollback executed.")

    def close(self) -> tuple:
        """
        Closes table connection
        """
        self.__cursor.close()
        self.__db.close()
        print("### DBOperator: Connection closed.")
        return ("message", "DB instance closed.")

    ### Accessors ###
    def __get_attributes(self) -> dict:
        """
        Fetches table attributes
        """
        self.__cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{self.table}'")
        return {q[0]:q[1] for q in self.__cursor.fetchall()}

    # Fetching tables in DB --> Dev option!
    def __get_tables(self) -> list:
        """
        Fetching tables in DB
        """
        self.__cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        tables = [i[0] for i in self.__cursor.fetchall()]
        # pprint(type(tables))
        # for table in tables:
        #     pprint(table)
        return tables

    def __get_privileges(self) -> dict:
        """
        Lists the privileges assigned to user per a given operation
        """
        operations = ['SELECT', 'INSERT', 'UPDATE', 'DELETE']
        result = {}

        # I doubt this will hold up to ANY sort of load
        for op in operations:
            self.__cursor.execute(f"SELECT has_table_privilege('{self.table}', '{op}')")
            result[f"{op}"] = self.__cursor.fetchone()[0]

        return result

    def fetch_filter_options(self) -> dict:
        """
        Fetches distinct filter options for vessel types, origins, and statuses.
        """
        query = f"""
            SELECT DISTINCT type, flag, current_status AS origin
            FROM {self.table};
        """
        self.__cursor.execute(query)
        vessels = self.__cursor.fetchall()

        # Extract unique filter options
        types = list(set(v[0] for v in vessels if v[0]))
        origins = list(set(v[1] for v in vessels if v[1]))
        statuses = list(set(v[2] for v in vessels if v[2]))

        return {
            "types": types,
            "flag": origins,
            "current_status": statuses
        }

    # pull data from DB
    def query(self, queries: list) -> list:
        """
        Querys entities based on a dictionary of provided filters
        returns list of dictionary types
        """
        # NOTE: NO indication for query on non-existent values.
        # Assume value exists and just returns an empty array.
        cmd = []
        values = []

        if len(queries) == 0:
            raise AttributeError("### DBOperator: Cannot query an empty array...")

        for entity in queries:
            if len(entity) == 0:
                raise AttributeError("### DBOperator: Cannot query an empty dictionary...")
            conditions = []
            for attr,value in entity.items():
                conditions.append(f"{attr} = %s")
                values.append(value)

            if not conditions:
                return []

            cmd.append(f"""
                SELECT *, ST_AsGeoJson(geom)
                FROM {self.table}
                WHERE {' AND '.join(conditions)}
            """)

        try:
            self.__cursor.execute(f"SELECT row_to_json(data) FROM ({' UNION '.join(cmd)}) data", tuple(values))
            results = [i[0] for i in self.__cursor.fetchall()]

            for r in results: # quick formatting to remove binary Geom data
                tmp = r.pop('st_asgeojson')
                r['geom'] = tmp

            return results
        except UndefinedColumn as e:
            print(f"### DBOperator: Error occured:\n{e}")
            raise UndefinedColumn
        except InFailedSqlTransaction as e:
            print(f"{e}\n### DBOperator: Error executing query. Did you forget to rollback an invalid edit-like command?")
            raise InFailedSqlTransaction

    def get_table(self) -> list:
        """
        Returns all entries in a table as a list of dictionary datatypes
        """
        self.__cursor.execute(f"select row_to_json(data) FROM (SELECT *,ST_AsGeoJson(geom) FROM {self.table}) data")

        results = [i[0] for i in self.__cursor.fetchall()]

        for r in results: # quick formatting to remove binary Geom data
            tmp = r.pop('st_asgeojson')
            r['geom'] = tmp

        return results

    def get_count(self) -> int:
        """
        Returns count of entries in table
        """
        # Idea is for this to be faster and more efficeint than pulling the whole table and counting it
        self.__cursor.execute(f"SELECT Count(*) FROM {self.table}")
        return self.__cursor.fetchone()[0]

    """
    ### geom-ship relationships!
    """
    # These are ideally supposed to take advantage of the PostGIS stuff
    def proximity(self, var, range=5000.0):
        """
        Gets vessels witihin a specified range of a geometry
        ST_DWithin(geom, var, range)
        """

        query = f"""
                SELECT mmsi,vessel_name,callsign,heading,speed,current_status,src,type,flag,lat,lon,ST_AsGeoJson(geom)
                FROM {self.table}
                WHERE ST_DWithin(geom, ST_GeogFromText('{var}'),{range})
            """

        """
        select mmsi 
        from vessels 
        where ST_DWithin(geom, St_GeogFromText('Point(-91.02 30.13)'), 5000)
        """
        print(query)

        # input()

        self.__cursor.execute(f"SELECT row_to_json(data) FROM ({query}) data")
        
        results = [i[0] for i in self.__cursor.fetchall()]

        for r in results: # quick formatting to remove binary Geom data
            tmp = r.pop('st_asgeojson')
            r['geom'] = tmp

        return results

    def inside(self, var):
        """
        Gets vessels within a specified geometry
        ST_Contains(var, geom)
        """
        pass


    def borders(self, var):
        """
        Gets vessels that border/touches a specified geometry
        """
        pass
    

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

    entity2 = {
        'mmsi':367702270,
        'vessel_name':'MS. JENIFER TRETTER',
        'callsign':'WDI4813',
        'timestamp':'2024-09-30T00:00:00',
        'heading':334.5,
        'speed':6.6,
        'current_status':'12',
        'src':'MarineCadastre-AIS',
        'type':'TUG',
        'flag':'USA',
        'length':113,
        'width':34,
        'draft':3.1,
        'cargo_weight':57,
        'geom':'Point(-97.21 26.1)',
        'lat':26.1,
        'lon':-97.21,
        'dist_from_shore':0.0,
        'dist_from_port':0.0,
    }

    # operator = DBOperator(table='vessels')
    # print(operator.permissions)
    # print(operator.attrs)
    # input()

    # pprint(operator.proximity('Point(-91.02 30.13)', 1000))
    ### Get filterable items
    # pprint(operator.fetch_filter_options())
    # input()

    ### Filter
    # filters = {
    #     "type": "TUG",
    #     "orign": "USA"
    # }
    # operator.fetch_filtered_vessels(filters)
    # input()

    ### Add
    # operator.add(entity2)
    # operator.commit()

    ### Query
    # pprint(operator.query([{"mmsi":368261120}])) # Table should have new entity
    # pprint(operator.query([]))
    # pprint(operator.query([{}]))
    # input()
    
    ### Modify
    # operator.modify(("mmsi",368261120),{'speed':0.0})
    # operator.commit()
    # print("Changed entry:")
    # pprint(operator.query(("mmsi",368261120)))
    # input()

    ### Delete
    # operator.delete(entity)
    # operator.delete({'mmsi':1234})
    # operator.commit()
    # pprint(operator.query([{"mmsi":368261120}]))

    # operator = DBOperator(table='zones')
    # pprint(operator.query([{'id':'AKC013'}]))
    operator.close()
