# -*- coding: utf-8 -*-
"""
This module is part of the IH-STORM model

Functions described here are part of the data pre-processing. 

Copyright (C) 2024 Itxaso Odériz. 
"""


import numpy as np

def input_data(file):
    # Load data from the .dat file
    data = np.genfromtxt(file, delimiter='=', dtype=str)

    # Convert data to a dictionary
    variables = dict(data)

    # Convert specific variables to their appropriate types
    period = list(map(int, variables['period'][1:-1].split(',')))
    climate_index = variables['climate_index'].strip("'")
    threshold = float(variables['threshold'])
    idx_basin = list(map(int, variables['idx_basin'][1:-1].split(',')))
    months = [list(map(int, m.strip('[]').split(','))) for m in variables['months'].split('],')]
    mpi_bounds = [list(map(int, b.strip('[]').split(','))) for b in variables['mpi_bounds'].split('],')]
    months_for_coef_MPI = [list(map(int, b.strip('[]').split(','))) for b in variables['mpi_bounds'].split('],')]
    months_for_coef_PRESS = [list(map(int, b.strip('[]').split(','))) for b in variables['mpi_bounds'].split('],')]

    return period,climate_index,threshold, idx_basin, months,mpi_bounds,months_for_coef_MPI,months_for_coef_PRESS