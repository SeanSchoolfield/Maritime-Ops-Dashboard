## main.py
Handles GET requests made to localhost:8000. Uses DBOperator to retrive basic information from interfacing with the PostGIS example database "NYC Census Data".

## DBOperator
DBOperator is a basic Object meant to strictly operate on PostGIS tables. It uses the PyGreSQL `pgdb` library to execute PostgreSQL calls. It only performs very basic SQL queries right now, and one entity at a time.

Below is a list of methods that the Object offers:

### DBOperator(table, host, port, user, passwd, schema, db)
Requires a table to be specified in order to define an instance. Assumes a public instance, connected to database "demo" hosted on localhost:5432 with no user logging in

### add(entity: dict)
Takes a dictionary of values to add to database

### modify(entity: tuple, data: dict)
Takes a tuple to identify the existing entity, and a dictionary of data that will update the entitity's attributes

### delete(entity: tuple)
Takes a tuple to identify an entity to delete from table

### custom_cmd(cmd: str, call: str)
Takes an SQL command as a string to execute on database. Will require 'r' or 'w' to identify proper commit() call

### commit() -> tuple
Submits changes made by add(), modify(), clear(), and delete() calls to table.

### rollback() -> tuple
Clears queued changes to table

### close() -> tuple
Closes instance

### get_attributes() -> dict
Pulls the column lables for a table

### get_privileges() -> dict
Pulls the logged in user's privileges to INSERT, SELECT, UPDATE, and DELTE to table.

### query(entity: tuple) -> dict
Takes a tuple to identify an entity to retrieve from table

### get_table() -> list
Pulls all entities from table as a list

### get_count() -> int
Returns a count of all entities within a table
