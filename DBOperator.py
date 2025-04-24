import csv
from pprint import pprint
from psycopg2 import *
from psycopg2.errors import *
from json import loads, dumps

'''
// TODO:
- Add ability to exclude attr:value for query/delete
- Querying/Deleting substrings????
'''


class DBOperator():
    """
    A basic Class that will directly interface with a PostGIS database on
    behalf of the Maritime Dashboard

    DBOperator will implicitly connect to 'capstone' database unless specified
    otherwise
    """
    # FIXME: add() accepts WKT, but doesn't like GeoJSON
    #   - Just threw in a couple lines to convert the geom as needed.
    #   - Want a better fix than that^ !!!
    # WARN: Expecting fetch_filter_options() to not work with tables other than vessels


    ''' For Yolvin :) 
    def __init__(self, table: str, host='localhost', port='5432', user='postgres',
                 passwd='1234', schema='public', db='capstone') -> None:
    '''
    # def __init__(self, table: str, host='localhost', port='5432', user='postgres',
    #                 passwd='', schema='public', db='capstone') -> None:

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
            ID reference values (vessels.mmsi, user.id, user.hash, zone.id)
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
        if geom != None:  # If geometry was popped, append geom key to attrs
            attrs += ',geom'

        # Define values array for pruning LATER...
        values = [value for value in entity.values()]

        # Pre-formatting SQL command.
        #   Add table, formatted attributes string, and the number of %s to add for values
        cmd = f'''
            INSERT INTO {self.table} ({attrs})
            VALUES ({'%s,' * (len(values))}'''

        if geom != None:  # if geom was popped, append value to values array
            values += [geom]
            # values += [dumps(geom)] # NOTE: USING to convert GeoJSON into PostGIS Geography

        # NOW we convert values into tuples
        values = tuple(values)

        # If geom was popped, finish off cmd string formatting append 'ST_GeomFromText()'
        #   Otherwise, just add a ')'
        if geom != None:
            cmd += 'ST_GeographyFromText(%s))'
            # NOTE: USING to convert GeoJSON into PostGIS Geography
            # cmd += 'ST_GeogFromWKB(ST_GeomFromGeoJSON(%s)))'
        else:
            cmd = cmd[:-1] + ')'

        try:
            self.__cursor.execute(cmd, (values))
        except UniqueViolation as e:
            print(f"### DBOperator ERROR: Unable to add entity: {e}")
            raise UniqueViolation

    # TODO: Finish!
    def modify(self, entity: dict, data: dict) -> None:
        """
        Modifys a singular exisitng entity
        """
        # TODO: Try getting dict working for entity!
        if len(data) == 0:
            raise AttributeError(
                "### DBOperator: Error. No data provided.")
        if len(entity) == 0:
            raise AttributeError(
                "### DBOperator: Error. Entity is empty.")

        conditions = []
        changes = []
        values = []

        # Constructing changes for 'SET' clause
        for attr, value in data.items():
            if attr == 'geom':
                print(f"Geom provided: {attr}:{value}")
                # Potentially an issue if passed GeoJSON
                changes.append(f"{attr} = ST_GeographyFromText(%s)")
            else:
                changes.append(f"{attr} = %s")
            values.append(value)

        # Constructing conditions for 'WHERE' clause
        # since the values need to be associated with the '%s' in the WHERE
        # clause, this HAS to be last
        for attr, value in entity.items():
            if attr == 'geom':
                print(f"Geom provided: {attr}:{value}")
                # Potentially an issue if passed GeoJSON
                conditions.append(f"{attr} = ST_GeographyFromText(%s)")
            else:
                conditions.append(f"{attr} = %s")
            values.append(value)

        query = f"""
            UPDATE {self.table}
            SET {' AND '.join(changes)}
            WHERE {' AND '.join(conditions)}
        """

        # DEBUG
        print(query)
        print()
        pprint(values)
        input()

        try:
            self.__cursor.execute(query, tuple(values))
            print("### DBOperator: Update reqeust added to queue.")
        except UndefinedColumn as e:
            print(f"{e}\n### DBOperator: Error updating item.")
            self.rollback()  # Uhm... Why are you necessary so other commands don't break?
            raise UndefinedColumn

    # TODO: TEST!
    def delete(self, entity: dict) -> None:
        """
        deletes entry that has matching attributes ONLY.
        ONLY deletes from connected table, tables inheriting from connected are NOT processed
            - I'm highly tempted to have it wipe inherited entries as well, but that defeats the purpose of this object
        """
        # NOTE: NO indication that delete is called on non-existent values.
        # Assumes value exists, and just deletes nothing

        if len(entity) == 0:
            raise AttributeError(
                "### DBOperator: Error. Entity is empty.")

        conditions = []
        values = []

        for attr, value in entity.items():
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

        try:
            self.__cursor.execute(query, tuple(values))
            print("### DBOperator: Deletion reqeust added to queue.")
        except UndefinedColumn as e:
            print(f"{e}\n### DBOperator: Error deleting item.")
            self.rollback()  # Uhm... Why are you necessary so other commands don't break?
            raise UndefinedColumn

    def custom_cmd(self, cmd: str, call: str) -> list:
        """
        This is here in case you wanna submit custom SQL commands that are not currently supported
        Specify if the command is to read (r) or write (w) from database, so command is committed properly
        """
        # NOTE: WILL IMPLICITLY COMMIT COMMAND
        self.__cursor.execute(cmd)
        if call == 'w':
            self.__db.commit()
            return [("Message", "Committed.")]
        else:
            return self.__cursor.fetchall()

    # NOTE: Do these need to return anything?
    def clear(self) -> tuple:
        """
        Clears all entries from table
        """
        self.__cursor.execute(f"DELETE FROM {self.table}")
        print(f"### DBOperator: {self.table} Cleared.")
        return ("message", "table cleared.")

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
        Fetches table attributes and converts them into vaid Python types
        """
        self.__cursor.execute(
            f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{self.table}'")

        result = {}

        for key, value in {q[0]: q[1] for q in self.__cursor.fetchall()}.items():
            if value in "bigint,smallint,integer".split(','):
                result.update({key: type(1)})
            elif value in "double precision,numeric,decimal,real".split(','):
                result.update({key: type(1.1)})
            # Not sure if I wanna use type(dict) for geom attrs or keep it as string for JSON
            elif value in "character varying,text,name,USER-DEFINED".split(','):
                result.update({key: type("goober")})
            elif value in "boolean".split(','):
                result.update({key: type(True)})
            elif value in "ARRAY".split(','):
                result.update({key: type([1, 2, 3])})
            else:
                result.update({key: "unk"})

        return result

    def __get_tables(self) -> list:
        """
        Fetching tables in DB
        """
        self.__cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
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
            self.__cursor.execute(
                f"SELECT has_table_privilege('{self.table}', '{op}')")
            result[f"{op}"] = self.__cursor.fetchone()[0]

        return result

    # TODO: FIXME
    def fetch_filter_options(self) -> dict:
        """
        Fetches distinct filter options for vessel types, origins, and statuses.
        """
        query = f"""
            SELECT DISTINCT type, flag, current_status
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
            raise AttributeError(
                "### DBOperator: Cannot query an empty array...")

        for entity in queries:
            if len(entity) == 0:
                raise AttributeError(
                    "### DBOperator: Cannot query an empty dictionary...")
            conditions = []
            for attr, value in entity.items():
                conditions.append(f"{attr} = %s")
                values.append(value)

            if not conditions:
                return []

            cmd.append(f"""
                SELECT *{',ST_AsGeoJson(geom)' if 'geom' in self.attrs.keys() else ''}
                FROM {self.table}
                WHERE {' AND '.join(conditions)}
            """)

        try:
            self.__cursor.execute(
                f"SELECT row_to_json(data) FROM ({' UNION '.join(cmd)}) data", tuple(values))
            results = [i[0] for i in self.__cursor.fetchall()]

            if 'geom' in self.attrs.keys():
                for r in results:  # quick formatting to remove binary Geom data
                    tmp = r.pop('st_asgeojson')
                    r['geom'] = tmp

            return results
        except UndefinedColumn as e:
            print(f"### DBOperator: Error occured:\n{e}")
            raise UndefinedColumn
        except InFailedSqlTransaction as e:
            print(
                f"{e}\n### DBOperator: Error executing query. Did you forget to rollback an invalid edit-like command?")
            raise InFailedSqlTransaction

    def get_table(self) -> list:
        """
        Returns all entries in a table as a list of dictionary datatypes
        """
        self.__cursor.execute(f"""
                SELECT row_to_json(data)
                FROM (SELECT *{',ST_AsGeoJson(geom)' if 'geom' in self.attrs.keys() else ''}
                FROM {self.table}) data
                """)

        results = [i[0] for i in self.__cursor.fetchall()]

        if 'geom' in self.attrs.keys():
            for r in results:  # quick formatting to remove binary Geom data
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
    ### geom-based relationships!
    """
    # These are ideally supposed to take advantage of the PostGIS stuff

    def proximity(self, var: str, range=5000.0):
        """
        Gets geometry witihin a specified range of a geometry
        """
        if "geom" not in self.attrs.keys():
            raise AttributeError(
                "Cannot call GIS function on table with no 'geom' attrubute.")

        query = f"""
                SELECT mmsi,vessel_name,callsign,heading,speed,current_status,src,type,flag,lat,lon,dist_from_shore,dist_from_port,ST_AsGeoJson(geom)
                FROM {self.table}
                WHERE ST_DWithin(geom, ST_GeogFromText('{var}'),{range})
            """

        self.__cursor.execute(f"SELECT row_to_json(data) FROM ({query}) data")

        results = [i[0] for i in self.__cursor.fetchall()]

        for r in results:  # quick formatting to remove binary Geom data
            tmp = r.pop('st_asgeojson')
            r['geom'] = tmp

        return results

    # TODO: TEST
    def within(self, var: dict) -> list:
        """
        Gets entity within a (Multi) Polygon
        """
        if "geom" not in self.attrs.keys():
            raise AttributeError(
                "Cannot call GIS function on table with no 'geom' attrubute.")

        query = f"""
                SELECT *,ST_AsGeoJson(geom)
                FROM {self.table}
                WHERE ST_Within(geom::geometry, ST_GeomFromGeoJSON(%s))
            """

        self.__cursor.execute(
            f"SELECT row_to_json(data) FROM ({query}) AS data", (dumps(var),))

        results = [i[0] for i in self.__cursor.fetchall()]

        for r in results:  # quick formatting to remove binary Geom data
            tmp = r.pop('st_asgeojson')
            r['geom'] = tmp

        return results

    # TODO: TEST
    def overlaps(self, var: dict):
        """
        Gets (Multi) Polygon that overlaps a (Multi) Polygon
        """
        if "geom" not in self.attrs.keys():
            raise AttributeError(
                "Cannot call GIS function on table with no 'geom' attrubute")

        query = f"""
                SELECT *,ST_AsGeoJson(geom)
                FROM {self.table}
                WHERE ST_Overlaps(geom::geometry, ST_MakeValid(ST_GeomFromGeoJSON(%s)))
            """

        self.__cursor.execute(
            f"SELECT row_to_json(data) FROM ({query}) AS data", (dumps(var),))

        results = [i[0] for i in self.__cursor.fetchall()]

        for r in results:  # quick formatting to remove binary Geom data
            tmp = r.pop('st_asgeojson')
            r['geom'] = tmp

        return results

    # TODO: TEST
    def contains(self, var: dict):
        """
        Gets entity that contains geometry
        """
        if "geom" not in self.attrs.keys():
            raise AttributeError(
                "Cannot call GIS function on table with no 'geom' attrubute")

        query = f"""
                SELECT *,ST_AsGeoJson(geom)
                FROM {self.table}
                WHERE ST_Contains(geom::geometry, ST_GeomFromGeoJSON(%s))
            """

        self.__cursor.execute(
            f"SELECT row_to_json(data) FROM ({query}) AS data", (dumps(var),))

        results = [i[0] for i in self.__cursor.fetchall()]

        for r in results:  # quick formatting to remove binary Geom data
            tmp = r.pop('st_asgeojson')
            r['geom'] = tmp

        return results

    def meets(self, var):
        """
        Gets a geometry that touches the broundary of (Multi) Polygon
        """
        if "geom" not in self.attrs.keys():
            raise AttributeError(
                "Cannot call GIS function on table with no 'geom' attrubute")

        pass


if __name__ == "__main__":


    # pprint(operator.query([{'id':'AKC013'}]))
    # operator.close()

    # print(operator.permissions)
    # pprint(operator.attrs)
    # print("Table attributes:")
    # pprint(operator.attrs.keys())
    # print("Table attribute datatypes:")
    # pprint(operator.attrs.values())

    # Add
    # operator.add()
    # operator.commit()

    # Modify
    # operator.modify()
    # operator.commit()

    # Delete
    # operator.delete()
    # operator.commit()

    # Clear
    # operator.clear()
    # operator.commit()

    """
    Scratch work
    """
    operator = DBOperator(table='vessels')
    # operator = DBOperator(table='zones')
    # operator = DBOperator(table='sources')
    # operator = DBOperator(table='meteorology')
    # operator = DBOperator(table='oceanography')
    # operator = DBOperator(table='events')

    # FIXME: TopologyError when trying to check zones containing some stations
    #        Following stations threwe TopologyException:
    #          - ILM
    #          - CHS
    #          - LWX
    #          - AKQ
    #          - TBW

    # print(f"Entities in table: {operator.get_count()}")
    # results = operator.query([{'type':'NOAA-NWS'}])
    # operator.close()
    # zoneOp = DBOperator(table='zones')

    # for station in results:
    #     print(f"Checking Station: {station['id']}")
    #     try:
    #         print(len(zoneOp.contains(loads(station['geom']))))
    #     except Exception as e:
    #         print(f"Station {station['id']} threw error:\n{e}")
    #         zoneOp.rollback()
    #         input()

    # print(len(results))

    geom = {'coordinates': [[['-83.5959', '27.9413'],
                             ['-83.5968', '27.4006'],
                             ['-82.9061', '27.3887'],
                             ['-82.9911', '27.9317']]],
            'type': 'Polygon'}
    zones = operator.overlaps(geom)
    operator.close()

    operator = DBOperator(table='sources')
    # Does the zone overlap known zones, and do those zones contain stations?
    stations = []
    for zone in zones:
        stations.extend(operator.within(loads(zone['geom'])))

    pprint(stations)




















