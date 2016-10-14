#ISRC

Set of functions to validate, manage and display ISRC as defined by
http://isrc.ifpi.org/en/isrc-standard/code-syntax

###Details

- Author  Yann Bayle
- E-mail  bayle.yann@live.fr
- License MIT
- Created 25/05/2016
- Updated 14/10/2016
- Version 1.0.0

###Installation

Nothing to install

###Dependencies

- cartopy 
- matplotlib 
- numpy

###Files

####isrc.py
Main and unique python file containing all functions

####isrc.txt
An example file containing a real list of both valid and invalid ISRCs.

###Functions available

- Validates an ISRC
- Validates a list of ISRCs and indicates the corrupted ones
- Plot an histogram of year repartition of a list of ISRCs
- Plot country repartition of ISRC on a color globe

###Examples

- python isrc.py
- python isrc.py -i /path/isrc.txt -o /path/invalid_ISRCs.txt
- python isrc.py -d /path/dir/

###Notes

Code validated by https://www.pylint.org/
