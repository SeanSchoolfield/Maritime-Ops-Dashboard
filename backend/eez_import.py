import csv
from pprint import pprint
from DBOperator import DBOperator

table = DBOperator(table='zones')
eez = DBOperator(db='demo',table='eez_v12')
dubs = 0
els = 0

"""
EEZs
"""

# pprint(eez.attrs)
# input()
eez_arr = eez.get_table()
eez.close()

for thingy in eez_arr:
    entity = {}
    # print(f"mrgid: {thingy[1]}") # zone_id ??counting connections omaha?
    entity['id'] = thingy[1]
    # print("geom")
    # pprint(thingy[-1]) # Geom!
    entity['geom'] = thingy[-1]
    # print("src_id: NULL") # How to retrieve?
    entity['src_id'] = "" # TODO: Search for src_id length 0 and update with source IDs!
    # print(f"Region: {thingy[23]}-{thingy[7]}")
    entity['region'] = f'{thingy[23]}-{thingy[7]}'
    entity['type'] = "EEZ"
    # print(f"geoname: {thingy[2]}") # Another name ???
    entity['name'] = thingy[2]
    # print(f"fid: {thingy[0]}")
    # print(f"mrgid_eez: {thingy[21]}")
    # print(f"mrgid_ter1: {thingy[3]}")
    # print(f"mrgid_ter2: {thingy[9]}")
    # print(f"mrgid_ter3: {thingy[14]}")
    # print(f"mrgid_sov1: {thingy[5]}")
    # print(f"mrgid_sov2: {thingy[10]}")
    # print(f"mrgid_sov3: {thingy[15]}")
    # print(f"territory1: {thingy[6]}") # Region?
    # print(f"territory2: {thingy[11]}")
    # print(f"territory3: {thingy[16]}")
    # print(f"sovereign1: {thingy[8]}")
    # print(f"sovereign2: {thingy[13]}")
    # print(f"sovereign3: {thingy[18]}")
    # print(f"iso_ter2: {thingy[12]}")
    # print(f"iso_ter3: {thingy[17]}")
    # print(f"iso_sov2: {thingy[24]}")
    # print(f"iso_sov3: {thingy[25]}")
    # print(f"un_ter1: {thingy[29]}")
    # print(f"un_ter2: {thingy[30]}")
    # print(f"un_ter3: {thingy[31]}")
    # print(f"un_sov1: {thingy[26]}")
    # print(f"un_sov2: {thingy[27]}")
    # print(f"un_sov3: {thingy[28]}")
    # print(f"pol_type: {thingy[4]}")
    # print(f"x_1: {thingy[19]}")
    # print(f"y_1: {thingy[20]}")
    # print(f"area: {thingy[22]} square km") # area

    # pprint(entity)
    # input()

    try:
        # Add to zones table
        # print("Adding to Zones...")
        table.add(entity)
        table.commit()
        dubs += 1
    except Exception as e:
        els += 1
        table.rollback()
        print(f"{e}\nError adding to zones...")
        with open('eez_failures.csv', 'a', newline='') as outFile:
            writer = csv.DictWriter(outFile, delimiter=',', fieldnames=entity.keys())
            writer.writerow(entity)
    # input()

print(f"Size of EEZ table: {len(eez_arr)}")
print(f"{dubs} zones added to DB")
print(f"{els} zones failed were not added to DB")

table.close()

"""
EEZ Boundaries
"""
# eez_boundaries = DBOperator(db='demo',table='eez_boundaries_v12')
# eez_boundary_arr = eez_boundaries.get_table()
# # thingy = eez_boundary_arr[0]
# # pprint(thingy)
# for thingy in eez_boundary_arr:
#     print(f"fid: {thingy[0]}")
#     print(f"line_id: {thingy[1]}") # zone_id ???
#     print(f"line_name: {thingy[2]}") # name
#     print(f"line_type: {thingy[3]}")
#     print(f"mrgid_sov1: {thingy[4]}")
#     print(f"mrgid_ter1: {thingy[5]}")
#     print(f"territory1: {thingy[6]}")
#     print(f"sovereign1: {thingy[7]}") # Flag
#     print(f"mrgid_ter2: {thingy[8]}")
#     print(f"territory2: {thingy[9]}") # region ???
#     print(f"mrgid_sov2: {thingy[10]}")
#     print(f"sovereign2: {thingy[11]}")
#     print(f"mrgid_eez1: {thingy[12]}")
#     print(f"eez1: {thingy[13]}") # Another name ???
#     print(f"mrgid_eez2: {thingy[14]}")
#     print(f"eez2: {thingy[15]}") # ANOTHER name ???
#     print(f"source1: {thingy[16]}") # Name of source reporting EEZ
#     print(f"url1: {thingy[17]}") # URL source for EEZ 
#     print(f"source2: {thingy[18]}")
#     print(f"url2: {thingy[19]}")
#     print(f"source3: {thingy[20]}")
#     print(f"url3: {thingy[21]}")
#     print(f"origin: {thingy[22]}")
#     print(f"doc_date: {thingy[23]}") # date of report
#     print(f"mrgid_jreg: {thingy[24]}")
#     print(f"joint_reg: {thingy[25]}")
#     print(f"length_km: {thingy[26]}") # length
#     print(f"mrgid_eez3: {thingy[27]}")
#     print(f"eez3: {thingy[28]}")
#     print(f"territory3: {thingy[29]}")
#     print(f"mrgid_ter3: {thingy[30]}")
#     print(f"sovereign3: {thingy[31]}")
#     print(f"mrgid_sov3: {thingy[32]}")
#     print(f"geom: {thingy[-1]}") # Geom MultLineString
#     input()

# print(f"size of EEZ boundaries table: {len(eez_boundary_arr)}")
