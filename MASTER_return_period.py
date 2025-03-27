import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import geopandas as gpd

#==================================================== 
# Calculate distance                 
#==================================================== 
PathOut=r'/home/projects/gflood/itxaso/TC/results/'
pathSTORM=r'/home/projects/gflood/itxaso/TC/Return_periods/'

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)

    Parameters
    ----------
    lon1,lat1 : coordinates location 1
    lon2,lat2 : coordinates location 2

    Returns
    -------
    distance in km.

    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r


name_BASIN='SP'
range1=4
range2=5

GCM=['IBTRACS','CMCC-CM2-VHR4','CNRM-CM6-1-HR','EC-Earth3P-HR','HadGEM3-GC31-HM']
BASIN_names=['EP','NA','NI','SI','SP','WP']
text_file=['.txt','_EXTRA_PARAMETERS__IBTRACSDELTA.txt','_EXTRA_PARAMETERS__IBTRACSDELTA.txt','_EXTRA_PARAMETERS__IBTRACSDELTA.txt','_EXTRA_PARAMETERS__IBTRACSDELTA.txt']

#==================================================== 
# Load cities                 
#==================================================== 
df=pd.read_excel('TC_municipalities_adm04_'+name_BASIN+'.xlsx',header=0,keep_default_na=False)
latitudes=df['LATITUDE']
longitudes=df['LONGITUDE']
basins=df['BASIN']
names=df['NAME']
capitals=df['CAPITAL CITY']

wind_dict={i:[] for i in range(len(latitudes))}
radius=111
nloop=3
nyear=3000.
nyear1=3000

