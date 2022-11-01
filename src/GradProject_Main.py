# -*- coding: utf-8 -*-
"""
ATOC-5570 Graduate Project: California LeoSphere Lidar Data Analysis 
  
    These scripts are used to evaluate the wind resources at of two
    lidar datasets. The data source: https://a2e.energy.gov/data# 
    
    set z06: Morro Bay https://a2e.energy.gov/data/buoy/lidar.z06.a0 
    set z05: Humboldt Bay https://a2e.energy.gov/data/buoy/lidar.z05.a0
    
    
"""
import netCDF4 as nc
import numpy as np
import math 
import scipy.stats as s
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.ticker as tk 
import os

#from windrose import WindroseAxes, clean

from data_filter_Functions import * 
from file_filter_Functions import * 
from plot_Functions import * 

#######################
# Input Parameters 
#
#######################
inputList = ['Humboldt', 20201003, 20211002]
#inputList = ['Morro', 20201001, 20210930] # ['Morro', 20200926, 20210925]
startDate = inputList[1] # 20200926 # Humboldt 20201003 # Morro start 20200926
endDate   = inputList[2] # 20210925 # Humboldt 20211002 # Morro end 20210925 # 20201001  # 20200928 # 

hub_ht    = 100.0
cutin_spd = 0.0

Wint_span = [12,2 ]
Sprg_span = [3 ,5 ]
Sumr_span = [6 ,8 ]
Fall_span = [9 ,11]

#######################
# Plot switches
# 
#######################
iPlotWindRose = True
iPlotWeibull = True
iPlotAvail = True
iPlotDiurn = True
iPlotDiurn2 = False


#######################
# File directories 
#
#######################
datadir = '../data/'            # Data directory 
lidarset= 'LeoSphere_' + inputList[0]     # Lidar Subdirectory (Morro Bay)
#lidarset= 'LeoSphere_Humboldt' # Lidar Subdirectory (Humboldt Bay)
datapath = datadir + lidarset
sumdir = datadir + 'Summary_csv/' # Summary Subdirectory (csv files)

######################
# Summary file names 
#
######################
TSummaryFile = "TWS_Sum_"+ str(startDate) + '_' + str(endDate) + lidarset[10:11] +'.csv'
SSummaryFile = 'WS_Sum_' + str(startDate) + '_' + str(endDate) + lidarset[10:11] + '.csv'
DSummaryFile = 'WD_Sum_' + str(startDate) + '_' + str(endDate) + lidarset[10:11] + '.csv'
ASummaryFile = 'DA_Sum_' + str(startDate) + '_' + str(endDate) + lidarset[10:11] + '.csv'


### Checking file existance and generating csv files for later  
# Check if .nc files exist in the Lidary Subdirectory (datapath)
filesAll = getAllFiles(datapath,".nc", True)

# Get list of unique files and dates associated with startDate and endDate
filesUniq = getUniqueFiles(filesAll,True)
datesUniq = getUniqueDates(filesUniq,False)

# Get a date span list associated with startDate and endDate
dateSpan = getDateSpan(startDate,endDate,True)

# Get list of files that match the date span 
fileSpan = getFileSpan(dateSpan,filesUniq,True)

# Report any missing files in the date span  
filesMissing = getMissingFiles(dateSpan,fileSpan, True)

# Generate Summary csv files if they do not exist in sumdir 
genSummaryCsv('wind_speed',sumdir, SSummaryFile, datapath, fileSpan,True,True)
genSummaryCsv('wind_direction',sumdir, DSummaryFile, datapath, fileSpan)
genSummaryCsv('data_availability',sumdir, ASummaryFile, datapath, fileSpan)

# Write data from Summary csv files into arrays for processing/plotting 
sumArrayT  = getArrayFromCsv(sumdir, TSummaryFile)
sumArrayWS = getArrayFromCsv(sumdir, SSummaryFile)
sumArrayWD = getArrayFromCsv(sumdir, DSummaryFile)
sumArrayDA = getArrayFromCsv(sumdir, ASummaryFile)
    

### Height array and hub height index
# 
hASL = get1dArg(datapath + '/' + filesUniq[0], 'height')
#print("Height above seal level", ASL)
h_ind = np.where(hASL == hub_ht)

