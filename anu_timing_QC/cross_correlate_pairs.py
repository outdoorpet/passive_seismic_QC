
from obspy.signal.cross_correlation import xcorr
import matplotlib.pyplot as plt

def accp(st):
    for tr_1 in st:
        print '.....'
        print tr_1
        station_1 = tr_1.stats.station
        for tr_2 in st:
            station_2 = tr_2.stats.station
            if station_1 == station_2:
                continue
            print tr_2

            a, b, xcorr_func = xcorr(tr_1, tr_2, 1000, full_xcorr=True)


            plt.close()

            plt.plot(xcorr_func)

            plt.show()

            break

        break