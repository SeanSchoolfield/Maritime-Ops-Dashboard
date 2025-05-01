import base64
from Crypto.Cipher import AES
from fastapi import HTTPException
from backend.DBOperator import DBOperator

def connect(table: str) -> DBOperator:
    """
    Attempt DB connection
    """
    # Seans credentials - CHANGE THIS FOR YOUR OWN
    db = 'capstonev2'
    user = 'postgres'
    passwd = 'gres'
    host = 'localhost'
    port = '5432'

    try:
        # print(f"### Fast Server: Attempting to connect to {table}, table with: user=postgres, host=localhost, port=5432")
        instance = DBOperator(table=table)
        # instance = DBOperator(table=table, db=db, user=user, passwd=passwd, host=host, port=port,schema='public')
        print(f"### Fast Server: Connected to {table} table")
        return instance
    except Exception as e:
        print(f"### Fast Server: Unable connect to {table} table, Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Unable to connect to database."
        )

def decrypt_password(encrypted_password, secret_key):
    encrypted_data = base64.b64decode(encrypted_password)
    cipher = AES.new(secret_key.encode('utf-8'), AES.MODE_ECB)
    decrypted_bytes = cipher.decrypt(encrypted_data)
    return decrypted_bytes.strip().decode('utf-8')

def filter_parser(p: dict, result: list) -> None:
    """
    Quick lil recursion function to create a list of dictionaries that have one
    query-able value per attribute
    """

    # WARNING: Creates some duplicate queries when more than one attribute
    # has more than 1 value. Pretty sure its cuz my recursive restraints suck so
    # much ass. Shouldn't affect results since its a UNION query
    for key, val in p.items():
            if not val:
                continue
            if not isinstance(val, list):
                try:
                    val = val.split(",")
                except Exception:
                    continue
            if not val:
                continue

            if key == "ship_types":
                result.append(f"type IN ({','.join(f'\'{v}\'' for v in val)})")
            elif key == "flags":
                result.append(f"flag IN ({','.join(f'\'{v}\'' for v in val)})")
