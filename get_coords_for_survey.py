import json
from collections import defaultdict
import sys

json_file = '/g/data1/ha3/Passive/_ANU/XX/raw_DATA/7F(2013-2014)_raw_dataDB.json'

with open(json_file, 'r') as f:

    # json_load = json.load(f)
    dict = json.load(f)


survey_coords = {}

db_len = len(dict)

counter = 1
for db_key, value in dict.iteritems():
    counter += 1

    if not (value['lat'] and value['lng'] and value['elev']):
        # there are no coordinate information
        continue


    sc_key = value['station']


    if not sc_key in survey_coords.keys():
        survey_coords[sc_key] = ([],[],[])

    else:
        #check if all of the coords match
        if (value['lat'] in survey_coords[sc_key][0]) and (value['lng'] in survey_coords[sc_key][1]) and (value['elev'] in survey_coords[sc_key][2]):
            #matching coords do not duplicate
            continue
        else:
            # at least one of the lat/lng/elev does not match. Append the coords into survey dict
            survey_coords[sc_key][0].append(value['lat'])
            survey_coords[sc_key][1].append(value['lng'])
            survey_coords[sc_key][2].append(value['elev'])

#now print the output
for key in survey_coords.keys():
    print(key, survey_coords[key])
