#!/usr/bin/python
#
# Author    Yann Bayle
# E-mail    bayle.yann@live.fr
# License   MIT
# Created   25/05/2016
# Updated   14/10/2016
# Version   1.0.0
#

"""
Description of isrc.py
======================

Provide functions for ISRC as defined by:
http://isrc.ifpi.org/en/isrc-standard/code-syntax

Validate list of ISRCs
Plot year distribution
Plot country repartition

:Example:

python isrc.py
python isrc.py -i /path/isrc.txt -o /path/invalid_ISRCs.txt
python isrc.py -d /path/dir/

"""

import re
import os
import sys
import csv
import argparse
from datetime import date
from collections import Counter
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize
from matplotlib.colorbar import ColorbarBase
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader
import numpy as np

VERBOSE = True

COLOR = {
    "HEADER" : "\033[95m",
    "OKBLUE" : "\033[94m",
    "OKGREEN" : "\033[92m",
    "WARNING" : "\033[93m",
    "ERROR" : "\033[91m",
    "FILE" : "\033[37m",
    "ENDC" : "\033[0m",
    "BOLD" : "\033[1m",
    "UNDERLINE" : "\033[4m"
}

def print_error(msg):
    """Description of print_error

    Print error message and exit program
    """
    disp_msg = COLOR["BOLD"] + COLOR["ERROR"] + "ERROR:\n"
    disp_msg = disp_msg + str(msg) + "\nProgram stopped" + COLOR["ENDC"]
    print(disp_msg)
    sys.exit()

def print_info(msg):
    """Description of print_info

    Print info message
    """
    if VERBOSE:
        print(COLOR["OKBLUE"] + str(msg) + COLOR["ENDC"])

def print_warning(msg):
    """Description of print_warning

    Print warning message
    """
    if VERBOSE:
        print(COLOR["WARNING"] + str(msg) + COLOR["ENDC"])

def print_success(msg):
    """Description of print_success

    Print success message
    """
    if VERBOSE:
        print(COLOR["BOLD"] + COLOR["OKGREEN"] + msg + COLOR["ENDC"])

def plot_worldmap(countries, values, label='', clim=None, verbose=False):
    """Description of plot_worldmap

    This module plots a world map of countries' attribute.
    It takes a list of countries and their corresponding values.
    Written by Amir Zabet @ 2014/05/13

    Usage: worldmap.plot(countries, values [, label] [, clim])
    """
    countries_shp = shpreader.natural_earth(resolution='110m', category='cultural',
                                            name='admin_0_countries')
    ## Create a plot
    fig = plt.figure()
    axe = plt.axes(projection=ccrs.PlateCarree())
    ## Create a colormap
    cmap = plt.cm.Blues
    if clim:
        vmin = clim[0]
        vmax = clim[1]
    else:
        val = values[np.isfinite(values)]
        mean = val.mean()
        std = val.std()
        vmin = mean-2*std
        vmax = mean+2*std
    norm = Normalize(vmin=vmin, vmax=vmax)
    smap = ScalarMappable(norm=norm, cmap=cmap)
    ax2 = fig.add_axes([0.3, 0.18, 0.4, 0.03])
    cbar = ColorbarBase(ax2, cmap=cmap, norm=norm, orientation='horizontal')
    cbar.set_label(label)
    ## Add countries to the map
    i = 0
    for country in shpreader.Reader(countries_shp).records():
        countrycode = country.attributes['adm0_a3']
        countryname = country.attributes['name_long']
        ## Check for country code consistency
        if countrycode == 'SDS': #South Sudan
            countrycode = 'SSD'
        elif countrycode == 'ROU': #Romania
            countrycode = 'ROM'
        elif countrycode == 'COD': #Dem. Rep. Congo
            countrycode = 'ZAR'
        elif countrycode == 'KOS': #Kosovo
            countrycode = 'KSV'
        if countrycode in countries:
            val = values[i]
            i += 1
            if np.isfinite(val):
                color = smap.to_rgba(val)
            else:
                color = 'grey'
        else:
            color = 'w'
            if verbose:
                print("No data available for "+countrycode+": "+countryname)
        axe.add_geometries(country.geometry, ccrs.PlateCarree(), facecolor=color, label=countryname)
    plt.savefig('ISRC_country_repartition.png')
    print_success("ISRC country repartition image saved")

def plot_isrc_country_repartition(isrc_filename):
    """Description of plot_isrc_country_repartition

    TODO Cartopy does not manage log value in axes scale: found a workaround
    """
    country = []
    with open('wikipedia-iso-country-codes.csv', 'r') as csvfile:
        country_code_reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in country_code_reader:
            country.append([row[1], row[2]])

    isrc = []
    isrc_file = open(isrc_filename, 'r')
    for line in isrc_file:
        isrc.append(line[:2])
    isrc_file.close()

    tmp = Counter(isrc)
    alpha3 = []
    country_count = []
    for (tmp_a2, tmp_a3) in country:
        if tmp[tmp_a2]:
            alpha3.append(tmp_a3)
            country_count.append(tmp[tmp_a2])

    country_count = np.array(country_count)
    # plot_worldmap(alpha3, country_count, clim=[0, max(country_count)])
    plot_worldmap(alpha3, country_count, clim=[0, 5000])

