import numpy as np
import time
import json
from obspy import UTCDateTime
import random

with open('/g/data1/ha3/Passive/_ANU/7F(2013-2014)/raw_DATA/7F(2013-2014)_raw_dataDB.json', 'r') as f:

    json_dict = json.load(f)



new_dict = {}

dict_list = []



for _i, (key, value) in enumerate(json_dict.iteritems()):
    new_dict[_i] = value
    temp_list = []
    temp_list.append(key)
    for field in value.values():
        temp_list.append(field)

    dict_list.append(temp_list)

db_array = np.array(dict_list)

print(dict_list[0])

sta = ["SQ2A1", "SQ2F6"]
chan = ["BHZ"]
query_time = UTCDateTime(2014, 3, 16, 20).timestamp


# if ((matched_entry['starttime'] <= query_time < matched_entry['endtime']) \
#                                 or (
#                                 query_time <= matched_entry['starttime'] and matched_entry['starttime'] < query_time + (
#                             30 * 60))) \
#                             and ((matched_entry['station'] in select_sta) and (
#                                 matched_entry['component'] in select_comp)):

# keys = random.sample(xrange(len(dict_list)), 1000)
# print(keys)

start_time = time.time()
db_array_masked = np.where((np.in1d(db_array[:,2], sta))
                           & (np.in1d(db_array[:,3], chan))
                           & np.logical_or(np.logical_and(db_array[:,1] <= query_time,  query_time < db_array[:,-1]),
                                           (np.logical_and(query_time <= db_array[:,1],
                                                           db_array[:,-1] < query_time + (30 * 60)))))


# print(np.logical_or(np.logical_and(db_array[:,0] <= query_time, query_time < db_array[:,-1]),(np.logical_and(query_time <= db_array[:,0],db_array[:,-1] < query_time + (30 * 60)))))


run_time = time.time() - start_time
print(db_array_masked[0])
for index in db_array_masked[0]:
    print(db_array[index, 0])
print(len(db_array_masked[0]))
print(run_time)


start_time = time.time()
indices = []

for _i, key in enumerate(new_dict.keys()):
    matched_entry = new_dict[key]
    if ((matched_entry['starttime'] <= query_time < matched_entry['endtime'])
        or (query_time <= matched_entry['starttime'] and matched_entry['starttime'] < query_time + (30 * 60))) \
            and ((matched_entry['station'] in sta) and (matched_entry['component'] in chan)):
        indices.append(_i)

run_time = time.time() - start_time

indices_array = np.array(indices)
print(indices_array)
print(len(indices_array))
print(run_time)


# print '\n'
# if db_array_masked[0].all() == indices_array.all():
#     print(True)



