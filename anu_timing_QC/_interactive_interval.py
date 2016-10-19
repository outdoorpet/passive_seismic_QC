import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import RectangleSelector

def onselect(eclick, erelease):
    global bot_left
    global top_right
    bot_left = [eclick.xdata, eclick.ydata]
    top_right = [erelease.xdata, erelease.ydata]


def toggle_selector(event):
    # Press enter to save the rectangle
    if event.key in ['enter']:
        toggle_selector.RS.set_active(False)

        final_bot_left.append(bot_left)
        final_top_right.append(top_right)

        toggle_selector.RS.set_active(True)



def vis_int(di, ser, oth_ser):
    global final_bot_left
    global final_top_right
    final_bot_left = []
    final_top_right = []


    fig = plt.figure(figsize=(16, 10))

    ax = fig.add_subplot(111)

    for ot in oth_ser:
        ax.axvline(x=ot, color='k')

    ax.axvline(x=ser)

    station_lables = di.keys()
    station_lables.insert(0,u'')

    ax.set_yticklabels(station_lables)

    count = 1

    for di_key in di.keys():

        # go through intervals
        for interval in di[di_key]:
            ax.hlines(y=count, xmin=interval[0], xmax=interval[1])
            ax.vlines(interval[0], ymin=count-0.1, ymax=count+0.1)
            ax.vlines(interval[1], ymin=count - 0.1, ymax=count + 0.1)


        count += 1


    #plt.xlim(ser - (24 * 3600), ser + (24 * 3600))
    plt.ylim(0, len(di.keys()) + 1)

    toggle_selector.RS = RectangleSelector(ax, onselect, drawtype='box', useblit=True, interactive=True)
    plt.connect('key_press_event', toggle_selector)
    plt.show()

    return (final_bot_left, final_top_right)
