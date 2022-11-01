# -*- coding: utf-8 -*-
"""
Created on Mon Apr  4 21:20:19 2022

@author: nricc
"""
import numpy as np
import math 
import scipy.stats as s
import datetime as dt
import matplotlib.pyplot as plt
from windrose import WindroseAxes, clean

from data_filter_Functions import * 

def plotWindRose(time_vect, dir_array, spd_array, height_ind):
    
    time_gt0 = time_vect[nonZeroIndex(time_vect)]
    #print(time_gt0)
    
    dir_filt = dir_array[:, nonZeroIndex(time_vect)]
    spd_filt = spd_array[:, nonZeroIndex(time_vect)]
    #print(np.argwhere(np.isnan(spd_filt)))
    
    spd_filt = np.nan_to_num(spd_filt)
    dirspdClean = clean(dir_filt[height_ind,:],spd_filt[height_ind,:])
    #print(np.argwhere(np.isnan(dirspdClean[1])))

    ax = WindroseAxes.from_ax()
    ax.set_xticklabels(['E', 'NE',  'N', 'NW', 'W', 'SW','S', 'SE']) 
    ax.set_theta_zero_location('N',offset=-90.0)
    ax.bar(dirspdClean[0], dirspdClean[1] , nsector = 9, bins = range(0,30,5), \
           normed=True, opening=0.5, edgecolor='black') 
    ax.set_rgrids([10,30,50,70,],labels=['0.1','0.3','0.5','0.7'],fontsize=14)
    ax.set_legend(units='m/s', decimal_places=0,fontsize=14)
    plt.title('Wind Rose, Morro Bay: ')
    plt.show()
    
    meanWS = np.mean(dirspdClean[1])
    medianWD = np.median(dirspdClean[0])
    
    #print("Mean Wind Speed: %.2f" % np.mean(dirspdClean[1]))
    #print("Median Wind Dir: %.1f" % np.median(dirspdClean[0]))
    
    return meanWS, medianWD

def plotWeibull(dates, spd_array, height_array, hub_height, spdf):
    
    height_ind = np.where(height_array == hub_height)
    spd_filt = sortAndNoNan(spd_array[height_ind,:])
    #print(spd_filt)
    spd_filt = spd_filt[np.where(spd_filt > spdf)]
    
    wShape, wLoc, wScale = s.weibull_min.fit(spd_filt,floc=0)
    
    print("Weibull Shape: %.2f" % wShape)
    print("Weibull Scale: %.2f" % wScale)
    
    weibLabel = 'Weibull (c= %.2f, k=%.2f)' % (wScale, wShape)
    
    binsA = range(0,25,1)
    plt.plot(spd_filt, \
          s.weibull_min.pdf(spd_filt, \
           *s.weibull_min.fit(spd_filt, floc=0)), label=weibLabel)
    plt.hist(spd_filt, bins=binsA, density=True, edgecolor='black',label="at "+str(hub_height)+'m')
    plt.title('Weibull Distribution: %s - %s' % (list(dates)[0], list(dates)[-1]))
    plt.xlabel('Wind Speed (m/s)')
    plt.ylabel('PDF')
    plt.legend()
    plt.show() 

def plotDailyContour(data_avail_array, time_array, date_array, height_array):
 
    avg, std, med = ontheDayAvg(data_avail_array, height_array, date_array)

    #monName1 = getMonName(np.min(date_array[:,1]))
    #monName2 = getMonName(np.max(date_array[:,1]))
    monthRange = getMonNames(date_array[:,1])
    tickval = np.array([1,7,14,21,28,31])
    ticklab = tickval.astype(str)
    
    #cp = plt.contourf(time_array,height_array, data_avail_array,cmap='RdYlBu',levels=np.linspace(0,100,25))
    cp = plt.contourf(range(1,32), height_array, avg, \
                      cmap='RdYlBu',levels=np.linspace(0,100,25))
    plt.plot(range(1,32),np.ones(31)*100.0, '--k')
    #plt.xticks(time_array[0:-1:filt],labels= date_array[0:-1:filt,3].astype(str))
    plt.xticks(tickval,labels=ticklab)
    plt.yticks(height_array[1:-1:3],labels=height_array[1:-1:3].astype(str))
    plt.title('Data Availability: %s-%s' % (monthRange[0], monthRange[1]) )
    
    plt.xlabel('Day of the Month')
    plt.ylabel('Height (m)')
    plt.colorbar(cp)
    plt.show() 
    
