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
        - EITHER throw error to be handled by higher components, or package details to be passed to higher components
    - Can properly package PostGIS stuff for client to process
    - Can handle invalid key: values properly
    - Can properly add/remove/change entries inside DB
    - Can properly call PostGIS commands by providing valid entities, or interpretable errors
    - Only accepts valid DB Users
    - add()/modify() fails if INSERT permissions fail
    - delete() fails if DELETE permissions fail
    - query() fails if SELECT permissions fail
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

    def test_valid_host(self):
        db = DBOperator(table="vessels",host='localhost',port='5432')
        assert isinstance(db, DBOperator), "instance connects to existing DB 'vessels'"

    def test_invalid_host(self):
        with pytest.raises(OperationalError):
            db = DBOperator(table="vessels",host='localhost',port='5432')

    def test_valid_credentials(self):
        db = DBOperator(table="vessels",user='sdj81')
        assert isinstance(db, DBOperator), "instance connects to existing DB 'vessels'"

    def test_invalid_credentials(self):
        with pytest.raises(OperationalError):
            db = DBOperator(table="vessels",user='postgres')
        pass

@pytest.mark.methods
class TestMethods():
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

if __name__ == "__main__":
    # db = DBOperator(table="vessels")
    # db = DBOperator()
    # db = DBOperator(table="some dumb table")
    db = DBOperator(table="vessels",host='localhost',port='5432',user='')
#     pprint(db.get_attributes())
#     pprint(db.get_tables())
