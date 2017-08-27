import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


def psd_plot(pore_radii, pore_dist, log=True, xmax=None):
    """Draws the pore size distribution plot"""
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(pore_radii, pore_dist,
             marker='', color='g', label='distribution')
    if(log):
        ax1.set_xscale('log')
        ax1.xaxis.set_major_locator(ticker.LogLocator(
            base=10.0, numticks=15, numdecs=20))
    ax1.set_title("PSD plot")
    ax1.set_xlabel('Pore width (nm)')
    ax1.set_ylabel('Pore size')
    ax1.legend(loc='best')
    ax1.set_xlim(xmin=0, xmax=xmax)
    ax1.set_ylim(ymin=0)
    ax1.grid(True)
    plt.show()
