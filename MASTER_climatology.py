# -*- coding: utf-8 -*-
"""
This module is part of the IH-STORM model

Functions described here are part of the data pre-processing. 

Copyright (C) 2024 Itxaso Odériz. 
"""

import xarray as xr
import preprocessing
import coefficients
import environmental
import genesis_matrix
import os
import sys
import import_data
import climatology
import numpy as np

# input variables read from input.dat=======================================================================================================
#period: an array including initial and final year
#climate_index: is an climate index, for none climate index use 'none'
#threshold: is the value of the climate index to select a positive or negative phase, for exmaple with ONI, the thresold for EL Niño is +0.5, while for la Niña is -0.5
#idx_basin: id refere to each basin 
            # 0 = EP = Eastern Pacific
            # 1 = NA = North Atlantic
            # 2 = NI = North Indian
            # 3 = SI = South Indian
            # 4 = SP = South Pacific
            # 5 = WP = Western Pacific
#months: months of each season per basin
#mpi_bounds:the lowest mpi values per basin and serve as the lower bound, derived from Bister & Emanuel 2002
#=======================================================================================================

dir_path=os.path.dirname(os.path.realpath(sys.argv[0]))
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

period,climate_index,threshold, idx_basin, months,mpi_bounds,months_for_coef_MPI,months_for_coef_PRESS=import_data.input_data('input.dat')
# Print the loaded variables
print("period:", period)
print("climate_index:", climate_index)
print("threshold:", threshold)
print("idx_basin:", idx_basin)
print("months:", months)
print("mpi_bounds:", mpi_bounds)


#=======================================================================================================

if climate_index!='none':
    climatology.climatology_data(period)
else:
    climatology.climatology_data_cliamte_index(climate_index,period,threshold)