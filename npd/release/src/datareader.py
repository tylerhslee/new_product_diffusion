'''
Python 3.x

This module provides the DataReader class, which is an instance created to retain data across different stores and years. Respective data can be accessed through its attributes at any point in main.py as long as the product category is the same.

Method fnctions used for concatenation are defined at the bottom.
'''

from gvar import *
import pandas as pd
import numpy as np
import os

class DataReader():

    # stores data to be concatenated as attributes
    # used to create combined data by category
    # directory tree:
    # | /
    # | +-- occurrence
    # |     +-- beer.csv
    # |     +-- blades.csv
    # |     +-- ...
    # | +-- sales
    # |     +-- ...
    # | +-- ...
    # each csv file contains data from all years (2001 - 2011)

    def __init__(self):

        # dictionary used to map brands and UPC numbers
        self.ref = {}

        # table of zeroes used for sales and unitp data
        self.sales_data = None
        self.units_data = None

        # lists used to concat respective data
        self.occ_list = []
        self.sales_list = []
        self.units_list = []
        self.panel_list = []


    def create_reference(self, cat, time):

        # use data from stub files to create brand - UPC mapping
        # only occurs on year 1, 7, and 8
        if time == 1:
            file_name = "prod_{}.xls".format(cat)
            file_path = os.path.join(STUBS, file_name)
        elif time == 7:
            file_name = "prod_{}.xlsx".format(cat)
            file_path = os.path.join(STUBS2007, file_name)
        elif time == 8:
            file_name = "prod11_{}.xlsx".format(cat)
            file_path = os.path.join(STUBS2008, file_name)
        else:
            return

        data = pd.ExcelFile(file_path).parse(TABLE)[[BRAND_COL, UPC_COL]]
        data = data[data[UPC_COL].isnull() == False]
        brands = list(data[BRAND_COL])
        upc_nums = list(map(lambda num: ''.join(num.split(sep='-')), data[UPC_COL]))

        for index, upc in enumerate(upc_nums):
            self.ref[upc] = brands[index]


    def create_zeroes(self, cat, time):

        if time < 8: self.target_dir = os.path.join('Year'+str(time), 'External', cat)
        else: self.target_dir = os.path.join('Year'+str(time), cat)

        # create a table with weeks in columns and brand names in indices
        # all values are initialized to 0.0
        # year 6 has 1 more week than any other years
        if time != 6:
            self.beg = YEAR1['beg'] + 52*(time - 1) + int(time/7)
            self.end = YEAR1['beg'] + 52*time -1 + int(time/7)
        else:
            self.beg = YEAR6['beg']
            self.end = YEAR6['end']

        brands = set(self.ref.values())
        weeks = [week for week in range(self.beg, self.end+1)]
        self.sales_data = pd.DataFrame(0.0, index=brands, columns=weeks)
        self.units_data = pd.DataFrame(0.0, index=brands, columns=weeks)


    def store_data(self, cat, time, store):

        # import data files that contain the respective store data
        print("\nImporting Year {} {} {} data...".format(time, cat, store))
        self.cat = cat
        self.time = time
        self.store = store

        if store != 'MA': target_file = '{}_{}_{}_{}'.format(cat, store, self.beg, self.end)
        else: target_file = '{}_PANEL_MA_{}_{}.dat'.format(cat, self.beg, self.end)

        target_path = os.path.join(self.target_dir, target_file)

        # check delimiter; always either comma or whitespace
        with open(target_path, 'r') as f:
            if ',' in f.readline():
                self.data = pd.read_csv(target_path)
            else:
                self.data = pd.read_csv(target_path, delim_whitespace=True)
        self.reformat_upc(self.data)

        
    def reformat_upc(self, data):

        # properly format the UPC numbers
        # they cannot have any symbols in them; e.g. 1-1-22 -> 1122
        if self.store != 'MA':
            print('Reformatting UPC Numbers... ', end='')
            data[UPC_COL] = data['SY'].apply('{:02d}'.format) + data['GE'].apply('{:02d}'.format) + data['VEND'].apply('{:05d}'.format) + data['ITEM'].apply('{:05d}'.format)
            data[BRAND_COL] = data[UPC_COL].apply(lambda upc: self.ref[upc])

        else:
            print('Reformatting UPC numbers... ', end='')
            data[UPC_COL] = data['COLUPC'].map(str).apply(lambda x: x[:-11].zfill(2) + x[-11].zfill(2) + x[-10:-5] + x[-5:])
            data[BRAND_COL] = data[UPC_COL].apply(lambda upc: self.ref[upc])
        print('Done')


    def export_data(self, data, data_type, file_name):

        # data_type parameter defines what kind of data is being exported
        # file_name is NOT the path to the file
        dest = os.path.join(OUT_PATH, data_type)
        if not(os.path.exists(dest)):
            os.makedirs(dest)
        file_path = os.path.join(dest, file_name)
        data.to_csv(file_path)

#------------------------------------------------------------------------------------------------

    # functions that go with helper functions (defined in helperfunc.py)
    # they take the respective list attribute from the instance and concat the DataFrames

    def occurrence(self):
        print('>> Combining OCC data... ', end = "")
        occ = pd.concat(self.occ_list)
        occ = occ.groupby(occ.index).max()
        print('Done')

        file_name = self.cat + '.csv'
        self.export_data(occ, 'occurrence', file_name)


    def sales(self):
        print('>> Combining SALES data... ', end='')
        self.total_sales = pd.concat(self.sales_list)
        self.total_sales = self.total_sales.groupby(self.total_sales.index).sum()
        print('Done')

        file_name = self.cat + '.csv'
        self.export_data(self.total_sales, 'total_sales', file_name)


    def units(self):

        # this function must be called AFTER self.sales()
        print('>> Combining UNITS data... ', end='')
        units = pd.concat(self.units_list)
        units = units.groupby(units.index).sum()
        print('Done')

        # total sales / units = unit price
        print('>> Computing UNIT PRICE... ', end='')
        unitp = self.total_sales
        unitp /= units
        unitp.round(2)
        print('Done')

        file_name = self.cat + '.csv'
        self.export_data(unitp, 'unit_price', file_name)


    def panels(self):

        # combine data in self.panel_list into one huge table
        print('>> Combining PANEL data... ', end='')
        panels = pd.concat(self.panel_list)
        file_name = self.cat + '.csv'
        self.export_data(panels, 'agg_panel_data', file_name)