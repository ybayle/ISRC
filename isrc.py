#!/usr/bin/python
#
# Author    Yann Bayle
# E-mail    bayle.yann@live.fr
# License   MIT
# Created   25/05/2016
# Updated   31/10/2016
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
import matplotlib as mpl
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.io.shapereader as shpreader

def plot_isrc_country_repartition(isrc_filename="ISRC_valid.txt"):
    """Description of plot_isrc_country_repartition
    """
    # Gather countries' name along ISO-2 codes
    countries = {}
    with open('wikipedia-iso-country-codes.csv', 'r') as csvfile:
        codes = csv.reader(csvfile, delimiter=',', quotechar='"')
        for row in codes:
            countries[row[0]] = row[1]
    # Map nb of ISRCs with a color for each country
    colors = {}
    with open(isrc_filename, "r") as filep:
        for row in filep:
            country_code = row[0:2]
            if country_code in colors:
                colors[country_code] += 1
            else:
                colors[country_code] = 1
    countries_shp = shpreader.natural_earth(
        resolution='110m',
        category='cultural',
        name='admin_0_countries')
    fig, axe = plt.subplots(
        figsize=(12, 6),
        subplot_kw={'projection': ccrs.PlateCarree()})

    norm = mpl.colors.Normalize(vmin=0, vmax=float(max(list(colors.values()))))
    cmap = plt.cm.YlOrBr # or YlGnBu

    for country in shpreader.Reader(countries_shp).records():
        country_name = country.attributes['name_long']
        if country_name in countries:
            country_iso2 = countries[country_name]
            if country_iso2 in colors:
                color = colors[country_iso2]
            else:
                color = -1
        else:
            color = -1
        axe.add_geometries(
            country.geometry,
            ccrs.PlateCarree(),
            facecolor=cmap(norm(color)),
            label=country_name)
    cax = fig.add_axes([0.91, 0.2, 0.02, 0.6])
    mpl.colorbar.ColorbarBase(cax, cmap=cmap, norm=norm)
    plt.savefig('ISRC_country_repartition.png')
    print("ISRC country repartition image saved")

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
    hist_bins_range = range(min(years), max(years) + 1, 1)
    plt.hist(years, bins=hist_bins_range, color='grey')
    plt.xlabel("Years")
    plt.ylabel("Numbers of ISRCs")
    plt.xlim(min(years)-2, max(years)+2)
    axe.spines['top'].set_visible(False)
    axe.spines['right'].set_visible(False)
    axe.get_xaxis().tick_bottom()
    axe.get_yaxis().tick_left()
    plt.savefig('ISRC_year_distribution.png')
    print("ISRC year distribution image saved")

def abs_path_dir(dir_name):
    """Description of abs_path_dir

    Check validity of directory and return absolute path
    Otherwise raise error and end programm
    """
    if not os.path.isfile(dir_name) and os.path.exists(dir_name):
        return os.path.abspath(dir_name)
    else:
        print("Invalid directory name: " + dir_name)
        sys.exit()

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

def validate_isrcs(infile="isrc.txt", outfile="ISRC_invalid.txt", indir=None):
    """Description of validate_isrcs

    Validate a list of ISRCs contained into a file
    All line must only contain the ISRC and the \n
    """
    rm_infile = False
    if indir:
        indir = abs_path_dir(indir)
        print("Directory to analyse: " + indir)
        infile = "tmpISRCs.txt"
        os.system("ls " + indir + " > " + infile)
        rm_infile = True
    else:
        if os.path.isfile(infile):
            infile = os.path.abspath(infile)
        else:
            print("Invalid input file")
            sys.exit()
    if not os.path.isfile(outfile):
        outfile = os.path.abspath(outfile)
    else:
        print("Already existing output file will be overwritten")

    valid_isrcs = ""
    invalid_isrcs = ""
    cpt_invalid = 0
    isrc_file = open(infile, "r")

    for index, line in enumerate(isrc_file):
        isrc = line[0:12]
        print("\t" + str(index) + "\t" + isrc)
        sys.stdout.write("\033[F") # Cursor up one line
        # sys.stdout.write("\033[K") # Clear line
        # if len(line) == 13 and validate_isrc(line[0:12]):
        if validate_isrc(isrc):
            valid_isrcs = valid_isrcs + isrc + "\n"
        else:
            invalid_isrcs = invalid_isrcs + isrc + "\n"
            cpt_invalid += 1
    sys.stdout.write("\033[K") # Clear line

    isrc_file.close()

    if rm_infile:
        os.remove(infile)

    file_valid = open("ISRC_valid.txt", "w")
    file_valid.write(valid_isrcs)
    file_valid.close()

    if len(invalid_isrcs) != 0:
        print(str(cpt_invalid) + " invalid ISRCs stored in: " + outfile)
        file_invalid = open(outfile, "w")
        file_invalid.write(invalid_isrcs)
        file_invalid.close()
    else:
        print("All ISRCs are valid")

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
        "--outfile",
        help="output file containing invalid ISRCs if any found",
        type=str,
        default="ISRC_invalid.txt",
        metavar="outfile")
    PARSER.add_argument(
        "-d",
        "--dir_input",
        help="input dir containing files with name corresponding to an ISRC",
        type=str,
        metavar="dir_input")

    validate_isrcs( \
        PARSER.parse_args().input_file, \
        PARSER.parse_args().outfile, \
        PARSER.parse_args().dir_input)
    plot_isrc_year_distribution()
    plot_isrc_country_repartition()