# Plot Wind Rose at hub height for all time stamps
if(iPlotWindRose): 
    avgWS, medWD = plotWindRose(sumArrayT, sumArrayWD, sumArrayWS, h_ind)
    print("\nPlotting Wind Rose \n")
    print("Mean Wind Speed: %.2f" % avgWS) 
    print("Median Wind Dir: %.1f" % medWD)

# Plot Wiebull Distribution at hub height for all time stamps
if(iPlotWeibull):
    print("\nPlotting Weibull Distribution \n")
    plotWeibull(dateSpan, sumArrayWS, hASL, hub_ht, cutin_spd)



### Shrink time stamp array into seasonal arrays 
#
times_Fall, ind_Fall = shrinkTime(sumArrayT,Fall_span[0], Fall_span[1])
dates_Fall = separateTime(times_Fall)
dates2_Fall = getDateStamp(times_Fall)

times_Wint, ind_Wint = shrinkTime(sumArrayT,Wint_span[0], Wint_span[1])
dates_Wint = separateTime(times_Wint)

times_Sprg, ind_Sprg = shrinkTime(sumArrayT,Sprg_span[0], Sprg_span[1])
dates_Sprg = separateTime(times_Sprg)

times_Sumr, ind_Sumr = shrinkTime(sumArrayT,Sumr_span[0], Sumr_span[1])
dates_Sumr = separateTime(times_Sumr)

### Arguments array into season arrays 
#
wspd_Fall = sumArrayWS[:,ind_Fall]
wspd_Wint = sumArrayWS[:,ind_Wint]
wspd_Sprg = sumArrayWS[:,ind_Sprg]
wspd_Sumr = sumArrayWS[:,ind_Sumr]

wdir_Fall = sumArrayWD[:,ind_Fall]
wdir_Wint = sumArrayWD[:,ind_Wint]
wdir_Sprg = sumArrayWD[:,ind_Sprg]
wdir_Sumr = sumArrayWD[:,ind_Sumr]

da_Fall = sumArrayDA[:,ind_Fall]
da_Wint = sumArrayDA[:,ind_Wint]
da_Sprg = sumArrayDA[:,ind_Sprg]
da_Sumr = sumArrayDA[:,ind_Sumr]

### Get hourly averages of season arrays 
#
wspd_Fall_avg, times_Fall_avg, dates_Fall_avg = hourlyAvg(times_Fall, wspd_Fall)
wspd_Wint_avg, times_Wint_avg, dates_Wint_avg = hourlyAvg(times_Wint, wspd_Wint)
wspd_Sprg_avg, times_Sprg_avg, dates_Sprg_avg = hourlyAvg(times_Sprg, wspd_Sprg)
wspd_Sumr_avg, times_Sumr_avg, dates_Sumr_avg = hourlyAvg(times_Sumr, wspd_Sumr)

wdir_Fall_avg, times_Fall_avg, dates_Fall_avg = hourlyAvg(times_Fall, wdir_Fall)
wdir_Wint_avg, times_Wint_avg, dates_Wint_avg = hourlyAvg(times_Wint, wdir_Wint)
wdir_Sprg_avg, times_Sprg_avg, dates_Sprg_avg = hourlyAvg(times_Sprg, wdir_Sprg)
wdir_Sumr_avg, times_Sumr_avg, dates_Sumr_avg = hourlyAvg(times_Sumr, wdir_Sumr)

da_Fall_avg, times_Fall_avg, dates_Fall_avg = hourlyAvg(times_Fall, da_Fall)
da_Wint_avg, times_Wint_avg, dates_Wint_avg = hourlyAvg(times_Wint, da_Wint)
da_Sprg_avg, times_Sprg_avg, dates_Sprg_avg = hourlyAvg(times_Sprg, da_Sprg)
da_Sumr_avg, times_Sumr_avg, dates_Sumr_avg = hourlyAvg(times_Sumr, da_Sumr)

wspd2_Fall_avg, time2_Fall_avg, dates2_Fall_avg = hourlyAvg2(times_Fall, wspd_Fall)
### Plot Diurnal cycle of Wind Speed
#
if(iPlotDiurn):
    plotDiurnalCycle(wspd_Wint_avg, times_Wint_avg, dates_Wint_avg, h_ind)
    plotDiurnalCycle(wspd_Sprg_avg, times_Sprg_avg, dates_Sprg_avg, h_ind)
    plotDiurnalCycle(wspd_Sumr_avg, times_Sumr_avg, dates_Sumr_avg, h_ind)
    plotDiurnalCycle(wspd_Fall_avg, times_Fall_avg, dates_Fall_avg, h_ind)
    
    #plotDiurnalCycle(wspd2_Fall_avg, times_Fall_avg, dates2_Fall_avg, h_ind)

