# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 18:46:13 2022

@author: nricc
"""
import numpy as np
import scipy.stats as s
import datetime as dt
import netCDF4 as nc
import os

from file_filter_Functions import * 

FillVal = -9999.0
timeDim = 144       # full length of time dimension in nc file
hghtDim = 12        # full length of height dimension in ncfile

def getDateSpan(d1,d2,showDates=False):
        
    if(d1 > d2): d2 = d1 
    
    start = dt.date(int(str(d1)[0:4]),int(str(d1)[4:6]),int(str(d1)[6:8]))
    end   = dt.date(int(str(d2)[0:4]),int(str(d2)[4:6]),int(str(d2)[6:8]))
    delta = end - start
    
    span_set = set(start + dt.timedelta(x) for x in range((delta.days+1)))
    sortedspan = sorted(span_set)
    if(showDates):
        print("results from getDateSpan:", len(list(sortedspan)),"days") 
        print(list(sortedspan)[0], "to", list(sortedspan)[-1],)
            
    return sortedspan

def get1dArg(dsfile,argin,debug=False):
    global FillVal 
    global timeDim      
    global hghtDim
    
    ds = nc.Dataset(dsfile)
    
    argSize = ds.dimensions[argin].size
    argVal = np.zeros([argSize])
    
    for x in range(argSize):
        argVal[x] = ds[argin][x]
    
    if(debug):
        if(argin == 'time'):
            if(argSize < timeDim):
                print("Time.size=",argSize)
                print("File",dsfile," has incomplete time series\n")
        elif(argin == 'height'):
            if(argSize < hghtDim):
                print("Height.size=",argSize)
                print("File",dsfile," has incomplete height series \n")
    
    return argVal

def get2dArg(dsfile,argin):
    global FillVal 
    global timeDim      
    global hghtDim
    
    ds = nc.Dataset(dsfile)
    
    tDim = get1dArg(dsfile,'time')
    hDim = get1dArg(dsfile,'height')
    
    argVal= np.zeros([tDim.size,hDim.size])
    
    for i in range(tDim.size):
        for j in range(hDim.size):
            
            if(ds[argin][i,j] == FillVal):
               argVal[i,j]  = np.nan 
            else:
                argVal[i,j] = ds[argin][i,j]
            
    return argVal 
        
def combineFiles(datdir, files,argin,debug=False):
    global timeDim
    global hghtDim

    combinedTime = np.zeros([len(files)*timeDim])
    combinedArg  = np.zeros([hghtDim,combinedTime.size]) 
    
    #files = []*len(fileslist)
    #os.chdir('../data/' + datdir)
    for e in range(len(files)):
        #files.append(datdir + '/' +fileslist[e])
        
        filep = datdir + '/' + files[e]
        ds = nc.Dataset(filep)
        
        #tdim, hdim, arg = checkDimensions(files[e],argin)
        timeD = get1dArg(filep,'time',debug)
        argV  = get2dArg(filep, argin) 
        
        if(timeD.size == timeDim):
            
            for t in range(timeDim):
                
                combinedTime[e*(timeDim) + t] = timeD[t]
                
                for h in range(hghtDim):
                    combinedArg[h,e*(timeDim) + t] = argV[t,h]
        else: 
            for s in range(timeD.size):
                combinedTime[e*(timeDim) + s] = timeD[s]
                
                for j in range(hghtDim):
                    combinedArg[j,e*(timeDim) + s] = argV[s,j]

    return combinedTime, combinedArg

def genSummaryCsv(argin, sumdir, filename, datdir, ufilelist, getTime=False, debug=False):

    #os.chdir(sumdir)
    prevd = os.getcwd()
    sumExist = checkSumFile(sumdir, filename)
    
    if (sumExist == False):
        print('\n Generating Summary file...')
        #os.chdir('../'+ datdir)
        os.chdir(prevd)
        combinedTArray, combinedArray = combineFiles(datdir, ufilelist, argin, debug)
        
        os.chdir(sumdir)
        np.savetxt(filename, np.array(combinedArray), delimiter=",")
        if(getTime):
            np.savetxt('T'+filename, np.array(combinedTArray),delimiter=",")

    os.chdir(prevd)

def getArrayFromCsv(sumdir, filename):
    
    #os.chdir(sumdir)
    with open(sumdir + '/' + filename) as file:
        sumArray = np.loadtxt(file,delimiter=",")
    
    return sumArray
 
def nonZeroIndex(a_Array):
    
    nZind = np.where(a_Array > 0.0)[0]
    
    return nZind

def sortAndNoNan(a_Array):
    
    f_sorted = np.sort(a_Array) 
    f_nonan = f_sorted[~np.isnan(f_sorted)]
    
    return f_nonan

def separateTime(sec_vect):
    dtStamp = [""]*sec_vect.size
    tExpd = np.zeros([6,sec_vect.size]).astype(int)
    
    for t in range(sec_vect.size):    
        dtStamp[t] = dt.datetime.strptime( \
                        str(dt.datetime.fromtimestamp(sec_vect[t])),"%Y-%m-%d  %H:%M:%S")
            
         
    
        # Populate year-month-day-Hour-Min-Sec array 
        tExpd[0,t] = int(dtStamp[t].year)
        tExpd[1,t] = int(dtStamp[t].month)
        tExpd[2,t] = int(dtStamp[t].day)
        tExpd[3,t] = int(dtStamp[t].hour)
        tExpd[4,t] = int(dtStamp[t].minute)
        tExpd[5,t] = int(dtStamp[t].second)

    #print(dtStamp[0],dtStamp[-1]) 
    #print("year:", ymdHMS[0,:])
    #print("hour", ymdHMS[3,:])
    #print(tStamp[1].year)
    return tExpd

def getDateStamp(sec_vect):
    
    dtStamp = [""]*sec_vect.size
    
    for t in range(sec_vect.size):    
        dtStamp[t] = dt.datetime.strptime( \
                        str(dt.datetime.fromtimestamp(sec_vect[t])),"%Y-%m-%d  %H:%M:%S")

    return dtStamp

def fillInTime(sec_vect): 
    
    filled_vect = np.zeros(sec_vect.size)
    dt = 10*60 # 10min x 60 seconds 
    for i in range(sec_vect.size):
        
        filled_vect[i] = sec_vect[i]
        if(filled_vect[i] == 0.0):
            filled_vect[i] = filled_vect[i-1]+dt
    
    return filled_vect

def shrinkTime(sec_vect, start, end):
    #int(str(d1)[0:4]),int(str(d1)[4:6]),int(str(d1)[6:8]))
    filled_vect = fillInTime(sec_vect)
    filled_dates = separateTime(filled_vect)
    # full month string - loses wrap around next year 
    #start_ind = np.where((filled_dates[0,:]== int(str(start)[0:4])) & \
    #                      (filled_dates[1,:]== int(str(start)[4:6])) & \
    #                        (filled_dates[2,:]== int(str(start)[6:8]))  )[0]
    t_ind = []
    # find indices where for a given month 
    if start == 12: start = 0
    if end == 12: end = 12
    for i in range(start,end+1):
        j = i
        if i==0 : j=12 
        t_ind.append(np.where((filled_dates[1,:] == j))[0])
       # print(j)
    #print(start_ind.size)
    #match the ending month
    #end_ind = np.where((filled_dates[1,:] == end))[0]
    #print(end_ind.size)
    shrunk_ind = np.sort(np.concatenate((t_ind[:]))) # np.sort(np.concatenate((start_ind,end_ind)))
    shrunk_vect = filled_vect[shrunk_ind] #[np.concatenate((start_ind,end_ind))]
    
    return shrunk_vect , shrunk_ind
    
def hourlyAvg(sec_vect,arg_array):
    global FillVal
    global timeDim
    global hghtDim
    
    date_array = separateTime(sec_vect)
    year_now = date_array[0,0]
    mon_now = date_array[1,0]
    day_now = date_array[2,0]
    hour_now = date_array[3,0] + 1 # should start on the next full hour
    
    #tenmin_arg = np.zeros([hghtDim,timeDim])
    tenmin_arg = np.zeros([hghtDim, 6])
    j = 0 # initialize a 10 min step (full day j = 144, watch out for DLS)
    prevj = j
    hourly_avglist = []
    dates_list = []
    time_list = []
    #count = 0
    
    for i in range(date_array.shape[1]):
        # check year 
        if(date_array[0,i]==year_now):
            
            # check the month
            if(date_array[1,i] == mon_now):
                
                # check the day 
                if(date_array[2,i] == day_now): 
                    #print(date_array[2,i])
                    
                    # check the hour 
                    if(date_array[3,i] == hour_now):
                        #if(j==0): print(date_array[:,i])
                        
                        # Use this to reset on DLS 
                        if(j >= 6):
                            j = 0
                        
                        tenmin_arg[:,j] = arg_array[:,i]
                        
                        #if(count < 20): print(j)
                        #count += 1
                        prevj = j
                        j += 1
                            
                    # new hour. Reset 10m step
                    else:
                        hour_now = date_array[3,i]
                        i -= 1
                        j = 0
                                        
                # new day. Reset 10m step. Capture new day and step back i-1
                else:
                    #print(j)
                    day_now = date_array[2,i]
                    hour_now = date_array[3,i]
                    i -= 1
                    j = 0
                    #daily_list.append(date_array[:,i])
                    
            # new month and new day. Step back i - 1 
            else: 
                mon_now = date_array[1,i]
                day_now = date_array[2,i]
                hour_now = date_array[3,i]
                #print(i, "when changing month")
                i -= 1
                j = 0
        else:
                year_now = date_array[0,i]
                mon_now = date_array[1,i]
                day_now = date_array[2,i]
                hour_now = date_array[3,i]
                
                i -= 1
                j= 0
        
        # Catch last step to append last day
        if(i==range(date_array.shape[1])[-1]): j=0 
        
        #if(prevj != j): print("j's don't match", mon_now, day_now)
        if((j==0) & (prevj != j)):
            hourly_avglist.append(np.nanmean(tenmin_arg[:,0:prevj+1],axis=1))
            dates_list.append(date_array[:,i])
            time_list.append(sec_vect[i])
        
    hourly_avgArray = np.array(hourly_avglist).T
    time_Array = np.array(time_list)
    dates_Array = np.array(dates_list)
    return hourly_avgArray, time_Array, dates_Array

def hourlyAvg2(sec_vect, arg_array):
    global FillVal
    global timeDim
    global hghtDim
    
    date_array = getDateStamp(sec_vect)
    today = dt.datetime.strftime(date_array[0],'%Y-%m-%d')
    #mon_now = dt.datetime.strftime(date_array[0],'%m')
    #day_now = dt.datetime.strftime(date_array[0],'%d')
    hour_now = dt.datetime.strftime(date_array[0],'%H') # date_array[3,0] + 1 # should start on the next full hour
    
    #tenmin_arg = np.zeros([hghtDim,timeDim])
    tenmin_arg = np.zeros([hghtDim, 6])
    j = 0 # initialize a 10 min step (full day j = 144, watch out for DLS)
    prevj = j
    hourly_avglist = []
    dates_list = []
    time_list = []
    #count = 0
    
    for i in range(len(date_array)):
        # check the date (year-mon-day)
        if(dt.datetime.strftime(date_array[i],'%Y-%m-%d') == today):
            
            # check the hour
            if(dt.datetime.strftime(date_array[i],'%H') == hour_now):
                # Use this to reset on DLS 
                if(j >= 6): j = 0
                        
                tenmin_arg[:,j] = arg_array[:,i]
                        
                #if(count < 20): print(j)
                #count += 1
                prevj = j
                j += 1
                            
                    # new hour. Reset 10m step
            else:
                hour_now = dt.datetime.strftime(date_array[i],'%H')
                i -= 1
                j = 0
                                        
        # new date. Reset 10m step. Capture new day and step back i-1
        else:
            #print(j)
            today = dt.datetime.strftime(date_array[i],'%Y-%m-%d')
                    
            i -= 1
            j = 0
        
        # Catch last step to append last day
        if(i==range(len(date_array))[-1]): j=0 
        
        #if(prevj != j): print("j's don't match", mon_now, day_now)
        if((j==0) & (prevj != j)):
            hourly_avglist.append(np.nanmean(tenmin_arg[:,0:prevj+1],axis=1))
            dates_list.append(date_array[i])
            time_list.append(sec_vect[i])
        
    hourly_avgArray = np.array(hourly_avglist).T
    time_Array = np.array(time_list)
    dates_Array = np.array(dates_list)
    return hourly_avgArray, time_Array, dates_Array

def onTheHourAvg(arg_array, h_ind, dates_array):
    
    onTheHour_avg = np.zeros(24)
    onTheHour_std = np.zeros(24)
    onTheHour_med = np.zeros(24)

    for i in range(0,24):
        
        onTheHour_avg[i] = np.nanmean(arg_array[h_ind, \
                                    np.where(dates_array[:,3] == i)[0]])
        onTheHour_std[i] = np.nanstd(arg_array[h_ind, \
                                    np.where(dates_array[:,3] == i)[0]])
        onTheHour_med[i] = np.nanmedian(arg_array[h_ind, \
                                    np.where(dates_array[:,3] == i)[0]])
        
    return onTheHour_avg, onTheHour_std, onTheHour_med

def onTheHourAvg2(arg_array, h_ind, dates_array):
    
    onTheHour_avg = np.zeros(24)
    onTheHour_std = np.zeros(24)
    onTheHour_med = np.zeros(24)

    for i in range(0,24):
        
        onTheHour_avg[i] = np.nanmean(arg_array[h_ind, \
                                    np.where(dates_array[:,3] == i)[0]])
        onTheHour_std[i] = np.nanstd(arg_array[h_ind, \
                                    np.where(dates_array[:,3] == i)[0]])
        onTheHour_med[i] = np.nanmedian(arg_array[h_ind, \
                                    np.where(dates_array[:,3] == i)[0]])
        
    return onTheHour_avg, onTheHour_std, onTheHour_med

def ontheDayAvg(arg_array, height_array, dates_array):
    
    onTheDay_avg = np.zeros([height_array.size,31])
    onTheDay_med = np.zeros([height_array.size,31])
    onTheDay_std = np.zeros([height_array.size,31])
    
    for i in range(1,32):
        for j in range(height_array.size):
            onTheDay_avg[j,i-1] = np.nanmean(arg_array[j, \
                                    np.where(dates_array[:,2] == i)[0]])
            
            onTheDay_std[j,i-1] = np.nanstd(arg_array[j, \
                                    np.where(dates_array[:,2] == i)[0]])
                
            onTheDay_med[j,i-1] = np.nanmedian(arg_array[j, \
                                    np.where(dates_array[:,2] == i)[0]])
            
    return onTheDay_avg, onTheDay_std, onTheDay_med

def ontheMonAvg(arg_array, height_array, dates_array):
    
    onTheMon_avg = np.zeros([height_array.size,12])
    onTheMon_std = np.zeros([height_array.size,12])
    onTheMon_med = np.zeros([height_array.size,12])

    for i in range(1,13): 
        for j in range(height_array.size):
            onTheMon_avg[j,i-1] = np.nanmean(arg_array[j, \
                                    np.where(dates_array[:,1] == i)[0]])
            
            onTheMon_std[j,i-1] = np.nanstd(arg_array[j, \
                                    np.where(dates_array[:,1] == i)[0]])
                
            onTheMon_med[j,i-1] = np.nanmedian(arg_array[j, \
                                    np.where(dates_array[:,1] == i)[0]])

    return onTheMon_avg, onTheMon_std, onTheMon_med
                
def getMonNames(month_array):
    
    if( month_array[0] > np.min(month_array) ): 
        monNum1 = month_array[0]
   
    else: 
        monNum1 = np.min(month_array)  
    
    if( month_array[-1] == month_array[0] ):
        monNum2 = np.max(month_array)
    
    else:
        monNum2 = month_array[-1]

    # Get 3-char Month string
    monObj1 = dt.datetime.strptime(monNum1.astype(str),'%m')
    monName1 = monObj1.strftime('%b')
    
    monObj2 = dt.datetime.strptime(monNum2.astype(str),'%m')
    monName2 = monObj2.strftime('%b')
    
    monthRange = [monName1, monName2]
    return monthRange 
    
        