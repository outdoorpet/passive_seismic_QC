from obspy.core import read
import os

raw_data_path = '/g/data1/ha3/Passive/_ANU/S1/raw_DATA/'

year_list = os.listdir(raw_data_path)
print(year_list)

# iterate through the year directories and then the day directories
for year_dir in year_list:
    year_path = raw_data_path + year_dir

    day_list = os.listdir(year_path)

    for day_dir in day_list:
        day_path = year_path + '/' + day_dir

        seed_list = os.listdir(day_path)

        for seed_file in seed_list:
            print(day_path +'/' + seed_file)

            st = read(day_path +'/' + seed_file)
            tr = st[0]
            tr.stats.network = '7G'

            tr.write(day_path +'/' + seed_file, format="MSEED")
