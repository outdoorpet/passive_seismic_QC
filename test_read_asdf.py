import pyasdf
import matplotlib.pyplot as plt

ds = pyasdf.ASDFDataSet('/g/data1/ha3/Passive/_ANU/7F(2013-2014)/raw_DATA/7F(2013-2014)_test_DB.h5')

print(ds)

print(ds.auxiliary_data)
print(ds.auxiliary_data.DbDict['7F_raw_data_db'])

data_dict = ds.auxiliary_data.DbDict['7F_raw_data_db'].parameters

print data_dict
print data_dict['starttime']
print data_dict['test']

print ds.auxiliary_data.DbDict['7F_raw_data_db'].data

plt.plot(ds.auxiliary_data.DbDict['7F_raw_data_db'].data)
plt.show()

del ds