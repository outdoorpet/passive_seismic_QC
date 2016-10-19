
import pyasdf
from os.path import join, exists
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from obspy.core import Stream, UTCDateTime

from anu_timing_QC import cross_correlate_pairs
from anu_timing_QC import _interactive_interval
import matplotlib.pyplot as plt

# =========================== User Input Required =========================== #

#Path to the data
data_path = '/media/obsuser/seismic_data_1/'

#IRIS Virtual Ntework name
virt_net = '_GA_test'

# FDSN network identifier (2 Characters)
FDSNnetwork = 'XX'

# Service Interval time to check UTC
service_time = '2016-10-11T02:09:00'

other_service_times = ['2016-09-28T03:30:00', '2016-10-11T02:09:00', '2016-10-12T04:11:00', '2016-10-13T01:30:00', '2016-10-18T03:20:00']

# Component to analyse
comp = 'BHZ'

xcond = 'both'

# =========================================================================== #

Base = declarative_base()

class Waveforms(Base):
    __tablename__ = 'waveforms'
    # Here we define columns for the table
    # Notice that each column is also a normal Python instance attribute.
    starttime = Column(Integer)
    endtime = Column(Integer)
    station_id = Column(String(250), nullable=False)
    tag = Column(String(250), nullable=False)
    full_id = Column(String(250), nullable=False, primary_key=True)


# ASDF file (High Performance Dataset) one file per network
ASDF_in = join(data_path, virt_net, FDSNnetwork, 'ASDF', FDSNnetwork + '.h5')

# Open the ASDF file
ds = pyasdf.ASDFDataSet(ASDF_in)

# Get list of stations in ASDF file
sta_list = ds.waveforms.list()

# Convert the service time into a UTCDateTime object and then convert to timestamp
service_timestamp = UTCDateTime(service_time).timestamp

other_service_timestamps = []
for oth_time in other_service_times:
    other_service_timestamps.append(UTCDateTime(oth_time).timestamp)

# open up new obspy stream object for data before service and data after service
st_bef_ser = Stream()
st_aft_ser = Stream()

# data intervals
data_int = {}

# Iterate through stations in the ASDF file
for _i, station_name in enumerate(sta_list):

    # SQL file for station
    SQL_in = join(data_path, virt_net, FDSNnetwork, 'ASDF', station_name.split('.')[1] + '.db')

    # if the SQL database doesn't exist for the station,
    # then there is no waveforms in the ASDF file for that station
    if not exists(SQL_in):
        print 'No Waveforms for station...'
        continue

    # Initialize the sqlalchemy sqlite engine
    engine = create_engine('sqlite:////' + SQL_in)

    Session = sessionmaker(bind=engine)
    session = Session()

    temp_data_int = []

    for matched_waveform in session.query(Waveforms). \
            filter(Waveforms.full_id.like('%BHZ%raw_recording%')):

        temp_data_int.append((matched_waveform.starttime, matched_waveform.endtime, matched_waveform.full_id))

    data_int[station_name] = temp_data_int

desired_intervals = _interactive_interval.vis_int(data_int, service_timestamp, other_service_timestamps)

print desired_intervals

# Now extracting data from the pyasdf file
# go through data interval dictionary
for di_key in data_int.keys():

    print 'Working on Station: {0}'.format(di_key)

    bef_int = []
    aft_int = []

    #now go through the data_int elements
    for interval in data_int[di_key]:
        # check if the before service desired interval is within the data interval
        if interval[0] <= desired_intervals[0][0][0] <= interval[1] or interval[0] <= desired_intervals[1][0][0] <= interval[1]:
            bef_int.append(interval)
            # check if the before service desired interval is within the data interval
        if interval[0] <= desired_intervals[0][1][0] <= interval[1] or interval[0] <= desired_intervals[1][1][0] <= interval[1]:
            aft_int.append(interval)

    sta_helper = ds.waveforms[di_key]

    #read in all streams in the interval lists
    #iterate through intervals in before serv:
    for bi in bef_int:
        matched_st = sta_helper[bi[2]]
        st_bef_ser += matched_st
    for ai in aft_int:
        matched_st = sta_helper[ai[2]]
        st_aft_ser += matched_st



UTCDateTime.DEFAULT_PRECISION = 6


# making the span intervals the same size
span_1 = UTCDateTime(desired_intervals[1][0][0]) - UTCDateTime(desired_intervals[0][0][0])
span_2 = UTCDateTime(desired_intervals[1][1][0]) - UTCDateTime(desired_intervals[0][1][0])

diff_1 = int(span_1-span_2)
diff_2 = int(span_2-span_1)

if diff_2 < 0:
    diff_2 = 0
if diff_1 < 0:
    diff_1 = 0

print "New Spans:"
print UTCDateTime(desired_intervals[0][0][0]), ' ---> ', UTCDateTime(desired_intervals[1][0][0])-diff_1
print UTCDateTime(desired_intervals[0][1][0]), ' ---> ', UTCDateTime(desired_intervals[1][1][0])-diff_2

st_bef_ser.merge()
st_aft_ser.merge()

st_bef_ser.trim(UTCDateTime(desired_intervals[0][0][0]), UTCDateTime(desired_intervals[1][0][0])-diff_1, pad=True, fill_value=0)#, nearest_sample=False)
st_aft_ser.trim(UTCDateTime(desired_intervals[0][1][0]), UTCDateTime(desired_intervals[1][1][0])-diff_2, pad=True, fill_value=0)#, nearest_sample=False)

# filter
#st_bef_ser.filter(type="bandpass", freqmin=0.2, freqmax=10)
#st_aft_ser.filter(type="bandpass", freqmin=0.2, freqmax=10)

print st_bef_ser
print st_aft_ser

print ''
print 'Performing x-correlations ....'
cross_correlate_pairs.accp(st_bef_ser, st_aft_ser, xcond)


