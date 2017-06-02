from obspy.core import read, UTCDateTime
from obspy.io.mseed.core import _is_mseed
import glob
from os.path import join, basename, exists
import sys
from os import remove
from collections import defaultdict, Counter

import json



# =========================== User Input Required =========================== #

# Path to the data
data_path = '/g/data/ha3/Passive/'

# IRIS Virtual Ntework name
virt_net = '_ANU'

# FDSN network identifier
FDSNnetwork = '7F(2013-2014)'


def make_datetime(filename):
    year = int('20'+filename[-16:-14])
    month = int(filename[-14:-12])
    day = int(filename[-12:-10])
    hr = int(filename[-10:-8])
    min = int(filename[-8:-6])
    sec = int(filename[-6:-4])

    datetime = UTCDateTime(year=year, month=month, day=day, hour=hr, minute=min, second=sec)

    return datetime

json_path = join(data_path, virt_net, FDSNnetwork, 'raw_DATA', FDSNnetwork + '_raw_dataDB.json')
savefile_path = join(data_path, virt_net, FDSNnetwork, 'problem_filenames.txt')

with open(json_path, 'r') as f:

    # json_load = json.load(f)
    dict = json.load(f)


if exists(savefile_path):
    remove(savefile_path)

# savefile = open(savefile_path, 'w')

problems_db = {}

for key, value in dict.iteritems():
    temp_dict = {"problem": defaultdict(list)} #, "solution": defaultdict(list)}

    # check if the station code matches the filename and the directory name
    # print(key, value['station'], value['path'].split('/')[-2])
    if not (value['station'] in key) \
            or not (value['station'] == value['path'].split('/')[-2]) \
            or (value['station'] == ''):

        temp_dict["problem"]["station_mismatch"].append((value['station'], value['path']))

        # problems_db[key].append(("station_mismatch", value['station'], value['path']))

    # get the component name from header
    component = value['component']

    #check if the component matches the filename
    if not key.split('.')[1] == component:
        temp_dict["problem"]["component_mismatch"].append((component, value['path']))
        # problems_db[key].append(("component_mismatch", component, value['path']))


    if len(key) < 15:
        # bad filename.
        # see if it is miniseed
        bool_seed = _is_mseed(join(value['path'], key))
        temp_dict["problem"]["bad_filename"].append((bool_seed, value['path']))
        # problems_db[key].append(("bad_filename", bool_seed, value['path']))

    else:
        # check if the starttime matches the filename
        nt = make_datetime(key)
        ht = UTCDateTime(value['starttime'])

        # if not (nt.year == ht.year and nt.month == ht.month and nt.day == ht.day and nt.hour==ht.hour):# and nt.minute==ht.minute and nt.second==ht.second):
        if (120 <= abs(ht-nt)):
            # if not (value['station'] == 'GA4'):
            #     continue
            # print '______________'
            # print(value['path'], key, value['station'], nt, ht)
            # print(nt-ht)
            # print(ht+(nt-ht))

            # file path, filename, filename time, header_time, time difference
            temp_dict["problem"]["time_mismatch"].append((str(nt),str(ht),str(ht-nt), value['path']))
            # problems_db[key].append(("time_mismatch",str(nt),str(ht),str(ht-nt), value['path']))

    # if there are problems for the filename then add it to the database
    if any(temp_dict['problem']):
        problems_db[key] = temp_dict


for key in problems_db.keys():
    print(key, problems_db[key])

print '\n'
print '--- Found ', len(problems_db), ' Problem filenames ---'

# def getkey(item):
#     return item[4]
#
# # sort the problems by time difference
# sorted_problems = sorted(time_problems_list, key=getkey)
#
# # iterate through and save to text file
# for problem in sorted_problems:
#     savefile.write(problem[0]+'\t'+problem[1]+'\t'+problem[2]+'\t'+problem[3]+'\t'+problem[4]+'\n')
#
# savefile.close()




# # =========================== User Input Required =========================== #
#
# #Path to the data
# data_path = '/media/obsuser/seismic_data_1/'
#
#
# #IRIS Virtual Ntework name
# virt_net = '_GA_ANUtest'
#
# # FDSN network identifier (2 Characters)
# FDSNnetwork = 'XX'
#
# path_out = join(data_path, virt_net, FDSNnetwork, 'raw_DATA/')
#
# # =========================================================================== #
#
# path_DATA = join(data_path, virt_net, FDSNnetwork, 'raw_DATA/')
#
# def make_datetime(filename, station_name):
#     filename = filename.replace(station_name, '')
#     year = int('20'+filename[0:2])
#     month = int(filename[2:4])
#     day = int(filename[4:6])
#     hr = int(filename[6:8])
#     min = int(filename[8:10])
#     sec = int(filename[10:12])
#
#     datetime = UTCDateTime(year=year, month=month, day=day, hour=hr, minute=min, second=sec)
#
#     return datetime
#
#
# # Get a list of service directories
# service_dir_list = glob.glob(path_DATA + '*service*')
#
# #iterate through service directories
# for service in service_dir_list:
#     print '\r Processing: ', basename(service)
#
#     station_dir_list = glob.glob(service + '/*')
#
#     # iterate through station directories
#     for station_path in station_dir_list:
#         station_name = basename(station_path)
#         print '\r Working on station: ', station_name
#
#         seed_files = glob.glob(join(station_path, '*miniSEED/*'))
#
#         savefile = open(join(station_path, basename(service)+'_'+station_name+'_'+'file_naming_check.txt'), 'w')

#         savefile.write('full_path_miniseed\tminiseed_filename\tminiseed_datetime\theader_datetime\n')
#
#         for _i, filename in enumerate(seed_files):
#             print "\r     Parsing miniseed file ", _i + 1, ' of ', len(seed_files), ' ....',
#             sys.stdout.flush()
#
#             # read the miniseed file
#             st = read(filename)
#             # there will only be one trace in stream because the data is by channels
#             tr = st[0]
#
#             nt = make_datetime(basename(filename), station_name)
#             ht = tr.stats.starttime
#
#
#
#             if not (nt.year == ht.year and nt.month == ht.month and nt.day == ht.day and nt.hour==ht.hour and nt.minute == ht.minute):
#                 savefile.write(filename+'\t'+basename(filename)+'\t'+str(nt)+'\t'+str(ht)+'\n')
#
#         savefile.close()