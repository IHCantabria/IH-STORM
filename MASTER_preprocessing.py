# -*- coding: utf-8 -*-
"""
This module is part of the STORM model

For more information, please see 
Bloemendaal, N., Haigh, I.D., de Moel, H. et al. 
Generation of a global synthetic tropical cyclone hazard dataset using STORM. 
Sci Data 7, 40 (2020). https://doi.org/10.1038/s41597-020-0381-2

This is the master program for the data pre-processing. 
This script is made for the data pre-processing of the IBTrACS dataset. For other input datasets, 
please change the syntax accordingly. 
This script will generate multiple output files in the working directory. 

The script is split up in multiple cells, with each cell running a specific part of the data
preprocessing. We advise you to read what is done per cell, and to run per cell rather than
the whole script at once. To keep the script as clean as possible, most of the code has been placed in 
seperate functions in the "preprocessing"-module. 
 
Copyright (C) 2020 Nadia Bloemendaal. All versions released under GNU General Public License v3.0
"""
import xarray as xr
import preprocessing
import coefficients
import environmental
import genesis_matrix
import os
import sys
import import_data
import numpy as np
dir_path=os.path.dirname(os.path.realpath(sys.argv[0]))
__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))

 
#period,climate_index,threshold, idx_basin, months,mpi_bounds=import_data.input_data('input.dat')
# Print the loaded variables
#print("period:", period)
#print("climate_index:", climate_index)
#print("threshold:", threshold)
#print("idx_basin:", idx_basin)
#print("months:", months)
#print("mpi_bounds:", mpi_bounds)

#=======================================================================================================
# CHANGE IT AT YOUR CONVIENIENCE IN THE INPUT FILE
period=[1980,2021]
## basins=['EP','NA','NI','SI','SP','WP']
idx_basin=[0,1,2,3,4,5] # Index for the basin vector
months=[[6,7,8,9,10,11],[6,7,8,9,10,11],[4,5,6,9,10,11],[1,2,3,4,11,12],[1,2,3,4,11,12],[5,6,7,8,9,10,11]]
mpi_bounds=[[860,880,900,900,880,860],[920,900,900,900,880,880],[840,860,880,900,880,860],[840,880,860,860,840,860],[840,840,860,860,840,840],[860,860,860,870,870,860,860]]
months_for_coef_MPI=[[6,7,8,9,10,10],[6,7,8,9,10,11],[6,6,6,10,10,11],[1,2,3,4,11,12],[1,2,3,4,11,12],[5,6,7,8,9,10,11]]
months_for_coef_PRESS=[[6,7,8,9,10,11],[6,7,8,9,10,11],[4,5,6,10,10,11],[1,2,3,4,11,12],[1,2,3,4,11,12],[5,6,7,8,9,10,11]]

months=[[6,7,8,9,10,11],[6,7,8,9,10,11],[10,11],[1,2,3,4,11,12],[1,2,3,4,11,12],[5,6,7,8,9,10,11]]
mpi_bounds=[[860,880,900,900,880,860],[920,900,900,900,880,880],[880,860],[840,880,860,860,840,860],[840,840,860,860,840,840],[860,860,860,870,870,860,860]]
months_for_coef_MPI=[[6,7,8,9,10,10],[6,7,8,9,10,11],[10,11],[1,2,3,4,11,12],[1,2,3,4,11,12],[5,6,7,8,9,10,11]]
months_for_coef_PRESS=[[6,7,8,9,10,11],[6,7,8,9,10,11],[10,11],[1,2,3,4,11,12],[1,2,3,4,11,12],[5,6,7,8,9,10,11]]


#threshold='0.5'
#climate_index='None'
#=======================================================================================================

TC_file='IBTrACS.'+str(period[0])+'_'+str(period[1])+'v04r00.nc'

#%%
"""
Open the IBTrACS dataset. The IBTrACS dataset can be downloaded via https://www.ncdc.noaa.gov/ibtracs/
or ftp://eclipse.ncdc.noaa.gov/pub/ibtracs/v04r00/provisional/netcdf/ 
Here, we use the global dataset (version 4) from 1980-2017.
"""

print('********************************')
data=xr.open_dataset(os.path.join(__location__,TC_file),decode_times=False)

# select the number of years for each basin 
df1 = data.to_dataframe()
df1 = df1[['lat', 'lon', 'sid', 'season', 'number', 'basin', 'subbasin', 'name', 'iso_time', 'wmo_wind', 'wmo_pres','track_type', 'main_track_sid', 'dist2land', 'landfall','usa_sshs','usa_rmw']]


df1['wmo_wind']=df1['wmo_wind']*0.51444444 
df1=df1[df1['wmo_wind']>=18]

df=df1[df1['basin']==b'EP']
nyear0=len(np.unique(df['season'].values))

df=df1[df1['basin']==b'NA']
nyear1=len(np.unique(df['season'].values))

df=df1[df1['basin']==b'NI']
nyear2=len(np.unique(df['season'].values))

df=df1[df1['basin']==b'SI']
nyear3=len(np.unique(df['season'].values))

df=df1[df1['basin']==b'SP']
nyear4=len(np.unique(df['season'].values))

df=df1[df1['basin']==b'WP']
nyear5=len(np.unique(df['season'].values))

years= np.unique(data.season.values)
nyear=[nyear0,nyear1,nyear2,nyear3,nyear4,nyear5]
period=[years[0],years[-1]]
print('number of years: ',int(len(years)), 'from',period[0],'to',period[1])

preprocessing.extract_data(data, period[1])
data.close()
print('extract_data done')
#%%
"""
Extract the important parameters necessary for the fitting of the regression formulas (and other parts
of the storm model
"""

print('********************************')
preprocessing.TC_variables(nyear,months)
print('TC_variables done')
#%%
"""
Calculate the coefficients for the track and pressure regression formulas
"""

print('********************************')
coefficients.track_coefficients()
print('track_coefficients done')
#%%
"""
Calculate the monthly mean SST and MSLP fields
ECMWF has monthly mean MSLP fields available via the CDS (cds.climate.copernicus.eu)
These should be downloaded and stored as "Monthly_mean_MSLP.nc" and "Monthly_mean_SST.nc"
"""

print('********************************')
   
data=xr.open_dataset(os.path.join(__location__,'Monthly_mean_MSLP.nc'))
# if data has 4th dimensions, uncomment it
# data = data.isel(expver=0) # to remove 4th dimension
# data = data.drop('expver') # to remove 4th dimension
environmental.monthly_mean_pressure(data)
data.close()
print('monthly_mean_pressure done')

print('********************************')
data=xr.open_dataset(os.path.join(__location__,'Monthly_mean_SST.nc'))
# if data has 4th dimensions, uncomment it
#data = data.isel(expver=0) # to remove 4th dimension
#data = data.drop('expver') # to remove 4th dimension
environmental.monthly_mean_sst(data)
data.close()
print('monthly_mean_sst done')

print('********************************')
environmental.wind_pressure_relationship(idx_basin,months)
print('wind_pressure_relationship done')

print('********************************')
environmental.calculate_MPI_fields(idx_basin,months,months_for_coef_MPI,mpi_bounds)
print('calculate_MPI_fields done')

print('********************************')
environmental.pressure_coefficients(idx_basin,months,months_for_coef_PRESS)
print('pressure_coefficients done')

print('********************************')
genesis_matrix.Change_genesis_locations(idx_basin,months)
print('genesis_matrix done')

