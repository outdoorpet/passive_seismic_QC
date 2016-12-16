
import pyasdf
from os.path import join, exists
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import or_, and_

from sqlalchemy import Column, Integer, String
from obspy.core import Stream, UTCDateTime

from anu_timing_QC import cross_correlate_pairs
from anu_timing_QC import _interactive_interval
import matplotlib.pyplot as plt

# =========================== User Input Required =========================== #

#Path to the data
data_path = '/g/data/ha3/Seismic/'

#IRIS Virtual Ntework name
virt_net = '_GA_ANUtest'

# FDSN network identifier (2 Characters)
FDSNnetwork = 'XX'

other_service_times = ['2016-09-28T03:30:00', '2016-10-11T02:09:00', '2016-10-12T04:11:00',
                       '2016-10-13T01:30:00', '2016-10-18T03:20:00', '2016-10-20T03:30:00',
                       '2016-10-24T02:35:00', '2016-11-02T04:43:00', '2016-11-08T03:30:00',
                       '2016-11-16T03:30:00']

# Component to analyse
comp = 'EHZ'


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

other_service_timestamps = []
for oth_time in other_service_times:
    other_service_timestamps.append(UTCDateTime(oth_time).timestamp)


q_times = []
# Access the event metadata
event_cat = ds.events

for _j, event in enumerate(event_cat):
    #print '\r  Extracting {0} of {1} Earthquakes....'.format(_j + 1, event_cat.count()),
    #sys.stdout.flush()
    # Get quake origin info
    origin_info = event.preferred_origin() or event.origins[0]
    qtime = origin_info.time.timestamp
    q_times.append(qtime)



# open up new obspy stream object for data
st = Stream()

# data intervals
data_int = {}

# Iterate through stations in the ASDF file
for _i, station_name in enumerate(sta_list):

    # SQL file for station
    SQL_in = r"" + join(data_path, virt_net, FDSNnetwork, 'ASDF', station_name.split('.')[1] + '.db')

    # if the SQL database doesn't exist for the station,
    # then there is no waveforms in the ASDF file for that station
    if not exists(SQL_in):
        print 'No Waveforms for station...'
        continue

    # Initialize the sqlalchemy sqlite engine
    engine = create_engine('sqlite:///' + SQL_in)

    Session = sessionmaker(bind=engine)
    session = Session()

    temp_data_int = []

    # First read in the SQL database to find out all of the data recording intervals
    for matched_waveform in session.query(Waveforms). \
            filter(Waveforms.full_id.like('%'+comp+'%raw_recording%')):

        temp_data_int.append((matched_waveform.starttime, matched_waveform.endtime, matched_waveform.full_id))

    data_int[station_name] = temp_data_int

# returns (coords for bottom left of rectangle, coords for top right of rectangle)
desired_intervals = _interactive_interval.vis_int(data_int, other_service_timestamps, q_times)

print 'Start of selcted interval: ', UTCDateTime(desired_intervals[0][0])
print 'End of selcted interval:   ', UTCDateTime(desired_intervals[1][0])

# desired_intervals = ([UTCDateTime('2016-11-13T11:07:00Z').timestamp],[UTCDateTime('2016-11-13T11:09:00Z').timestamp])

# Now extracting data from the pyasdf file
# go through data interval dictionary
for di_key in data_int.keys():

    print 'Working on Station: {0}'.format(di_key)

    int = []

    # now go through the data_int elements
    for interval in data_int[di_key]:
        # check if the before service desired interval is within the data interval
        if (interval[0] >= desired_intervals[0][0] and desired_intervals[1][0] >= interval[1]) or interval[0] <= desired_intervals[1][0] <= \
                interval[1] or interval[0] <= desired_intervals[0][0] <= interval[1]:
            int.append(interval)

    sta_helper = ds.waveforms[di_key]

    # read in all streams in the interval lists
    # iterate through intervals in before serv:
    for bi in int:
        matched_st = sta_helper[bi[2]]
        #matched_st.filter(type="bandpass", freqmin=0.01, freqmax=2)
        st += matched_st




UTCDateTime.DEFAULT_PRECISION = 6

st.plot()

st.merge()

st.plot()

st.trim(starttime=UTCDateTime(desired_intervals[0][0]), endtime=UTCDateTime(desired_intervals[1][0]), pad=True, fill_value=0)
#st.decimate(4)

st.plot()

print ''
print 'Performing x-correlations ....'
cross_correlate_pairs.accp(st)
