# -*- coding: utf-8 -*-
"""
This script has been developed by Itxaso Odériz. 
This script generate parameters of tropical cyclones that are important for coastal impacts.
The script is heavily inspired by 

Bloemendaal, N., Haigh, I.D., de Moel, H. et al. 
Generation of a global synthetic tropical cyclone hazard dataset using STORM. 
Sci Data 7, 40 (2020). https://doi.org/10.1038/s41597-020-0381-2

Copyright (C) 2023 Itxaso Odériz. 
"""

import numpy as np
import holland_model as hm
import math
from scipy import spatial
import storm_parameters as sp

def Basins_WMO(basin):
    if basin=='EP': #Eastern Pacific
        lat0,lat1,lon0,lon1=5,60,180,285
    if basin=='NA': #North Atlantic
        lat0,lat1,lon0,lon1=5,60,255,359
    if basin=='NI': #North Indian
        lat0,lat1,lon0,lon1=5,60,30,100
    if basin=='SI': #South Indian
        lat0,lat1,lon0,lon1=-60,-5,10,135
    if basin=='SP': #South Pacific
        lat0,lat1,lon0,lon1=-60,-5,135,240
    if basin=='WP': #Western Pacific
        lat0,lat1,lon0,lon1=5,60,100,180
    
    return lat0,lat1,lon0,lon1

# =============================================================================
# Please define a basin (EP,NA,NI,SI,SP,WP), index (0-9), and yearslice of 100 years (0-9)
# =============================================================================
basin='NA'
index=0
yearslice=0
year_int=100

#==============================================================================
# Constants from literature
#==============================================================================
alpha=0.55              #Deceleration of surface background wind - Lin & Chavas 2012
beta_bg=20.             #Angle of background wind flow - Lin & Chavas 2012
SWRF=0.85               #Empirical surface wind reduction factor (SWRF) - Powell et al 2005 
CF=0.915                #Wind conversion factor from 1 minute average to 10 minute average - Harper et al (2012)

#==============================================================================
# Other pre-defined constants
#==============================================================================
tc_radius=1000.            #Radius of the tropical cyclone, in km
max_distance=tc_radius/110. #Maximum distance (in degrees) to look for coastal points in the full file
Patm=101325.

#==============================================================================
# Douglas_peucker algorithm pre-defined constants
#==============================================================================
Param_track=0.3   #Delta to applied douglas_peucker algorithm

#==============================================================================
# Spyderweb specifications 
#==============================================================================
n_cols=36                   #number of gridpoints in angular direction
n_rows=1000                 #number of gridpoints in radial direction

#==============================================================================
# Create a list of points at 0.1deg resolution, spanning the whole basin
#==============================================================================
lat0,lat1,lon0,lon1=Basins_WMO(basin) #see basin boundary definitions in line 23
res=0.1
if lat0>0:
    latspace=np.arange(lat0+res/2.,lat1+res/2.,res)
else:
    latspace=np.arange(lat0-res/2.,lat1-res/2.,res)

lonspace=np.arange(lon0+res/2.,lon1+res/2.,res)

points=[(i,j) for i in latspace for j in lonspace]
   
wind_field={i:[] for i in range(len(points))} #the index corresponds to the index of the 
#points-list. So the lon/lat of index i is given by points[i], the wind data by wind_field[i] 

tree=spatial.cKDTree(points)

#==============================================================================
# Open the STORM dataset
#==============================================================================
#Please make sure to point to the right directory!
data=np.loadtxt('STORM_DATA_IBTRACS_'+str(basin)+'_1000_YEARS_'+str(index)+'.txt',delimiter=',')
yearall,data1,data2,timeall,data4,latall,lonall,presall,windall,rmaxall,data10,landall,distlandall=data[:,0],data[:,1],data[:,2],data[:,3],data[:,4],data[:,5],data[:,6],data[:,7],data[:,8],data[:,9],data[:,10],data[:,11],data[:,12]

# Create arrays for the transitional speed, residence-time, and relative angle and complexity track
transspeedall = yearall-yearall
residencetimeall = yearall-yearall
complexitytrackall= []
relative_angleall= yearall-yearall
# Usurf=[]
year=[y for y in yearall if y>=yearslice*year_int and y<(yearslice+1)*year_int]
year_begin=year[0]
year_end=year[-1]
begin=np.searchsorted(yearall,year_begin)
end=np.searchsorted(yearall,year_end)   

