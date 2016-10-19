
from obspy.signal.cross_correlation import xcorr
import matplotlib.pyplot as plt
import numpy as np

def perform_xcorr(tr_1, tr_2):

    samp_shift = 200

    a, b, xcorr_func = xcorr(tr_1, tr_2, samp_shift, full_xcorr=True)
    X = np.linspace(-1 * samp_shift, samp_shift, samp_shift * 2 + 1)

    print 'Index of max correlation value = ', a
    print 'Value of max correlation value = ', b

    plt.close()

    ax1 = plt.subplot(3, 1, 1)
    ax2 = plt.subplot(3, 1, 2)
    ax3 = plt.subplot(3, 1, 3)

    ax1.plot(tr_1.data)
    ax2.plot(tr_2.data)

    ax3.plot(X, xcorr_func)

    plt.ylabel('Correlation')
    plt.xlabel('Lag')

    plt.show()




def accp(st_bef, st_aft, xcond):

    comp_list = []

    if xcond == 'before' or xcond == 'both':

        for tr_1_bef in st_bef:
            station_1 = tr_1_bef.stats.station

            for tr_2_bef in st_bef:
                station_2 = tr_2_bef.stats.station

                if station_1+'bef_'+station_2+'bef' in comp_list or station_2+'bef_'+station_1+'bef' in comp_list:
                    continue
                # Avoid the autocorrelation
                if station_1 == station_2:
                    continue

                comp_list.append(station_1 + 'bef_' + station_2 + 'bef')

                print '---------------------------------------'
                print tr_1_bef.stats.station, 'bef with ', tr_2_bef.stats.station, ' bef'

                perform_xcorr(tr_1_bef, tr_2_bef)

            if xcond == 'both':

                for tr_2_aft in st_aft:
                    station_2 = tr_2_aft.stats.station

                    if station_1+'bef_'+station_2+'aft' in comp_list or station_2+'aft_'+station_1+'bef' in comp_list:
                        continue

                    comp_list.append(station_1 + 'bef_' + station_2 + 'aft')

                    print '---------------------------------------'
                    print tr_1_bef.stats.station, 'bef with ', tr_2_aft.stats.station, ' aft'

                    perform_xcorr(tr_1_bef, tr_2_aft)

    if xcond == 'after' or xcond == 'both':

        for tr_1_aft in st_aft:
            station_1 = tr_1_aft.stats.station

            for tr_2_aft in st_aft:
                station_2 = tr_2_aft.stats.station

                if station_1+'aft_'+station_2+'aft' in comp_list or station_2+'aft_'+station_1+'aft' in comp_list:
                    continue
                # Avoid the autocorrelation
                if station_1 == station_2:
                    continue

                comp_list.append(station_1 + 'aft_' + station_2 + 'aft')

                print '---------------------------------------'
                print tr_1_aft.stats.station, 'aft with ', tr_2_aft.stats.station, ' aft'

                perform_xcorr(tr_1_aft, tr_2_aft)


    print comp_list