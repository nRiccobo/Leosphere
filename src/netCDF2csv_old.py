# Converting NetCDF to csv (recursively)

# 3/9/2022
#
import netCDF4 as nc
import numpy as np
import scipy.stats as s
import datetime as dt
import matplotlib.pyplot as plt
import os

from dirlogger import  ncExist, findUniqueAndDuplicate, ncDump, findMissingDates

## Input Parameters 
datdir='./data'         # File directory where nc files are stored 
#
startDate = 20200925
endDate = 20201231 

FillVal = -9999.0
timeDim = 144       # full length of time dimension in nc file
hghtDim = 12        # full length of height dimension in ncfile

fileNames = ncExist(datdir,False) 
#print(fileNames)
print("Number of Files in", datdir, ":", len(fileNames))

uniqFiles_all, uniqDates_all, uniqPatt_all = findUniqueAndDuplicate(fileNames,False)

# Change working directory
os.chdir(datdir)

def getDateSpan(d1,d2):
        
    # Chance to def function to read in files between d1 and d2
    if(d1 > d2): d2 = d1 
    start = dt.date(int(str(d1)[0:4]),int(str(d1)[4:6]),int(str(d1)[6:8]))
    end   = dt.date(int(str(d2)[0:4]),int(str(d2)[4:6]),int(str(d2)[6:8]))
    delta = end-start
    
    span_set = set(start + dt.timedelta(x) for x in range((delta.days+1)))
    
   #print("Days between dates:", delta.days)
    #return start, end, delta.days
    return sorted(span_set)

span = getDateSpan(startDate,endDate)
print("results from getDateSpan:", list(span)[0], "to", list(span)[-1],len(list(span)),"days")

def getFileSpan(datespan, filedates, files):
    
    startind = filedates.index(datespan[0])
    endind = filedates.index(datespan[-1])
    numfiles = (endind+1)-startind
    #print(range(startind,endind))
    uniqSpan = []*(numfiles)
    for f in range(startind,endind+1):
        uniqSpan.append(files[f])
 
    #print("Files of interest:", uniqSpan)
    return uniqSpan
    #missingDates = findMissingDates(dateSpan,dbg=False)
        
uniqFiles_span = getFileSpan(span,uniqDates_all, uniqFiles_all)
print("results from getFileSpan:", uniqFiles_span[0], "to", uniqFiles_span[-1])
print("results from getFileSpan:", len(uniqFiles_span),"files")

def checkDimensions(file,argin,dbg=True):
    global FillVal 
    global timeDim      
    global hghtDim
    
    # Parameters to filter data 
    #filename=datdir + '/lidar.z06.a0.20210921.001000.sta.a2e.nc'
    #filename=datdir + '/lidar.z06.a0.20200926.001000.sta.a2e.nc'
    #filename = datdir + '/' + file
#    print(re.findall(pattern, uniqFiles))
    ds = nc.Dataset(file)
# Isolate the time group and assign to local variables and Expand to matrix
# Input Time Format: seconds since 1970-01-01
# Output Date Format: YYYY-MM-DD HH:MM:SS   (Ex: 2020-10-03 18:30:00) 
    dbgTime = False
    sizeT = ds.dimensions['time'].size
    tSec = np.zeros([sizeT])
    
    if(dbgTime): print("Date and Time:")
    
    for t in range(sizeT):
        tSec[t] = ds['time'][t]

    dbgHght = False
    sizeH = ds.dimensions['height'].size
    aslH = np.zeros([sizeH])

    for h in range(sizeH):
        aslH[h] = ds['height'][h]

    if(dbgHght): print("Height:", aslH)
    #print("height array:" aslH[:])
 
    #print(ds[argin].shape)
    arg = np.zeros([ds[argin].shape[0],ds[argin].shape[1]])
    for i in range(sizeT): 
        arg[i,:] = ds[argin][i]
        
        for j in range(sizeH):

            if(arg[i,j]==FillVal):
                arg[i,j]=np.nan
    
    if(dbg):    
        if(sizeT < timeDim):   
            print(sizeT)
            print("File",file,"has incomplete time series\n")
            
        if(sizeH < hghtDim):
            print(sizeH)
            print("File",file,"has incomplete height series\n")
            
    return tSec, aslH, arg