if(iPlotDiurn2):
    plotDiurnalCycle2(wdir_Wint_avg, times_Wint_avg, dates_Wint_avg, h_ind)
    plotDiurnalCycle2(wdir_Sprg_avg, times_Sprg_avg, dates_Sprg_avg, h_ind)
    plotDiurnalCycle2(wdir_Sumr_avg, times_Sumr_avg, dates_Sumr_avg, h_ind)
    plotDiurnalCycle2(wdir_Fall_avg, times_Fall_avg, dates_Fall_avg, h_ind)
    
### Plot Contour of Data Availability 
#
if(iPlotAvail):
    plotDailyContour(da_Wint_avg, times_Wint_avg, dates_Wint_avg, hASL)
    plotDailyContour(da_Sprg_avg, times_Sprg_avg, dates_Sprg_avg, hASL)
    plotDailyContour(da_Sumr_avg, times_Sumr_avg, dates_Sumr_avg, hASL)
    plotDailyContour(da_Fall_avg, times_Fall_avg, dates_Fall_avg, hASL)

#if(iPlotAvail2):
    #plotMonthContour()
# Plot wind shear profile for a given day 
#sumArrayDate = separateTime(sumArrayT)
#day = 20200930
#dayStamp = dt.date(int(str(day)[0:4]),int(str(day)[4:6]),int(str(day)[6:8]))
#startInd = np.where((sumArrayDate[0,:]==dayStamp.year) & \
#                    (sumArrayDate[1,:]==dayStamp.month) & \
#                        (sumArrayDate[2,:]==dayStamp.day))[0][0]
#endInd = np.where((sumArrayDate[0,:]==dayStamp.year) & \
#                    (sumArrayDate[1,:]==dayStamp.month) & \
#                        (sumArrayDate[2,:]==dayStamp.day))[0][-1]
    
#timeDay = sumArrayDate[:,startInd:endInd]
#secsDay = sumArrayT[startInd:endInd]

#spdDay = sumArrayWS[:,startInd:endInd]
#spdDay_avg = np.nanmean(sumArrayWS[:,startInd:endInd],axis=1)
#spdDay_std = np.nanstd(sumArrayWS[:,startInd:endInd],axis=1)

#plt.plot(spdDay_avg,hASL,'--k',label='Lidar')
#plt.fill_betweenx(hASL, spdDay_avg-spdDay_std, spdDay_avg+spdDay_std, \
#                  alpha=0.5, label='+/-$\sigma$')

#plt.xlim([4.0,20.0])
#plt.xlabel('Wind Speed (m/s)')
#plt.ylabel('Height (m)')
#plt.title('Mean Wind Speed Profile: %s-%s-%s' % (dayStamp.year,dayStamp.month,dayStamp.day))
#plt.legend()
#plt.show()

#daDay = sumArrayDA[:,startInd:endInd]
#plotDailyContour(daDay, secsDay, hASL)


#A, B, C = hourlyAvg(sumArrayT_f, sumArrayDA)

#newDA = np.stack(A)
#cp = plt.contourf(B,hASL, newDA.T,cmap='RdYlBu',levels=np.linspace(0,100,25))
#plt.xticks()
#plt.title("Data Availability: %s-%s-%s") # % (dayStamp.year,dayStamp.month,dayStamp.day))
#plt.colorbar(cp)
#plt.show() 


#plt.plot(timeDay[3],spdDay[h_ind].T)
#plt.show()
#A = np.where(arrayTstamp[])
#print(WindSumVsTime[:,2].shape,WindSum_noNan.shape, WindSum_noNan.astype)
#WindClean = clean(WindSumVsTime[:,2], WindSumVsTime[:,1])
#C = np.argwhere(np.isnan(WindClean[1]))
#print(C)
#A = np.where(WindClean[0]==np.nan)

#wd = np.random.random(13728)*360
#ws = np.random.random(13728)*6

#A = np.where(WindSumVsTime[:,0]>0.0)
#print(A)
#plt.plot(WindSumVsTime[A[0],0],WindSumVsTime[A[0],2])
#plt.xlim([1.59e9,1.61e9])
#plt.show()



