'''
Python 3.x

This module sets up the working environment and provide global variables used in other modules.
All global variables are named in capital letters to prevent naming conflicts.
'''

import os
import logging

YEAR = [y for y in range(1,12)]
CATEGORY = os.listdir(os.path.join('..','ADE','Year1', 'External'))
OUTLET = ['drug', 'groc', 'MA']

TABLE = 'Sheet1'    # in any excel file, only the Sheet1 contains needed data
BRAND_COL = 'L5'    # all brands are listed under the column L5
UPC_COL = 'UPC'     # all upc numbers are listed under the column UPC

YEAR1 = {'beg': 1114, 'end': 1165}
YEAR6 = {'beg': 1374, 'end': 1426}

OUT_DIR = 'output'
LOG_DIR = 'log'
LOG_SEP = '\n<------------------>\n'

OUT_PATH = os.path.join(os.getcwd(), OUT_DIR)
LOG_PATH = os.path.join(os.getcwd(), LOG_DIR)

STUBS = 'parsed_stub_files'
STUBS2007 = 'parsed_stub_files2007'
STUBS2008 = 'parsed_stub_files2008-2011'

if not(os.path.exists(LOG_DIR)):
    os.makedirs(LOG_DIR)

if not(os.path.exists(OUT_DIR)):
    os.makedirs(OUT_DIR)

os.chdir(os.path.join('..','ADE'))

for root, dirs, files in os.walk(os.getcwd()):
	for oldname in files:
		oldpath = os.path.join(root, oldname)
		if oldname[-4:] == '.DAT':
			newname = oldname.replace('.DAT', '.dat')
			newpath = os.path.join(root, newname)
			os.rename(oldpath, newpath)
		if 'razor_' in oldname:
			newname = oldname.replace('razor_', 'razors_')
			newpath = os.path.join(root, newname)
			os.rename(oldpath, newpath)


# TODO: Fix this global logging mumbo jumbo
def start_logging(logfile):
    # create logfile according to the module
    logfile = os.path.join(LOG_PATH, logfile) # Log/logfile.txt
    log = open(logfile, 'w')
    log.close()
    logging.basicConfig(filename=logfile, level=logging.DEBUG, format=' %(asctime)s - %(levelname)s\n%(message)s' + LOG_SEP)

    # logging.disable(logging.CRITICAL)     # un-comment this line to disable logging
