import numpy as np
import csv
import argparse
import pickle
import os

''' ssp_preprocess_landwaterstorage.py

Code generated 17-09-2019, by Tim Hermans

This script runs the land water storage pre-processing task for the SSP LWS workflow. 
This task generates the data and variables needed to configure the LWS submodel.

Parameters:
scen 				The RCP or SSP scenario (default: RCP85) 
dotriangular        Logical 0 or 1, to use triangular distribution for gwd [1,1]
includepokhrel      Logical 0 or 1, to include Pokhrel data for gwd [1,1] 

Output:
"ssp_landwaterstorage_data.pkl" = Contains the LWS data
"ssp_landwaterstorage_config.pkl" = Contains the configuration parameters

'''

def ssp_preprocess_landwaterstorage(scen, dotriangular, includepokhrel):
	
	##################################################
	# configure run (could be separate script)
	dgwd_dt_dpop_pcterr = .25       # error on gwd slope
	dam_pcterr = .25                # error on sigmoidal function reservoirs
	yrs = np.linspace(2010,2100,10) # target years projections

	# paths to data
	datadir = os.path.dirname(__file__)
	pophistfile     = 'UNWPP2012 population historical.csv'
	reservoirfile   = 'Chao2008 groundwater impoundment.csv'
	gwdfiles        = ['Konikow2011 GWD.csv','Wada2012 GWD.csv','Pokhrel2012 GWD.csv']
	popscenfile     = 'ssp_iam_baseline_popscenarios2100.csv'    

	if len(gwdfiles) != 3:
		dotriangular=0

	##################################################
	# read population history .csv file
	pophistfile = os.path.join(datadir, pophistfile)
	with open(pophistfile,'rU') as csvfile:
	   	popdata = csv.reader(csvfile)
		row_count = sum(1 for row in popdata)

	with open(pophistfile,'rU') as csvfile:
		popdata = csv.reader(csvfile)
		first_row = next(popdata)
		i = 0
		t = np.zeros(row_count-1)
		pop=np.zeros(row_count-1)

		for row in popdata:
			t[i] = row[0]   # store years
			pop[i] = row[1] # store population
			i += 1

	t0 = t
	pop0 = pop

	# sample with 5 year steps
	t = t[::5]
	pop = pop[::5]

	##################################################
	# read reservoir impoundment .csv file
	reservoirfile = os.path.join(datadir, reservoirfile)
	with open(reservoirfile,'rU') as csvfile:
		damdata = csv.reader(csvfile)
		row_count = sum(1 for row in damdata)

	with open(reservoirfile,'rU') as csvfile:
		damdata = csv.reader(csvfile)
		first_row = next(damdata)
		i = 0
		tdams = dams=np.zeros(row_count-1)
		dams=np.zeros(row_count-1) 
    
		for row in damdata:
			tdams[i] = row[0]   # store years
			dams[i] = row[1]    # store reservoir impoundment
			i += 1

	##################################################
	# read groundwater depletion .csv files
	
	# Define function to count lines in a .csv file
	def countlines(f):
		with open(f,'rU') as csvfile:
			gwddata = csv.reader(csvfile)
			row_count = sum(1 for row in gwddata)
		return(row_count)
	
	# Count the lines in all the GWD files
	gwdfiles_full = [os.path.join(datadir, f) for f in gwdfiles]
	nlines = [countlines(f) for f in gwdfiles_full]
	
	# Initialize a multi-dimensional array to store GWD data
	gwd = np.full((len(gwdfiles_full), np.max(nlines)), np.nan)
	tgwd = np.full((len(gwdfiles_full), np.max(nlines)), np.nan)
	
	for j in np.arange(0,2+includepokhrel): # for different datasets
		path = gwdfiles_full[j]
		with open(path,'rU') as csvfile:
			gwddata = csv.reader(csvfile)
			first_row = next(gwddata)
			i = 0
    
			for row in gwddata:
				tgwd[j,i] = row[0] # store years
				gwd[j,i] = row[1] # store gwd
				i += 1
	
	##################################################
	# read population scenarios .csv file
	popscenfile = os.path.join(datadir, popscenfile)
	with open(popscenfile,'rU') as csvfile:
		popdata = csv.reader(csvfile)
		row_count = sum(1 for row in popdata)

	with open(popscenfile,'rU') as csvfile:
		popdata = csv.reader(csvfile)
		first_row = next(popdata)
		i = 0
		popscenyr = np.zeros(row_count-1)
		popscen   = np.zeros([row_count-1,5]) # 5 SSPs
    
		for row in popdata:
			popscenyr[i] = row[0] # store years
			popscen[i,:] = row[1:6] # store population projections
			i += 1
    
    ###################################################
    # Store the data in a pickle
	output = {'t': t, 'pop': pop, 'tdams': tdams, 'dams': dams,\
				'tgwd': tgwd, 'gwd': gwd, 'popscen': popscen, 'popscenyr': popscenyr}
	
	# Write the data to a file
	outdir = os.path.dirname(__file__)
	outfile = open(os.path.join(outdir, "ssp_landwaterstorage_data.pkl"), 'wb')
	pickle.dump(output, outfile)
	outfile.close()
	
	# Store the configuration in a pickle
	output = {'dgwd_dt_dpop_pcterr': dgwd_dt_dpop_pcterr, 'dam_pcterr': dam_pcterr,\
				'yrs': yrs, 'scen': scen, 'dotriangular': dotriangular,\
				'includepokhrel': includepokhrel,'pop0': pop0, 't0':t0}
	
	# Write the data to a file
	outdir = os.path.dirname(__file__)
	outfile = open(os.path.join(outdir, "ssp_landwaterstorage_config.pkl"), 'wb')
	pickle.dump(output, outfile)
	outfile.close()


if __name__ == '__main__':
	
	# Initialize the command-line argument parser
	parser = argparse.ArgumentParser(description="Run the land water storage pre-processing stage for the SSP LWS SLR projection workflow",\
	epilog="Note: This is meant to be run as part of the SSP LWS module within the Framework for the Assessment of Changes To Sea-level (FACTS)")
	
	# Define the command line arguments to be expected
	parser.add_argument('--scen', help="Use RCP or SSP scenario[default=RCP85]", choices=["RCP19","RCP26","RCP45","RCP70","RCP85","SSP1","SSP2","SSP3","SSP4","SSP5"], default="RCP85")
	parser.add_argument('--dotriangular', help="Use triangular distribution for GWD [default=0]", choices=[0, 1], default=0)
	parser.add_argument('--includepokherl', help="Include Pokherl data for GWD [default=0]", choices=[0, 1], default=0)

	# Parse the arguments
	args = parser.parse_args()
	
	# Run the preprocessing stage with the provided arguments
	ssp_preprocess_landwaterstorage(args.scen, args.dotriangular, args.includepokherl)
	
	exit()