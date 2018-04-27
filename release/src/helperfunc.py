'''
Python 3.x

This module provides helper functions to be used in main.py to perform individual level data manipulation. These data is stored in DataReader instance as one of its attributes, and later are concatenated though its method functions.
'''
from gvar import BRAND_COL, CATEGORY
import pandas as pd
import os

WEEK_COL = 'WEEK'
TOT_SALE_COL = 'DOLLARS'
SOLD_UNITS_COL = 'UNITS'

# load prompt to save some time
def load():
    invalid = 1
    while invalid == 1:
        prompt = input('Start from the beginning? Y/N  ')
        if prompt.upper() == 'Y':
            invalid = 0
            start = 0
        elif prompt.upper() == 'N':
            while invalid == 1:
                prompt2 = input('Category to start from: ')
                try:
		    start = CATEGORY.index(prompt2.lower())
                except ValueError:
                    print(prompt2 + ' is not a valid category.')
                    continue
                else: invalid = 0
        else:
            print('That is not a valid input.')
    return start


def occurrence(inst):
	# should be called under the OUTLET loop
	# takes occ_data for each store and appends it to inst.occ_list
	print('>> Gathering OCC data... ', end = "")
	occ_data = inst.data[[BRAND_COL, WEEK_COL]]
	inst.occ_list.append(pd.get_dummies(occ_data.set_index(BRAND_COL)[WEEK_COL]).groupby(level=0).max())
	print('Done')


def sales(inst):
	# should be called under the OUTLET loop
	# adds sales amount to inst.sales_data
	print('>> Gathering SALES data...', end = " ")
	init_data = inst.data[[BRAND_COL,WEEK_COL,TOT_SALE_COL]].groupby([BRAND_COL,WEEK_COL]).sum()
	brands = list(init_data.index.get_level_values(BRAND_COL))
	weeks = list(init_data.index.get_level_values(WEEK_COL))

	row_indexers = [inst.sales_data.index.get_loc(r) for r in brands]
	col_indexers = [inst.sales_data.columns.get_loc(c) for c in weeks]
	dollars = list(init_data[TOT_SALE_COL])

	inst.sales_data.values[row_indexers,col_indexers] += dollars
	print('Done')


def units(inst):
	# operates similarly to sales()
	print('>> Gathering UNITS data... ', end='')
	init_data = inst.data[[BRAND_COL, WEEK_COL, SOLD_UNITS_COL]].groupby([BRAND_COL, WEEK_COL]).sum()
	brands = list(init_data.index.get_level_values(BRAND_COL))
	weeks = list(init_data.index.get_level_values(WEEK_COL))

	row_indexers = [inst.units_data.index.get_loc(r) for r in brands]
	col_indexers = [inst.units_data.columns.get_loc(c) for c in weeks]
	units = list(init_data[SOLD_UNITS_COL])

	inst.units_data.values[row_indexers,col_indexers] += units
	print('Done')


def panels(inst):
	# imports _PANEL_ data and appends it to inst.panel_list
	print('>> Gathering PANEL data... ', end='')
	target_dir = inst.target_dir
	files_to_concat = [os.path.join(target_dir, name) for name in os.listdir(target_dir) if '_PANEL_' in name]
	data_to_concat = []

	for file in files_to_concat:
		with open(file, 'r') as f:
			header = f.readline()

			# check if comma- or whitespace-delimited
			if ',' in header:
				try: data_to_concat.append(pd.read_csv(file, index_col=0))
				except pd.io.common.EmptyDataError: continue
			
			else:
				try: data_to_concat.append(pd.read_csv(file, index_col=0, delim_whitespace=True))
				except pd.io.common.EmptyDataError: continue

	# return an aggragate data of the same year and category
	panel_data = pd.concat(data_to_concat)
	inst.panel_list.append(panel_data)
	print('Done')
