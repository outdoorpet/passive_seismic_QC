
import pyasdf
from os.path import join, exists
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import and_
from obspy.core import Stream, UTCDateTime

from anu_timing_QC import cross_correlate_pairs

# =========================== User Input Required =========================== #

#Path to the data
data_path = '/media/obsuser/seismic_data_1/'

#IRIS Virtual Ntework name
virt_net = '_GA_OBS'

# FDSN network identifier (2 Characters)
FDSNnetwork = '8B'

# Service Interval time to check
service_time = '2014-12-05T15:00:00'

# Component to analyse
comp = 'BHZ'

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

# open up new obspy stream object
st = Stream()

# Iterate through stations in the ASDF file
for _i, station_name in enumerate(sta_list):
    print 'Working on Station: {0}'.format(sta_list[_i])

    # Get the helper object to access the station waveforms
    sta_helper = ds.waveforms[station_name]

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

    for matched_waveform in session.query(Waveforms). \
            filter(and_(Waveforms.starttime >= (service_timestamp-1*3600), Waveforms.starttime <= (service_timestamp+1*3600))):

        # Use python condition to retrieve just the desired components
        if not comp in str(matched_waveform.station_id):
            continue

        # Now extract all matched waveforms, concatenate using Obspy and write to ASDF with associated event tag
        # Read in the HDF5 matched waveforms into obspy stream (merge them together)

        # Open up the waveform into an obspy stream object
        # (this will join to previous waveform if there are multiple SQL matches)
        st += sta_helper[matched_waveform.full_id]


# Merge the waveforms together, filling any gaps
st.merge(method=1, fill_value=0)
st.decimate(2)

cross_correlate_pairs.accp(st)