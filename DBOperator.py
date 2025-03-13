from pprint import pprint
from psycopg2 import *

class DBOperator():
    """
    A basic Class that will directly interface with a PostGIS database on
    behalf of the Maritime Dashboard

    psycopg2 is DB-API 2.0 Compliant with different geospatial DBs
    (https://peps.python.org/pep-0249/)
    - Enables things like threadsafety too???

    DBOperator will implicitly connect to 'capstone' database unless specified
    otherwise
    """
    # TODO:
    # - push multiple entries to DB
    # - export table(?)
    #     - To CSV/SQL
    # - export database(?)
    #     - To CSV/SQL
    # - import to DB(?)
    #     - From CSV/SQL?
    # - remove fetching table attributes(?)
    # - remove fetching tables in DB(?)
    # - Parsing (Geo)JSON to enter as SQL commands
    #     - Package as JSON

    # - PostGIS related stuff
    #     - Take advantage of geometric functions in PostGIS (See postGIS_notes.txt)
    #         - There's also the geography/projection stuff, definitely gonna use those
    #     - Retrieved data should already be primed for geospatial/projection
    #         - Look @ the projection/geography modules
    #         - refer to geospatial conversion/modify functions!
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
    def __init__(self, table: str, host='localhost', port='5432', user='',
                 passwd='', schema='public', db='capstone') -> None:
        self.table = table
        self.__host = host
        self.__port = port
        self.__user = user
        self.__passwd = passwd
        self.__db = connect(
            dbname=db,
            # user="postgres", #!! Replace this with correct username
            # password="1234", #!! Replace with PostgreSQL password
            # host=self.__host,
            # port=self.__port
        )

        self.__cursor = self.__db.cursor()
    ### Mutators ###
    def fetch_filter_options(self):
        """
        Fetches distinct filter options for vessel types, origins, and statuses.
        """
        query = f"""
            SELECT DISTINCT type, country_of_origin AS origin, status
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
            "origins": origins,
            "statuses": statuses
        }

    def fetch_filtered_vessels(self, filters: dict) -> list:
        """
        Fetches vessels based on filter options.
        """
        conditions = []
        values = []

        if "type" in filters:
            conditions.append("type = %s")
            values.append(filters['type'])
        if "origin" in filters:
            conditions.append("country_of_origin = %s")
            values.append(filters['origin'])
        if "status" in filters:
            conditions.append("status = %s")
            values.append(filters['status'])

        if not conditions:
            return []

        query = f"""
            SELECT id, name, type, country_of_origin, status, latitude, longitude
            FROM {self.table}
            WHERE {' AND '.join(conditions)}
        """

        self.__cursor.execute(query, tuple(values))
        vessels = self.__cursor.fetchall()

        return [
            {
                "id": v[0],
                "name": v[1],
                "type": v[2],
                "country_of_origin": v[3],
                "status": v[4],
                "latitude": v[5],
                "longitude": v[6]
            }
            for v in vessels
        ]
    def add(self, entity: dict) -> None:
        """
        Add entry
        Expects a dict = {key: value} to enter as attribute and value
        """
        # TODO: Handle multiple entities for bulk additions
        # I might want to track relations, and organize entity values based off of it.
        # An entity might be added by a source, but then the entity will be immediately updated. It might be worth tracking what the values are so everything is up to date as fast as possible
        #       - Linked List? RoundRobin Queue? Hash table?
        # IDK how I want this to handle a bulk add, but I know it will include cursor.executemany()
        #   - Prolly have entity become entities = [dict]
        #   - Pretty sure this will replicate for modify() and delete() too
        
        # Wonder if this can be restricted to expect all values to be added to DB
        #   i.e. JSON is provided, with all values, and data that is unkown/un-needed is given default or NULL value

        # pprint(entity)
        # input()

        geom = None
        # If Geometry element exists, pop it to be added at the end
        if 'geom' in entity.keys():
            geom = entity.pop('geom')
            # print(f"Geometry: {geom}")

        # Format keys as attributes for INSERT INTO cmd
        attrs = ','.join(entity.keys())
        if geom != None: # If geometry was popped, append geom key to attrs
            attrs += ',geom'

        # ### DEBUG: Verifying Attributes
        # print(f"attributes ({len(attrs.split(','))}):")
        # pprint(attrs)
        # input()

        # Define values array for pruning LATER...
        values = [value for value in entity.values()]

        # Pre-formatting SQL command.
        #   Add table, formatted attributes string, and the number of %s to add for values
        cmd = f'''
            INSERT INTO {self.table} ({attrs})
            VALUES ({'%s,' * (len(values))}'''

        if geom != None: # if geom was popped, append value to values array
            values += [geom]

        # NOW we convert values into tuples
        values = tuple(values)

        # ### DEBUG: Checking that values were properly assigned
        # print()
        # pprint(f"values({len(values)}):")
        # pprint(values)
        # input()

        # If geom was popped, finish off cmd string formatting append 'ST_GeomFromText()'
        #   Otherwise, just add a ')'
        if geom != None:
            cmd += 'ST_GeographyFromText(%s))'
        else:
            cmd = cmd[:-1] + ')'

        ### DEBUG: Verifying finalized cmd string
        # input(cmd)

        self.__cursor.execute(cmd,(values))
        print("### DBOperator: Entry added to commands queue")

    def modify(self, entity: tuple, data: dict) -> None:
        """
        Modifys a singular exisitng entity
        """
        pprint("Entity targetted:")
        pprint(entity)
        print("")

        pprint("Attributes to update:")
        pprint(data)

        # Disgusting
        cmd = f"UPDATE {self.table} SET "
        for i, (key, val) in enumerate(data.items()):
            cmd += f"{key} = {val}" if type(val) != str else f"{key} = '{val}'"
            if i < (len(data.items()) - 1):
                cmd += ","
        print(cmd)
        print(cmd + f" WHERE {entity[0]} = %s", (entity[1],))

        self.__cursor.execute(cmd + f" WHERE {entity[0]} = %s", (entity[1],))

    def delete(self, entity: tuple) -> None:
        """
        deletes entry that has matching attribute
        ONLY deletes from connected table, tables inheriting from connected are NOT processed
            - I'm highly tempted to have it wipe inherited entries as well, but that defeats the purpose of this class
        """
        # TODO: Might need to check if attr value type is string, so it can be wrapped in single quotes
        pprint("ID to delete:")
        pprint(entity)
        self.__cursor.execute(f"DELETE FROM ONLY {self.table} WHERE {entity[0]} = %s", (entity[1],))

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
        pprint("### DBOperator: Connection closed.")
        return ("message", "DB instance closed.")


    def import_db(self) -> None:
        """
        Import db
        """
        # TODO
        pass

    def importCSV(self) -> None:
        """
        Imports data from CSV file. Assume that the headers match the attributes 1-1
        """
        # TODO
        pass

    def export_db(self) -> None:
        """
        Export db
        """
        # TODO
        pass

    def exportCSV(self) -> None:
        """
        Exports data from table to CSV file.
        """
        # TODO
        pass

    ### Accessors ###
    def get_attributes(self) -> dict:
        """
        Fetches table attributes
        """
        self.__cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{self.table}'")
        return {q[0]:q[1] for q in self.__cursor.fetchall()}

    # Fetching tables in DB --> Dev option!
    def get_tables(self) -> None:
        """
        Fetching tables in DB
        """
        pprint("getting tables in db:")
        self.__cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
        attr = self.__cursor.fetchall()
        for table in attr:
            pprint(table)

    def get_privileges(self) -> dict:
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

    # pull data from DB
    def query(self, entity: tuple) -> dict:
        """
        Querys all of an attr (possibly add constraints and user defined limits?)
        """
        # Might be good to conform this to geospatial functions
        # ... or maybe add additional methods to do so
        self.__cursor.execute(f"SELECT * FROM {self.table} WHERE {entity[0]} = %s", (entity[1],))
        # NOTE: I wonder if it would be better for asynchronous calls to use the 
        # fetchone() command, and just have FAST script call DBOperator.query() n times
        query = self.__cursor.fetchone()
        return {query}

    def get_table(self) -> list:
        """
        querys the whole table
        """
        self.__cursor.execute(f"SELECT * FROM {self.table}")
        return self.__cursor.fetchall()

    def get_count(self) -> int:
        """
        Returns count of entries in table
        """
        # Idea is for this to be faster and more efficeint than pulling the whole table and counting it
        self.__cursor.execute(f"SELECT Count(*) FROM {self.table}")
        return self.__cursor.fetchone()[0]

    # These are ideally supposed to take advantage of the PostGIS stuff
    def get_within(self, geom):
        """
        Gets data within region
        """
        pass

    def get_surrounding(self, geom):
        """
        Gets data within region
        """
        pass

if __name__ == "__main__":
    # db = DBOperator(db=input("Enter db: "),table=input("Enter table: "))
    vessels = DBOperator(db='capstone', table='vessels')

    # pprint()
    # db.get_tables()
    # pprint()
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

    # vessels.add(entity)
    # vessels.commit()
    # pprint("New value:")
    pprint(vessels.query(("mmsi",368261120))) # Table should have new entity
    input()
    # pprint(vessels.delete()) # Entity should now be gone
    vessels.close()

    # pprint("Modifying existing value...")
    # db.modify(('id', 2), {'name':'apple'})
    # db.commit()
    # pprint("Modified value:")
    # pprint(db.query(("id",3))) # Entity should now be modified

    # db.delete(("id",2))
    # db.commit()
    # pprint("New table:")
    # pprint(db.get_table()) # Entity should now be gone

    # pprint("Rolling back clear table...")
    # db.clear()
    # db.rollback()
    # pprint(db.get_table()) # should still have full table

    # pprint("Clearing table...")
    # db.clear()
    # db.commit()
    # pprint(db.get_table()) # table should have no entries

    # db.close()