def plot_isrc_year_distribution(isrc_filename="ISRC_valid.txt"):
    """Description of plot_isrc_year_distribution

    Create a png image of the distribution of ISRCs over the years
    """
    years = []
    with open(isrc_filename, 'r') as csvfile:
        isrcs = csv.reader(csvfile)
        for isrc in isrcs:
            year = int(isrc[0][5:7]) + 2000
            if year > date.today().year:
                year -= 100
            years.append(year)

    axe = plt.subplot(111)
    plt.hist(years, bins=range(min(years), max(years) + 1, 1), color='grey')
    plt.xlabel("Years")
    plt.ylabel("Numbers of ISRCs")
    plt.xlim(min(years)-2, max(years)+2)
    axe.spines['top'].set_visible(False)
    axe.spines['right'].set_visible(False)
    axe.get_xaxis().tick_bottom()
    axe.get_yaxis().tick_left()
    plt.savefig('ISRC_year_distribution.png')
    print_success("ISRC year distribution image saved")

def abs_path_dir(dir_name):
    """Description of abs_path_dir

    Check validity of directory and return absolute path
    Otherwise raise error and end programm
    """
    if not os.path.isfile(dir_name) and os.path.exists(dir_name):
        return os.path.abspath(dir_name)
    else:
        print_error("Invalid directory name: " + dir_name)

def validate_isrc(isrc):
    """Description of validISRC

    Return True if isrc provided is valid, False otherwise
    TODOs
        Take into account ISO 3166-1 alpha 2 Code defined by
        http://isrc.ifpi.org/downloads/ISRC_Bulletin-2015-01.pdf
    """
    if len(isrc) == 12:
        pattern = re.compile("[a-zA-Z]{2}[a-zA-Z0-9]{3}[0-9]{7}")
        return pattern.match(isrc)
    else:
        return False

def validate_isrcs(input_file="isrc.txt", output_file="ISRC_invalid.txt", dir_input=None):
    """Description of validate_isrcs

    Validate a list of ISRCs contained into a file
    All line must only contain the ISRC and the \n
    """
    rm_input_file = False
    if dir_input:
        dir_input = abs_path_dir(dir_input)
        print_info("Directory to analyse: " + dir_input)
        input_file = "tmpISRCs.txt"
        os.system("ls " + dir_input + " > " + input_file)
        rm_input_file = True
    else:
        if os.path.isfile(input_file):
            input_file = os.path.abspath(input_file)
            print_info("Input File: " + input_file)
        else:
            print_error("Invalid input file")

    if not os.path.isfile(output_file):
        output_file = os.path.abspath(output_file)
    else:
        print_warning("Already existing output file will be overwritten")

    valid_isrcs = ""
    invalid_isrcs = ""
    cpt_invalid = 0
    isrc_file = open(input_file, "r")

    for line in isrc_file:
        if len(line) == 13 and validate_isrc(line[0:12]):
            valid_isrcs = valid_isrcs + line
        else:
            invalid_isrcs = invalid_isrcs + line
            cpt_invalid += 1

    isrc_file.close()

    if rm_input_file:
        os.remove(input_file)

    file_valid = open("ISRC_valid.txt", "w")
    file_valid.write(valid_isrcs)
    file_valid.close()

    if len(invalid_isrcs) != 0:
        print_warning(str(cpt_invalid) + " invalid ISRCs")
        file_invalid = open(output_file, "w")
        file_invalid.write(invalid_isrcs)
        file_invalid.close()
        print_info("Invalid ISRCs can be seen in: " + output_file)
    else:
        print_success("All ISRCs are valid")

if __name__ == "__main__":
    PARSER = argparse.ArgumentParser(description="Validate list of ISRCs")
    PARSER.add_argument(
        "-i",
        "--input_file",
        help="input file containing all ISRCs",
        type=str,
        default="isrc.txt",
        metavar="input_file")
    PARSER.add_argument(
        "-o",
        "--output_file",
        help="output file containing invalid ISRCs if any found",
        type=str,
        default="ISRC_invalid.txt",
        metavar="output_file")
    PARSER.add_argument(
        "-d",
        "--dir_input",
        help="input dir containing files with name corresponding to an ISRC",
        type=str,
        metavar="dir_input")

    validate_isrcs( \
        PARSER.parse_args().input_file, \
        PARSER.parse_args().output_file, \
        PARSER.parse_args().dir_input)
    plot_isrc_year_distribution()
    plot_isrc_country_repartition(PARSER.parse_args().input_file)
