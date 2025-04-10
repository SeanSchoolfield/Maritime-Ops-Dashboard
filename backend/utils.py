import base64
from Crypto.Cipher import AES
from fastapi import HTTPException
from DBOperator import DBOperator

def connect(table: str) -> DBOperator:
    """
    Attempt DB connection
    """
    try:
        instance = DBOperator(table=table)
        print(f"### Fast Server: Connected to {table} table")
        return instance
    except Exception as e:
        print(f"### Fast Server: Unable connect to {table} table")
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
    x = {}
    for k, v in p.items():
        # Still gonna parse, even though I think it's unecessary
        val = v if isinstance(v, list) else v.split(',')
        while len(val) > 1:
            q = p.copy()
            q[k] = val.pop(0)
            filter_parser(q,result)
        x.update({k: val[0]})
    result.append(x)