for nmodel in range(0,1):
    print (nmodel,GCM[nmodel])
    for basinid in range(range1,range2):
        basin=BASIN_names[basinid]
        for index in range(0,nloop): 
            #load the STORM datasets. Make sure the directory is set right!
            data=np.loadtxt('STORM_DATA_'+GCM[nmodel]+'_'+str(basin)+'_1000_YEARS_'+str(index)+text_file[nmodel],delimiter=',')
    
            #extract necessary parameters (change the parametered you want to study)
            time,lat,lon,wind=data[:,3],data[:,5],data[:,6],data[:,8]
            del data
                
            indices=[i for i,x in enumerate(time) if x==0]
            indices.append(len(time))
            i=0
            
            #loop over all TCs in the dataset
            while i<len(indices)-1:
                start=indices[i]
                end=indices[i+1]
                
                latslice=lat[start:end]
                lonslice=lon[start:end]
                windslice=wind[start:end]
                        
                for l in range(len(latitudes)): #for every city
                    if basins[l]==basin:
                        lat_loc=latitudes[l]
                        lon_loc=longitudes[l]
                        wind_loc=[]
                        if lon_loc<0.:
                            lon_loc+=360        
                
                        for j in range(len(latslice)):
                            #calculate the distance between the track and the capital city
                            distance=haversine(lonslice[j],latslice[j],lon_loc,lat_loc)
                          
                            if distance<=radius:
                                wind_loc.append(windslice[j])
                        
                        if len(wind_loc)>0.:
                            if np.max(wind_loc)>=18.:
                                wind_dict[l].append(np.max(wind_loc)) #store the maximum wind speed for the TC
                i=i+1
                
                   for index in range(0,nloop): 
            #load the STORM datasets. Make sure the directory is set right!
            data=np.loadtxt('STORM_DATA_'+GCM[nmodel]+'_'+str(basin)+'_1000_YEARS_'+str(index)+text_file[nmodel],delimiter=',')
    
            #extract necessary parameters (change the parametered you want to study)
            time,lat,lon,wind=data[:,3],data[:,5],data[:,6],data[:,8]
            del data
                
            indices=[i for i,x in enumerate(time) if x==0]
            indices.append(len(time))
            i=0
            
            #loop over all TCs in the dataset
            while i<len(indices)-1:
                start=indices[i]
                end=indices[i+1]
                
                latslice=lat[start:end]
                lonslice=lon[start:end]
                windslice=wind[start:end]
                        
                for l in range(len(latitudes)): #for every city
                    if basins[l]==basin:
                        lat_loc=latitudes[l]
                        lon_loc=longitudes[l]
                        wind_loc=[]
                        if lon_loc<0.:
                            lon_loc+=360        
                
                        for j in range(len(latslice)):
                            #calculate the distance between the track and the capital city
                            distance=haversine(lonslice[j],latslice[j],lon_loc,lat_loc)
                          
                            if distance<=radius:
                                wind_loc.append(windslice[j])
                        
                        if len(wind_loc)>0.:
                            if np.max(wind_loc)>=18.:
                                wind_dict[l].append(np.max(wind_loc)) #store the maximum wind speed for the TC
                i=i+1

    
    #==================================================== 
    # Define the return periods/wind speeds you want to evalute the wind speeds/return periods. 
    # This need to be stored in the wind_rp and wind_intems
    #====================================================             
    returnperiods=[1,2,5]
    returnperiods.extend(np.linspace(10,100,10))
    returnperiods.extend(np.linspace(200,1000,9))
    returnperiods.extend(np.linspace(2000,3000,9))
    
    #Please check the definition of wind speed! If it's 1-minute sustained wind, use the following: 
    #wind_items=[20,25,30,33,35,40,42,45,50,55,58,60,65,70,75,80,85]
    
    #In STORM, the wind speeds are 10-min average, so the Saffir-Simpson category thresholds need to be converted from 1-min to 10-min: 
    #This includes tropical storm, cat1,cat2,cat3,cat4 and cat5
    wind_items=[15.4,29,37.6,43.4,51.1,61.6]
    
    for i in range(len(wind_dict)):
        print(i)
        name=names[i]
        city=capitals[i]
        LON=longitudes[i]
        LAT=latitudes[i]
       
        if len(wind_dict[i])>0.:    
            df=pd.DataFrame({'Wind': wind_dict[i]})
            df['Ranked']=df['Wind'].rank(ascending=0)
            df=df.sort_values(by=['Ranked'])
            ranklist=df['Ranked'].tolist()
            windlist=df['Wind'].tolist() 
            
            rpwindlist=[]  
            
            NAME_city_1=[] 
            R_period_1=[]
            Wind_velocity_1=[]
            lat_city1=[]
            lon_city1=[]
            
            NAME_city_2=[] 
            R_period_2=[]
            Wind_velocity_2=[]
            lat_city2=[]
            lon_city2=[]
                
            for m in range(len(ranklist)):
                weibull=(ranklist[m])/(len(ranklist)+1.) #weibulls plotting formula. This yields the exceendance probability per event set
                r=weibull*(len(ranklist)/nyear) #multiply by the average number of events per year to reach the exceedence probability per year
                rpwindlist.append(1./r) #convert to year instead of probability

            rpwindlist=rpwindlist[::-1]         
            windlist=windlist[::-1] 
            
            if np.min(rpwindlist)<(nyear1+1):       
                for rp in returnperiods:
                    if np.max(rpwindlist)>=rp and np.min(rpwindlist)<=rp:            
                        #Interpolate to the desired return level
                        windint=np.interp(rp,rpwindlist,windlist) 
                        NAME_city_1.append(city) 
                        lat_city1.append(LAT) 
                        lon_city1.append(LON) 
                        R_period_1.append(rp)
                        Wind_velocity_1.append(windint)
    
                for w in wind_items:
                    rp_int=np.interp(w,windlist,rpwindlist)
                    NAME_city_2.append(city) 
                    lat_city2.append(LAT) 
                    lon_city2.append(LON) 
                    Wind_velocity_2.append(w)
                    R_period_2.append(rp_int)
                    
            df_rp = pd.DataFrame({'Lat':lat_city1,'Lon':lon_city1,'Name': NAME_city_1,'Return Period': R_period_1,  'Wind Speed': Wind_velocity_1})
            df_winds = pd.DataFrame({'Lat':lat_city2,'Lon':lon_city2,'Name': NAME_city_2, 'Wind Speed': Wind_velocity_2,  'Return Period': R_period_2})
            
            df_rp.to_csv(name_BASIN+'_adm04_'+str(i)+'_'+GCM[nmodel]+'_return_period.csv', index=False) 
            df_winds.to_csv(name_BASIN+'_adm04_'+str(i)+'_'+GCM[nmodel]+'_velocity.csv', index=False) 

