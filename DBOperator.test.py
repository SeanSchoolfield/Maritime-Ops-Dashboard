import DBOperator
import pytest

"""
// TODO
- Items to test
    - DBOperator
        - feed it all sorts of data and reqeusts to push/pull

- Things to test for
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
if __name__ == "__main__":
    print("DBOperator testing IN PROGRESS")
