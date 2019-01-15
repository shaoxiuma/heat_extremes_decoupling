#!/usr/bin/env python

"""
For each of the FLUXNET2015 sites, plot the TXx and T-3 days
GPP slope as a function of mean daily air temp

That's all folks.
"""

__author__ = "Martin De Kauwe"
__version__ = "1.0 (20.04.2018)"
__email__ = "mdekauwe@gmail.com"

import os
import sys
import glob
import netCDF4 as nc
import numpy as np
import xarray as xr
import matplotlib.pyplot as plt
import pandas as pd
import re
import constants as c
import string
from scipy import stats

def main(fname, fname2=None, slope_type=None):

    df = pd.read_csv(fname)
    df = df[df.pft == "EBF"]

    # Need to get Alice Springs data, note FLUXNET call it a ENF
    fname = "data/fluxnet2015_all_events.csv"
    df2 = pd.read_csv(fname)
    df2 = df2[~np.isnan(df2.temp)]
    df2 = df2.drop( df2[(df2.site != "AliceSprings")].index )

    df = df.append(df2, ignore_index=True)

    # No events found with matching GPP/LE slopes, removing it so we don't
    # plot an empty panel.
    ignore_sites = ["Tumbarumba"]
    for site in ignore_sites:
        df = df.drop( df[(df.site == site)].index )


    #width  = 12.0
    #height = width / 1.618
    #print(width, height)
    #sys.exit()
    width = 10
    height = 8
    fig = plt.figure(figsize=(width, height))
    fig.subplots_adjust(hspace=0.12)
    fig.subplots_adjust(wspace=0.13)
    plt.rcParams['text.usetex'] = False
    plt.rcParams['font.family'] = "sans-serif"
    plt.rcParams['font.sans-serif'] = "Helvetica"
    plt.rcParams['axes.labelsize'] = 14
    plt.rcParams['font.size'] = 14
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['xtick.labelsize'] = 14
    plt.rcParams['ytick.labelsize'] = 14

    labels = label_generator('lower', start="(", end=")")

    # type doesn't matter, but we only want to do this once.
    if slope_type == "negative":
        f = open(fname2, "w")
        print("site,slope", file=f)

    count = 0
    sites = np.unique(df.site)
    for site in sites:
        site_name = re.sub(r"(\w)([A-Z])", r"\1 \2", site)
        ax = fig.add_subplot(4,2,1+count)

        df_site = df[df.site == site]
        events = int(len(df_site)/4)

        site_max = -9999.
        cnt = 0
        for e in range(0, events):

            x = df_site["temp"][cnt:cnt+4]
            y = df_site["GPP"][cnt:cnt+4]

            (slope, intercept, r_value,
             p_value, std_err) = stats.linregress(x,y)

            # We only want to plot slopes if the direction of change in GPP is
            # opposite the LE, i.e. that they change together
            xx = df_site["temp"][cnt:cnt+4]
            yy = df_site["Qle"][cnt:cnt+4]
            (slope2, intercept2, r_value2,
             p_value2, std_err2) = stats.linregress(xx,yy)

            if slope_type == "negative" and slope2 > 0.0:
                print("%s,%f" % (site, slope), file=f)
            if slope_type == "negative":
                if (slope < 0.0 and p_value <= 0.05) and (slope2 > 0.0):
                    ax.plot(df_site["temp"][cnt:cnt+4],
                            df_site["GPP"][cnt:cnt+4],
                            label=site, color="darkblue", ls="-", marker="o",
                            zorder=100, alpha=0.5, lw=2.0)
                elif (slope < 0.0 and p_value > 0.05) and (slope2 > 0.0):
                    ax.plot(df_site["temp"][cnt:cnt+4],
                            df_site["GPP"][cnt:cnt+4],
                            label=site, ls="-", marker="o", color="darkgreen",
                            alpha=0.4, zorder=1)
            elif slope_type == "positive":
                if (slope > 0.0 and p_value <= 0.05) and (slope2 > 0.0):
                    ax.plot(df_site["temp"][cnt:cnt+4],
                            df_site["GPP"][cnt:cnt+4],
                            label=site, color="darkblue", ls="-", marker="o",
                            zorder=100, alpha=0.5, lw=2.0)
                elif (slope > 0.0 and p_value > 0.05) and (slope2 > 0.0):
                    ax.plot(df_site["temp"][cnt:cnt+4],
                            df_site["GPP"][cnt:cnt+4],
                            label=site, ls="-", marker="o", color="darkgreen",
                            zorder=1, alpha=0.4)

            if np.max(df_site["GPP"][cnt:cnt+4]) > site_max:
                site_max = np.max(df_site["GPP"][cnt:cnt+4]) * 1.5
            cnt += 4
        if count == 2:
            ax.set_ylabel("GPP (g C m$^{-2}$ d$^{-1}$)", position=(3.0, 0.0))
        if count == 6:
            #ax.set_xlabel('Temperature ($^\circ$C)', position=(1.0, 0.5))
            ax.set_xlabel('Temperature ($\degree$C)', position=(1.0, 0.5))

        if count < 5:
            plt.setp(ax.get_xticklabels(), visible=False)

        #if count != 0 and count != 2 and count != 4 and count != 6:
        #    plt.setp(ax.get_yticklabels(), visible=False)

        props = dict(boxstyle='round', facecolor='white', alpha=1.0,
                     ec="white")
        fig_label = "%s %s" % (next(labels), site_name)
        ax.text(0.02, 0.95, fig_label,
                transform=ax.transAxes, fontsize=12, verticalalignment='top',
                bbox=props)


        from matplotlib.ticker import MaxNLocator
        ax.yaxis.set_major_locator(MaxNLocator(4))
        #ax.set_ylim(0, 15)

        if count == 0:
            ax.set_ylim(0, 3)
        elif count == 1:
            ax.set_ylim(0, 4)
        elif count == 2:
            ax.set_ylim(0, 5)
        elif count == 3:
            ax.set_ylim(0, 7)
        elif count == 4:
            ax.set_ylim(0, 3)
        elif count == 5:
            ax.set_ylim(0, 7)
        elif count == 6:
            ax.set_ylim(0, 15)


        ax.set_xlim(18, 47)
        count += 1

    #plt.show()
    #sys.exit()

    ofdir = "/Users/mdekauwe/Dropbox/fluxnet_heatwaves_paper/figures/figs"
    ofname = "all_events_GPP_%s.pdf" % (slope_type)
    fig.savefig(os.path.join(ofdir, ofname),
                bbox_inches='tight', pad_inches=0.1)

    if slope_type == "negative":
        f.close()

def label_generator(case='lower', start='', end=''):
    choose_type = {'lower': string.ascii_lowercase,
                   'upper': string.ascii_uppercase}
    generator = ('%s%s%s' %(start, letter, end) for letter in choose_type[case])

    return generator

if __name__ == "__main__":

    data_dir = "data/"
    fname = "ozflux_all_events.csv"
    fname = os.path.join(data_dir, fname)
    fname2 = "ozflux_slopes_GPP.csv"
    fname2 = os.path.join(data_dir, fname2)
    main(fname, fname2, slope_type="negative")
    main(fname, slope_type="positive") # supplementary
