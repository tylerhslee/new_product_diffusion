'''
Python 3.x

This module executes main() function that performs everything.
First create the instance of DataReader, then use its methods and other helper function to achieve desired functionalities.
'''


# define magic literals
INITIAL_PROGRESS = 0
PROGRESS_INCREMENT = 1
SUCCESS_CODE = 0

#------------------------------------------------------------------------------------------------

from progressbar import ProgressBar, UnknownLength

def update_pbar(pbar, progress):
	progress += PROGRESS_INCREMENT
	pbar.update(progress)

	return pbar, progress

#------------------------------------------------------------------------------------------------

from gvar import YEAR, CATEGORY, OUTLET, start_logging
from datareader import DataReader
from helperfunc import *
import logging

LOG_FILE = 'test_log.txt'
start_logging(LOG_FILE)

#------------------------------------------------------------------------------------------------

def final_product(inst, cat):

	print("\nFinalizing {} data for Year 2001 through 2011...".format(cat))

	# run instance methods that concatenate approrpriate data
	inst.occurrence()
	inst.sales()
	inst.units()
	inst.panels()

#------------------------------------------------------------------------------------------------

def main(start):

	file_count = len(CATEGORY[start:]) * len(YEAR) * len(OUTLET)
	pbar = ProgressBar(max_value=file_count, redirect_stdout=True)
	progress = INITIAL_PROGRESS

	for cat in CATEGORY[start:]:

		# instance of DataReader that will retain all necessary data for categorical manipulation
		by_category = DataReader()

		for time in YEAR:
			by_category.create_reference(cat, time)
			by_category.create_zeroes(cat, time)

			for store in OUTLET:

				# import relevant data for the given category, year, and store
				by_category.store_data(cat, time, store)
	 
				# append individual occ_data to by_category.occ_list
				occurrence(by_category)

				# update by_category.sales_data with sales data
				sales(by_category)

				# update by_category.unitp_data with units data
				units(by_category)

				# append total purchase data (panel) to by_category.panel_list
				panels(by_category)

				# at the very end, update progress bar
				pbar, progress = update_pbar(pbar, progress)

			# append completed sales data to by_category.sales_list
			by_category.sales_list.append(by_category.sales_data)

			# append completed units data to by_category.units_list
			by_category.units_list.append(by_category.units_data)

		# concat all DataFrames and export the final product
		final_product(by_category, cat)

	return SUCCESS_CODE

#------------------------------------------------------------------------------------------------

if __name__ == '__main__':
	start = load()
	exit_code = main(start)
	if exit_code == SUCCESS_CODE:
		print("Successful")