indiceslist=[i for i,x in enumerate(timeall[begin:end]) if x==0]  #a new TC always starts at time step 0 
i=0 
cont=0  
#loop over the different TCs
while i<len(indiceslist)-1:  
    start=indiceslist[i]+begin
    end=indiceslist[i+1]+begin
    
    # Extract array for each TC's variable
    latslice=latall[start:end]
    lonslice=lonall[start:end]
    windslice=windall[start:end]
    presslice=presall[start:end]
    timeslice=timeall[start:end] 
    rmaxslice=rmaxall[start:end]
    landslice = landall[start:end]
    distlandslice = distlandall[start:end]
    complexitytrack_slice = distlandall[start:end]-distlandall[start:end]
    relative_angle_slice = distlandall[start:end]-distlandall[start:end]    
    
    # Simplified the track with douglas_peucker (predetermined function) differnciating between water and land cells
    #extract points in land (landslice==1 are points on land)

    # Extract points in water (landslice==0 are points on water)
    points_track_water = np.column_stack((lonslice[landslice==0], latslice[landslice==0]))

    # Simplified track for water
    simplief_track_water = sp.douglas_peucker(points_track_water, Param_track) 

    # Calculate complex index only for water cells 
    complexitytrack_water = sp.track_complexity_index (simplief_track_water) 

    complexitytrack_slice[landslice==0] = complexitytrack_water

    if len(landslice[landslice==1])>0:
        points_track_land = np.column_stack((lonslice[landslice==1], latslice[landslice==1]))
    
        # Simplified track for land
        Simplief_track_land = sp.douglas_peucker(points_track_land, Param_track) 
    
        # Calculate complex index only for water cells 
        complexitytrack_land = sp.track_complexity_index (Simplief_track_land) 
    
        # Save complexity track index (IMPROVING!!!!)
        complexitytrack_slice[landslice==1] = complexitytrack_land
        
    complexitytrack_all.append(complexitytrack_slice)
    
    # Calculate the angle between shoreline and TCs (save each value in the track) 
    angle_Between_TC_shoreline=sp.relative_angle_cyclone_shoreline (latslice,lonslice,landslice)
    relative_angle_slice=relative_angle_slice-relative_angle_slice+angle_Between_TC_shoreline
        
    # Calculate the angle between shoreline and TCs (save each value in the track) 
    angle_Between_TC_shoreline=sp.relative_angle_cyclone_shoreline (latslice,lonslice,landslice)
    relative_angle_slice=relative_angle_slice+angle_Between_TC_shoreline

    shadowlist={kk:[] for kk in range(len(points))}
    for j in range(1,len(latslice)):
      lat0,lat1,lon0,lon1,t0,t1=latslice[j-1],latslice[j],lonslice[j-1],lonslice[j],timeslice[j-1],timeslice[j]
        
      # U10,Rmax,P=windslice[j],rmaxslice[j],presslice[j]
      dt=(t1-t0)*3600*3.                            
      
      [bg,ubg,vbg]=hm.Compute_background_flow(lon0,lat0,lon1,lat1,dt)
      
      # Save translation speed
      transspeedall[cont] = bg

      # Calculate the resident time = translation velocity* distance to land   
      residencetimeall[cont] = bg*distlandslice[j] 
      
      #1-minute maximum sustained surface winds
      # Usurf[cont]=(U10/SWRF)-(bg*alpha) #1-minute maximum sustained surface winds
      cont=cont+1
   
    i=i+1   
    print(i)

yearall     = np.array(yearall)
data1       = np.array(data1)
data2       = np.array(data2)
timeall     = np.array(timeall)
data4       = np.array(data4)
latall      = np.array(latall)
lonall      = np.array(lonall)
presall     = np.array(presall)
windall     = np.array(windall)
rmaxall     = np.array(rmaxall)
data10      = np.array(data10)
landall     = np.array(landall)
distlandall = np.array(distlandall)


TC_data=np.column_stack(yearall,data1,data2,timeall,data4,latall,lonall,presall,windall,rmaxall,data10,landall,distlandall,transspeedall,residencetimeall,relative_angleall,complexitytrackall)
np.savetxt(os.path.join(__location__,'STORM_DATA_IBTRACS_'+str(basin)+'_'+str(total_years)+'_YEARS_'+str(nloop)+'_EXTRA_PARAMETERS.txt'),TC_data,fmt='%5s',delimiter=',')

#By Itxaso OdÃ©riz 2023
#Headerline of 'STORM_DATA_IBTRACS_'+str(basin)+'_1000_YEARS_'+str(index)+'.txt'

#Entry	Variable name			    Unit		Notes on variable
#1	Year				              -		    Starts at 0
#2	Month			        	      -	
#3	TC number			              -		    For every year; starts at 0. 
#4	Time step			            3-hourly	For every TC; starts at 0.
#5	Basin ID			             -		    0=EP, 1=NA, 2=NI, 3=SI, 4=SP, 5=WP
#6	Latitude			            Deg		    Position of the eye.
#7	Longitude			            Deg		    Position of the eye. Ranges from 0-360Â°, with prime meridian at Greenwich.
#8	Minimum pressure		        hPa	
#9	Maximum wind speed		        m/s	
#10	Radius to maximum winds		    km	
#11	Category			            -		    .
#12	Landfall			            -		    0= no landfall, 1= landfall
#13	Distance to land		        km
#14	Translation speed		        m/s
#15 Residence time                  s
#16	Relative angle to the coast		degrees
#17	Index track complexity		    degrees