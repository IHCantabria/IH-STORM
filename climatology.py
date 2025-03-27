# -*- coding: utf-8 -*-
"""
@author: Itxaso Oderiz, itxaso.oderiz@unican.es

Climatalogy's cyclone to execute STORM
This programs select STORM data (cyclones, SST, SLP) for different climatology periods


Copyright (C) 2023 Itxaso Odériz
"""

import xarray as xr
import requests
import os
import os.path as op
import cdsapi
import pandas as pd
import numpy as np



def get_IBStrack(url,local_path,file_name):
    # Specify the local file path where you want to save the downloaded file
    local_file_path = local_path+file_name
    
    # Send an HTTP GET request to the URL
    response = requests.get(url+file_name)
    
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open the local file in binary write mode and write the content of the response to it
        with open(local_file_path, 'wb') as file:
            file.write(response.content)
        print(f"File '{url}' downloaded successfully.")
    else:
        print(f"Failed to download file. Status code: {response.status_code}")
        
#==============================================================================
# Function to get climate index 
#==============================================================================       
        
def get_climate_index(url,local_path):
   
    # select the index from https://psl.noaa.gov/data/climateindices/list/ 
    # Send an HTTP GET request to the URL
    response = requests.get(url)
    data = response.text
    lines = data.split('\n')
    #delete the first row
    lines = lines[1:] 
    # create empty arrays and DataFRame 
    climate_index0 = pd.DataFrame();YEAR=[];MONTH=[];CLIMATE_INDEX=[]
    # Iterate over the lines and extract the year, month and climate index values
    for line in lines:
        # print(line)
        if line.strip():
            try:
                parts = line.split()
                values = [float(x) for x in parts[1:]]
                year = np.array([int(parts[0])] * 12)
                month  = np.array(range(1,13))
                climate_index= np.array(values)
                YEAR.append(year)
                MONTH.append(month)
                CLIMATE_INDEX.append(climate_index)
            except: 
                continue
    climate_index0['year'] = np.concatenate(YEAR)
    climate_index0['month']  =  np.concatenate(MONTH)
    climate_index0['climate_index']= np.concatenate(CLIMATE_INDEX) 
    # delete non registered values -999
    climate_index0 = climate_index0[climate_index0['climate_index'] != -999]
    climate_index0 = climate_index0[climate_index0['climate_index'] != -99]
    climate_index0.to_csv(local_path+'/climate_index.csv')
    print(f"File '{url}' downloaded successfully.")
    
#==============================================================================
# Function to get SLP from ERA5 
#==============================================================================   

def download_monthly_mean_SLP(dir_data,year_list):
    # change years accorign to the slide period
    c = cdsapi.Client()
    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'format': 'netcdf',
            'product_type': 'monthly_averaged_reanalysis',
            'variable': 'mean_sea_level_pressure',
            'year': year_list,
            'month': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
            ],
            'time': '00:00',
        },
        op.join(dir_data,'Monthly_mean_MSLP.nc'))


#==============================================================================
# Function to get SST from ERA5 
#==============================================================================  

def download_monthly_mean_SST(dir_data,year_list):
    c = cdsapi.Client()
    c.retrieve(
        'reanalysis-era5-single-levels-monthly-means',
        {
            'format': 'netcdf',
            'product_type': 'monthly_averaged_reanalysis',
            'variable': 'sea_surface_temperature',
            'year': year_list,
            'month': [
                '01', '02', '03',
                '04', '05', '06',
                '07', '08', '09',
                '10', '11', '12',
            ],
            'time': '00:00',
        },
        op.join(dir_data,'Monthly_mean_SST.nc'))
        
        
        
def climatology_data(year):
        
        
    #identifying local path (where this code is located)
    local_path= os.getcwd()
    year_list = [str(year) for year in range(year[0], year[1] + 1)]


    download_monthly_mean_SLP(local_path,year_list)
    download_monthly_mean_SST(local_path,year_list)

    # download data from IBTrACS
    file_name='/IBTrACS.ALL.v04r00.nc'
    get_IBStrack('https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/netcdf/',local_path,file_name)

    # open file of IBStrack
    cyclones=xr.open_dataset(local_path+file_name)
    filtered_cyclones = cyclones.where(cyclones.season >= year[0], drop=True)
    filtered_cyclones = filtered_cyclones.where(filtered_cyclones.season <= year[1], drop=True)
    filtered_cyclones.to_netcdf(local_path+'/IBTrACS.'+str(year[0])+'_'+str(year[1])+'v04r00.nc')

    # Download of climate index
    get_climate_index('https://psl.noaa.gov/data/correlation/tna.data',local_path)
    
    
    
    
    
    