#print(uniqFiles_span[1])
#tsize, hsize,argsize = checkDimensions(uniqFiles_span[0],'wind_speed')
#print(tsize)
#print(heights.size)
#print(argsize)

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

    print(dtStamp[0],dtStamp[-1]) 
    #print("year:", ymdHMS[0,:])
    #print("hour", ymdHMS[3,:])
    #print(tStamp[1].year)
    return tExpd 

#tSeparated = separateTime(tStamp)

def combineFileSpan(files,argin,hubh):
    global timeDim
    global hghtDim
    
    argvstime = np.zeros([len(files),timeDim])
    argvshght = np.zeros([len(files),hghtDim])
    
    filesvstime = np.zeros([len(files),timeDim])
    filesvsheight = np.zeros([len(files),hghtDim])
    for e in range(len(files)):
        ds = nc.Dataset(files[e])
        #print(files[e])

        tdim, hdim, arg = checkDimensions(files[e],argin)

        hhi = np.where(ds['height'][:] == hubh)[0]
        #ti = np.where(ds['time'][:] == )    
        for i in range(tdim.size):
            argvstime[e,i] = arg[i,hhi[0]]
            filesvstime[e,i] = ds['time'][i]
        #print(argvstime)
        
        for j in range(hdim.size):
            #argvshght[e,j] = arg[ti[0],j]
            filesvsheight[e,j] = ds['height'][j]

    return filesvstime, filesvsheight, argvstime, argvshght


# Plotting Histogram of Wind Speeds and Weibull Distribution 
#
WsSummaryFile = '../WS_filt_'+ str(startDate) + '_' + str(endDate) + '.csv'

#if (os.path.exists(WsSummaryFile)):
#    print('Wind Speed Summary File exists')
#else:
timeArray, heightArray, \
        WsAtHubvsTime, WsAtHubvsHeight = \
            combineFileSpan(uniqFiles_span,'wind_speed',120.0)
            
separateTime(timeArray[1,:])

WsHvsTime_flat_sorted = WsAtHubvsTime.flatten()[np.argsort(WsAtHubvsTime.flatten())]
WsAtHubvsTime_nonan = WsHvsTime_flat_sorted[~np.isnan(WsHvsTime_flat_sorted)]
WsAtHubvsTime_cutin = WsAtHubvsTime_nonan[np.where(WsAtHubvsTime_nonan >=3.0)]

#np.savetxt(WsSummarFile, WsAtHubvsTime_cutin,delimiter=",")
wShape, wLoc, wScale = s.weibull_min.fit(WsAtHubvsTime_cutin,floc=0)
print("Weibull Shape: %.2f" % wShape)
print("Weibull Scale: %.2f" % wScale)
plt.plot(WsAtHubvsTime_cutin, \
          s.weibull_min.pdf(WsAtHubvsTime_cutin, \
           *s.weibull_min.fit(WsAtHubvsTime_cutin, floc=0)))
plt.hist(WsAtHubvsTime_cutin, bins=25, density=True, edgecolor='black')
plt.title('Histogram: Wind Speed')
plt.xlabel('Wind Speed (m/s)')
plt.show() 




#for x in range(timeArray.shape[0]):
#plt.plot(timeArray[5,:],np.transpose(WsAtHubvsTime[5,:]))
#plt.plot(np.linspace(0,25,1),aslH[np.where(aslH==hubHt)[0]],'--r')
#lt.xticks([tExpd[3,:])
#plt.xlabel('Time (sec)')
#plt.ylabel('Wind Speed (m/s)')
#plt.title('Wind Speed vs Time:')


# Calculate Wind Resource 
#def calcWindResource(files,argin,ht=80.0):
    # Input Parameters
    # d1 = start day 8digit date (Ex: 20200919)
    # d2 = end day   8digit date (Ex: 20210919)
    # argin = argument input string (Ex: 'wind_direction' )
    # ht = hub height (meters) (default=80.0)
    #

#    print("Showing", argin,"data")
#    print("From:", dstart, "\tTo:", dend)
    
    #for e in files: 
        
    #dstart, dend, ddelta = spanOfDates(d1, d2)
#    print("Span of days:", ddelta.days)
    #processUniqFiles(str(d1), uniqFiles, uniqDates)
    # Take two date span and locate unique files and missing files
    # Use two consectutive files to build argument array with time array 
    # Height array is the same
#    day = 0
 #   while day < ddelta.days :
        #print(day)
 #       day +=1 

    

                
    #Arg_avg = np.nanmean(Arg_all)
    
    #hubh = np.where(aslH==ht)
    #print(np.where(aslH==ht)[0])
