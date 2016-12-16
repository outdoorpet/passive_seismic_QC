
from obspy.signal.cross_correlation import xcorr
import matplotlib.pyplot as plt
import numpy as np

def perform_xcorr(tr_1, tr_2, samp_shift):
    a, b, xcorr_func = xcorr(tr_1, tr_2, samp_shift, full_xcorr=True)
    return (a,b,xcorr_func)




def accp(st):
    samp_shift = 200
    X = np.linspace(-1 * samp_shift, samp_shift, samp_shift * 2 + 1)

    comp_list = []
    a_list = []
    b_list = []
    xcorr_list = []
    for tr_1 in st:
        station_1 = tr_1.stats.station

        for tr_2 in st:
                station_2 = tr_2.stats.station

                if station_1+station_2 in comp_list or station_2+station_1 in comp_list:
                    continue

                # Avoid the autocorrelation
                if station_1 == station_2:
                    continue

                comp_list.append(station_1 + station_2)

                print '--------------------------------------------------------'
                print tr_1.stats.station, ' with ', tr_2.stats.station

                a, b, xcorr_func = xcorr(tr_1, tr_2, samp_shift, full_xcorr=True)

                print 'Index of max correlation value = ', a
                print 'Value of max correlation value = ', b

                a_list.append(a)
                b_list.append(b)
                xcorr_list.append(xcorr_func)

    ax1 = plt.subplot(1, 1, 1)

    plt.ylabel('Correlation')
    plt.xlabel('Lag')
    ax1.grid()

    for i, comp_xcorr in enumerate(comp_list):

        ax1.plot(X, (xcorr_list[i]), label=comp_xcorr, lw=1.2)

    plt.legend()
    plt.show()