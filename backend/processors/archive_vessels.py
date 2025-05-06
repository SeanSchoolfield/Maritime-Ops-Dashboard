from backend.DBOperator import DBOperator

operator = DBOperator(table='vessels')

vessels = operator.get_table()

print(f"{len(vessels)}")