#    print(Arg_all[~np.isnan(Arg_all)].mean())
#    print(np.nanmean(Arg_all))
#    #print(Arg_all.shape)
#    print("Hub Height (m):", ht )
#    return np.transpose(Arg_all)
  
#X = calcWindResource(uniqFiles_span,'wind_speed', hubHt)
#for

#Y = calcWindResource(20200917,20211019,'data_availability', hubHt)
#print("size of DA",Y.shape)
#print("size of tsec",ds['time'])
#plt.contourf(tSec,aslH,np.transpose(Y))
#plt.title(argin)
#lt.colorbar()
#plt.show()
#print(wspd[10,:])
#print(ds['time'][1])
            # set to 12 for every two hours, 6 for every hour
            #if(i%12 == 0):
                #continue # plt.plot(wspd[i,:],ds['height'][:])
#print(ds['wind_speed'].shape)
#print('qc data availability')
#print(avail)
#print(ws.shape)

#print(ds.variables)

#for loop to plot multiple time steps
#
#plt.plot(ds['time'][:], Arg[:,4])

#lt.xticks([tExpd[3,:])
#plt.xlabel('Wind Speed (m/s)')
#plt.xlim([5,25])
#plt.ylabel('Height (m)')
#plt.title('Wind Speed:')

#plt.contourf(tExpd[3,:],aslH,np.transpose(wspd))
#plt.contourf(ds['time'][:],ds['height'][:],np.transpose(wspd))
#print(ds['time'][:].size)
#print(tExpd[3,:].size)
#print(wspd[:,:])
#plt.title(argin)
#plt.colorbar()
#plt.show()
#np.savetxt('20201003_mb.csv',ws)



# Old print stuff 
#print(ds.dimensions)
#print(ds.variables)
#print(ds.__dict__)

#print("printing dimensions\n")
#print(ds.dimensions.values())
#print("size of height", sizeH)

#print("size of time", sizeT)

#print("printing vars\n")
#print(ds.variables)

#print(tSeparated[0,1])
# Isolate the height group and assign to local variables
# Capture data based on argument inputs and plot
#argin = 'wind_speed'
#argin = ['data_availability','wind_speed','wind_direction'] 
# avail = np.zeros([sizeT,sizeH])

def checkDimensions(dsfile,argin,dbg=True):
    global FillVal 
    global timeDim      
    global hghtDim

    ds = nc.Dataset(dsfile)

    dbgTime = False
    sizeT = ds.dimensions['time'].size
    tSec = np.zeros([sizeT])
    
    if(dbgTime): print("Date and Time:")
    
    for t in range(sizeT):
        tSec[t] = ds['time'][t]

    dbgHght = False
    sizeH = ds.dimensions['height'].size
    aslH = np.zeros([sizeH])

    for h in range(sizeH):
        aslH[h] = ds['height'][h]

    if(dbgHght): print("Height:", aslH)
 
    arg = np.zeros([ds[argin].shape[0],ds[argin].shape[1]])
    for i in range(sizeT): 
        arg[i,:] = ds[argin][i]
        
        for j in range(sizeH):

            if(arg[i,j]==FillVal):
                arg[i,j]=np.nan
    
    if(dbg):    
        if(sizeT < timeDim):   
            print(sizeT)
            print("File",dsfile,"has incomplete time series\n")
            
        if(sizeH < hghtDim):
            print(sizeH)
            print("File",dsfile,"has incomplete height series\n")
            
    return tSec, aslH, arg

def combineFileSpan(files,argin,hubh):
    global timeDim
    global hghtDim
    
    argvstime = np.zeros([len(files),timeDim])
    argvshght = np.zeros([len(files),hghtDim])
    
    filesvstime = np.zeros([len(files),timeDim])
    filesvsheight = np.zeros([len(files),hghtDim])

    for e in range(len(files)):
        ds = nc.Dataset(files[e])

        tdim, hdim, arg = checkDimensions(files[e],argin)

        hhi = np.where(ds['height'][:] == hubh)[0]
        #ti = np.where(ds['time'][:] == )    
        for i in range(tdim.size):
            argvstime[e,i] = arg[i,hhi[0]]
            filesvstime[e,i] = ds['time'][i]
        #print(argvstime)
        
        for j in range(hdim.size):
            #argvshght[e,j] = arg[ti[0],j]
            filesvsheight[e,j] = ds['height'][j]

    return filesvstime, argvstime