def plotMonthContour(data_avail_array, time_array, date_array, height_array):
 
    avg, std, med = ontheMonAvg(data_avail_array, height_array, date_array)

    #monName1 = getMonName(np.min(date_array[:,1]))
    #monName2 = getMonName(np.max(date_array[:,1]))
    monthRange = getMonNames(date_array[:,1])
    tickval = np.arange(1,12,1)
    ticklab = tickval.astype(str)
    
    #cp = plt.contourf(time_array,height_array, data_avail_array,cmap='RdYlBu',levels=np.linspace(0,100,25))
    cp = plt.contourf(range(1,32), height_array, avg, \
                      cmap='RdYlBu',levels=np.linspace(0,100,25))
    plt.plot(range(1,32),np.ones(31)*100.0, '--k')
    #plt.xticks(time_array[0:-1:filt],labels= date_array[0:-1:filt,3].astype(str))
    plt.xticks(tickval,labels=ticklab)
    plt.yticks(height_array[1:-1:2],labels=height_array[1:-1:3].astype(str))
    plt.title('Data Availability: %s-%s' % (monthRange[0], monthRange[1]) )
    
    plt.xlabel('Month')
    plt.ylabel('Height (m)')
    plt.colorbar(cp)
    plt.show() 
    
def plotDiurnalCycle(wspd_array, time_array, date_array, hubh):
    
   # monName1 = getMonNames(np.min(date_array[:,1]))
    #monName2 = getMonName(np.max(date_array[:,1]))
    monthRange = getMonNames(date_array[:,1])
    # Need to nanmean on the hours 0,1,2...23
    # nanstd on hours 
    # plot line-cloud 
    # Should only have 24 data points 
    avg, std, med = onTheHourAvg(wspd_array, hubh, date_array)
    
    tickval = np.array([0,6,12,18,23])
    ticklab = tickval.astype(str)
    fig, ax = plt.subplots()
    ax.plot(range(0,24), avg, '--', color = 'navy', label='Lidar') #wspd_array[hubh,:].reshape(-1) ) #wspd_array[:,h_ind].reshape(-1)[st:en])
    plt.fill_between(range(0,24), avg-std, avg+std, color='lightsteelblue', \
                      alpha=0.75, label='+/-$\sigma$')
    plt.xticks(tickval, labels = ticklab)

    plt.ylim([0,25])
    plt.title('Diurnal Cycles at 100m: %s-%s' % (monthRange[0], monthRange[1]) )
              
    plt.ylabel('Mean Wind Speed (m/s)')
    plt.xlabel('Time (UTC-hr)')
    plt.legend()
    plt.grid()
    plt.show()
    
def plotDiurnalCycle2(wdir_array, time_array, date_array, hubh):
    
   # monName1 = getMonNames(np.min(date_array[:,1]))
    #monName2 = getMonName(np.max(date_array[:,1]))
    monthRange = getMonNames(date_array[:,1])
    # Need to nanmean on the hours 0,1,2...23
    # nanstd on hours 
    # plot line-cloud 
    # Should only have 24 data points 
    avg, std, med = onTheHourAvg(wdir_array, hubh, date_array)
    
    tickval = np.array([0,6,12,18,23])
    ticklab = tickval.astype(str)
    fig, ax = plt.subplots()
    ax.plot(range(0,24), med, '--', color = 'darkgreen', label='Lidar') #wspd_array[hubh,:].reshape(-1) ) #wspd_array[:,h_ind].reshape(-1)[st:en])
    plt.fill_between(range(0,24), med-std, med+std, color='lime', \
                      alpha=0.75, label='+/-$\sigma$')
    plt.xticks(tickval, labels = ticklab)

    #plt.ylim([0,25])
    plt.title('Diurnal Cycles at 120m: %s-%s' % (monthRange[0], monthRange[1]) )
              
    plt.ylabel('Median Wind Direction (deg)')
    plt.xlabel('Time (UTC-hr)')
    plt.legend()
    plt.grid()
    plt.show()