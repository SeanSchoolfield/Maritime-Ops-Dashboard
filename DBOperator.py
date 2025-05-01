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
                raise RuntimeError(f"### DBOperator Error: Table does not exist")
            print("### DBOperator: Connected to DB")
            self.permissions = self.__get_privileges()
            self.attrs = self.__get_attributes()
        except OperationalError as e:
            print(f"### DBOperator Error: Error connecting to database:\n{e}")
            raise OperationalError

    ### Mutators ###
    def add(self, entity: dict) -> None:
        """
        Adds entry to connected table
        Expects a dict = {key: value} to enter as attribute and value
        Expects keys to match attrs. If attr is missing from key, ''/0/0.0 is provided.
        """

        if len(entity) == 0:
            raise AttributeError("### DBOperator.add() Error: Attempting to add empty dictionary.")

        geom = None
        # If Geometry element exists, pop it to be added at the end
        if 'geom' in entity.keys():
            if type(entity['geom']) == type({'1':1}):
                geom = dumps(entity.pop('geom'))
                postgis = 'ST_GeogFromWKB(ST_GeomFromGeoJSON(%s)))'
            else:
                geom = entity.pop('geom')
                postgis = 'ST_GeographyFromText(%s))'

        # Format keys as attributes for INSERT INTO cmd
        attrs = ','.join(entity.keys())
        # If geometry was popped, append geom key to attrs
        if geom is not None:
            attrs += ',geom'

        # Define values array for pruning LATER...
        values = [value for value in entity.values()]

        cmd = f'''
            INSERT INTO {self.table} ({attrs})
            VALUES ({'%s,' * (len(values))}'''

        # if geom was popped, append value to values array
        if geom is not None:
            values += [geom]

        # NOW we convert values into tuples
        values = tuple(values)

        # If geom was popped, finish off cmd string formatting append 'ST_GeomFromText()'
        #   Otherwise, just add a ')'
        if geom != None:
            cmd += postgis
        else:
            cmd = cmd[:-1] + ')'

        try:
            self.__cursor.execute(cmd, (values))
        except UniqueViolation as e:
            print(f"### DBOperator.add() Error: Entity contains value that already exists.\n{e}")
            self.rollback()
            raise UniqueViolation

        except NotNullViolation as e:
            print(f"### DBOperator.add() Error: Entity missing attribute.\n{e}")
            self.rollback()
            raise NotNullViolation

        except Exception as e: # Generic exception
            print(f"### DBOperator.add() Error: Some error occured adding entity:\n{e}")
            self.rollback()
            raise Exception

    def modify(self, entity: dict, data: dict) -> None:
        """
        Modifies a singular exisitng entity
        """
        # NOTE: NO indication that changes are made on a nonexistent value
        # Assumes value exists, and just modifies nothing

        if len(data) == 0:
            raise AttributeError(
                "### DBOperator.modify() Error: No data provided.")
        if len(entity) == 0:
            raise AttributeError(
                "### DBOperator.modify() Error: Entity is empty.")

        conditions = []
        changes = []
        values = []

        # Constructing changes for 'SET' clause
        for attr, value in data.items():

            # Checking if passed key exists as table attribute
            if attr not in self.attrs.keys():
                raise UndefinedColumn(
                    f"### DBOperator.modify() Error: {attr} is not a valid attribute for {self.table}")

            # Checking if passed value type matches expected attribute datatype
            if type(value) not in self.attrs[attr]:
                raise TypeError(
                    f"### DBOperator.modify() Error: Invalid type for {attr}")

            # Enabling new Geography data if position updates (for vessels)
            if attr == 'geom':
                if type(value) == type({'1':1}): # GeoJSON
                    changes.append(f"{attr} = ST_GeogFromWKB(ST_GeomFromGeoJSON(%s))")
                    values.append(dumps(value))
                else: # WKT
                    changes.append(f"{attr} = ST_GeographyFromText(%s)")
                    values.append(value)
            else:
                changes.append(f"{attr} = %s")
                values.append(value)

        # Constructing conditions for 'WHERE' clause
        # since the values need to be associated with the '%s' in the WHERE
        # clause, this HAS to be last
        for attr, value in entity.items():
            # Checking if passed key exists as table attribute
            if attr not in self.attrs.keys():
                raise UndefinedColumn(
                    f"### DBOperator.modify() Error: {attr} is not a valid attribute for {self.table}")

            # Checking if passed value type matches expected attribute datatype
            if type(value) not in self.attrs[attr]:
                raise TypeError(
                    f"### DBOperator.modify() Error: Invalid type for {attr}")

            # Ignoring geom attributes if passed with entity. Gonna be
            # consistent and force users to search via ST_Equals()
            # also ignoring attributes that are None
            if attr == 'geom' or value is None:
                continue
            conditions.append(f"{attr} = %s")
            values.append(value)

        query = f"""
            UPDATE {self.table}
            SET {', '.join(changes)}
            WHERE {' AND '.join(conditions)}
        """

        try:
            self.__cursor.execute(query, tuple(values))
            print("### DBOperator Update request added to queue.")
        except UndefinedColumn as e:
            print(f"{e}\n### DBOperator.modify() Error: Error updating item.")
            self.rollback()
            raise UndefinedColumn

    def delete(self, entity: dict) -> None:
        """
        deletes entry that has matching attributes ONLY.
        ONLY deletes from connected table, tables inheriting from connected are NOT processed
        """
        # NOTE: NO indication that delete is called on non-existent values.
        # Assumes value exists, and just deletes nothing

        if len(entity) == 0:
            raise AttributeError(
                "### DBOperator.delete() Error: Entity is empty.")

        conditions = []
        values = []

        for attr, value in entity.items():
            # Ignoring passed geom value. Gonna force users to use
            # geometry-specific query if they wanna query/delete by geom
            # Also ignoring value if is None
            # Also ignoring value if is type Array (just cuz I'm lazy) (TODO)
            if attr == 'geom' or value is None or type(value) == type([1, 2]):
                continue

            # Checking if passed key exists as table attribute
            if attr not in self.attrs.keys():
                raise UndefinedColumn(
                    f"### DBOperator.delete() Error: {attr} is not a valid attribute for {self.table}")

            # Checking if passed value type matches expected attribute datatype
            if type(value) not in self.attrs[attr]:
                raise TypeError(
                    f"### DBOperator.delete() Error: Invalid type for {attr}")

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
            print(f"### DBOperator.delete() Error: Error deleting item:\n{e}")
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
                result.update({key: [type(1)]})
            elif value in "double precision,numeric,decimal,real".split(','):
                result.update({key: [type(1.1)]})
            # Not sure if I wanna use type(dict) for geom attrs or keep it as string for JSON
            elif value in "character varying,text,name".split(','):
                result.update({key: [type("goober")]})
            elif value in "boolean".split(','):
                result.update({key: [type(True)]})
            elif value in "ARRAY".split(','):
                result.update({key: [type([1, 2, 3])]})
            elif value in "USER-DEFINED".split(','):
                result.update({key: [type("guh"),type({'1':1})]})
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
                "### DBOperator.query() Error: Cannot query an empty array...")

        for entity in queries:
            if len(entity) == 0:
                raise AttributeError(
                    "### DBOperator.query() Error: Cannot query an empty dictionary...")
            conditions = []
            for attr, value in entity.items():
                # Just gonna pop geom object from query.
                # Users should call ST_Equals() to query with 'geom'
                # Will also just ignore any attributes with value type None
                # Also ignoring attr if is type Array, because I'm lazy (TODO)
                if attr == 'geom' or value is None or type(value) == type([1, 2]):
                    continue

                # Checking if passed key exists as table attribute
                if attr not in self.attrs.keys():
                    raise UndefinedColumn(
                        f"### DBOperator.query() Error: {attr} is not a valid attribute for {self.table}")

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
                    tmp = loads(r.pop('st_asgeojson'))
                    r['geom'] = tmp

            return results
        except UndefinedColumn as e:
            print(f"### DBOperator.query() Error: Error occured:\n{e}")
            raise UndefinedColumn
        except InFailedSqlTransaction as e:
            print(
                f"{e}\n### DBOperator.query() Error: Error executing query. Did you forget to rollback an invalid edit-like command?")
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
                tmp = loads(r.pop('st_asgeojson'))
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
                "### DBOperator.proximity() Error: Cannot call GIS function on table with no 'geom' attrubute.")

        query = f"""
                SELECT mmsi,vessel_name,callsign,heading,speed,current_status,src,type,flag,lat,lon,dist_from_shore,dist_from_port,ST_AsGeoJson(geom)
                FROM {self.table}
                WHERE ST_DWithin(geom, ST_GeogFromText('{var}'),{range})
            """

        self.__cursor.execute(f"SELECT row_to_json(data) FROM ({query}) data")

        results = [i[0] for i in self.__cursor.fetchall()]

        for r in results:  # quick formatting to remove binary Geom data
            tmp = loads(r.pop('st_asgeojson'))
            r['geom'] = tmp

        return results

    # TODO: TEST
    def within(self, var: dict) -> list:
        """
        Gets entity within a (Multi) Polygon
        """

        if "geom" not in self.attrs.keys():
            raise AttributeError(
                "### DBOperator.within() Error: Cannot call GIS function on table with no 'geom' attrubute.")

        query = f"""
                SELECT *,ST_AsGeoJson(geom)
                FROM {self.table}
                WHERE ST_Within(geom::geometry, ST_GeomFromGeoJSON(%s))
                OR ST_Crosses(geom::geometry,ST_GeomFromGeoJSON(%s))
            """

        self.__cursor.execute(
            f"SELECT row_to_json(data) FROM ({query}) AS data", (dumps(var),dumps(var)))

        results = [i[0] for i in self.__cursor.fetchall()]

        for r in results:  # quick formatting to remove binary Geom data
            tmp = loads(r.pop('st_asgeojson'))
            r['geom'] = tmp

        return results

    # TODO: TEST
    def overlaps(self, var: dict):
        """
        Gets (Multi) Polygon that overlaps a (Multi) Polygon
        """
        if "geom" not in self.attrs.keys():
            raise AttributeError(
                "### DBOperator.query() Error: Cannot call GIS function on table with no 'geom' attrubute")

        query = f"""
                SELECT *,ST_AsGeoJson(geom)
                FROM {self.table}
                WHERE ST_Overlaps(geom::geometry, ST_MakeValid(ST_GeomFromGeoJSON(%s)))
            """

        self.__cursor.execute(
            f"SELECT row_to_json(data) FROM ({query}) AS data", (dumps(var),))

        results = [i[0] for i in self.__cursor.fetchall()]

        for r in results:  # quick formatting to remove binary Geom data
            tmp = loads(r.pop('st_asgeojson'))
            r['geom'] = tmp

        return results

    # TODO: TEST
    def contains(self, var: dict):
        """
        Gets entity that contains geometry
        """
        if "geom" not in self.attrs.keys():
            raise AttributeError(
                "### DBOperator.contains() Error: Cannot call GIS function on table with no 'geom' attrubute")

        query = f"""
                SELECT *,ST_AsGeoJson(geom)
                FROM {self.table}
                WHERE ST_Contains(geom::geometry, ST_GeomFromGeoJSON(%s))
            """

        self.__cursor.execute(
            f"SELECT row_to_json(data) FROM ({query}) AS data", (dumps(var),))

        results = [i[0] for i in self.__cursor.fetchall()]

        for r in results:  # quick formatting to remove binary Geom data
            tmp = loads(r.pop('st_asgeojson'))
            r['geom'] = tmp

        return results

    def meets(self, var):
        """
        Gets a geometry that touches the broundary of (Multi) Polygon
        """
        if "geom" not in self.attrs.keys():
            raise AttributeError(
                "###DBOperator.meets() Error: Cannot call GIS function on table with no 'geom' attrubute")

        pass


if __name__ == "__main__":

    operator = DBOperator(table='vessels')
    # operator = DBOperator(table='zones')
    # operator = DBOperator(table='sources')
    # operator = DBOperator(table='meteorology')
    # operator = DBOperator(table='oceanography')
    # operator = DBOperator(table='events')

    # pprint(operator.query([{'mmsi':367633000}]))
    # operator.close()

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

