def climatology_data_cliamte_index (climate_index,year,threshold):
    # identifying local path (where this code is located)
    local_path= os.getcwd()

    # geratin a list of the years of interest
    year_list = [str(year) for year in range(year[0], year[1] + 1)]

    #==============================================================================
    # Download data  
    # UNCOMMENT IF DATASET IS IN THE LOCAL PATH
    #==============================================================================  
    # Download SLP for the range of years (this step can be omitted if data are in a local path)
    #download_monthly_mean_SLP(local_path,year_list)

    # Download SSST for the range of years(this step can be omitted if data are in a local path)
    #download_monthly_mean_SST(local_path,year_list)

    # Download data from IBTrACS (this step can be omitted if data are in a local path)
    file_name='/IBTrACS.ALL.v04r00.nc'
    get_IBStrack('https://www.ncei.noaa.gov/data/international-best-track-archive-for-climate-stewardship-ibtracs/v04r00/access/netcdf/',local_path,file_name)

    #====================================================================
    #  CLIMATE INDEX
    # Selects data of SLP, SST storms for specific months and years coinciding with a climate index 
    #==============================================================================  

    # Download of climate index
    get_climate_index('https://psl.noaa.gov/data/correlation/'+climate_index+'.data',local_path)

    # Filter data for specific years and phase
    climate_index=pd.read_csv(local_path+'/climate_index.csv')

    if threshold>=0:
        climate_index=climate_index[climate_index['climate_index']>=threshold] 
    elif threshold<0:
        climate_index=climate_index[climate_index['climate_index']<=threshold] 

    climate_index=climate_index[climate_index['year']>=year[0]] 
    climate_index=climate_index[climate_index['year']<=year[1]] 

    #====================================================================
    # Select data for SLP only months and years for the climate index
    #====================================================================
    climate_index['date']=pd.to_datetime(climate_index['year'].astype(str) +climate_index['month'].astype(str), format='%Y%m')
    SLP=xr.open_dataset(local_path+'/Monthly_mean_MSLP_all.nc')
    SLP['time'] = pd.to_datetime(SLP['time'])
    SLP= SLP.sel(time=SLP['time'].isin(climate_index['date']))

    # save filtered SLP 
    SLP.to_netcdf(local_path+'/Monthly_mean_MSLP.nc')

    #====================================================================
    # Select data for SST only months and years for the climate index
    #====================================================================

    SST=xr.open_dataset(local_path+'/Monthly_mean_SST_all.nc')
    SST['time'] = pd.to_datetime(SST['time'])
    SST= SST.sel(time=SST['time'].isin(climate_index['date']))

    # save filtered SST 
    SST.to_netcdf(local_path+'/Monthly_mean_SST.nc')

    # Select data for storms from IBTrACS only months and years for the climate index
    cyclones=xr.open_dataset(local_path+file_name)
    cyclones=xr.open_dataset(local_path+'/IBTrACS.ALL.v04r00.nc')

    # convert dates to the same format, in this case year and months
    datetime_array_month = cyclones['time'].values.astype('datetime64[M]')
    climate_index['date'] = pd.to_datetime(climate_index['year'].astype(str) + climate_index['month'].astype(str), format='%Y%m').dt.to_period('M')
    dates_to_compare = climate_index['date'].to_numpy()
    dates_to_compare = dates_to_compare.astype('datetime64[M]')

    #====================================================================
    # Select data for TC only months and years for the climate index
    #====================================================================

    # create a mask to identify storms belonging to a phase of the climate index 
    mask = np.zeros_like(datetime_array_month, dtype=bool)
    for i in range(datetime_array_month.shape[0]):
        for j in range(datetime_array_month.shape[1]):
            # Check if the value coincides with any date in dates_array
            if datetime_array_month[i, j] in dates_to_compare:
                mask[i, j] = True

    mask1=mask[:,0]
    filtered_cyclones = cyclones.sel(storm=mask1)

    # save filtered cyclones 
    filtered_cyclones.to_netcdf(local_path+'/IBTrACS.'+str(year[0])+'_'+str(year[1])+'v04r00.nc')