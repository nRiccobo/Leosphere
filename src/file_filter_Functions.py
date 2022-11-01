# Locate a data directory and count files then generate log 
#
#
import os 
import re
import datetime as dt
import numpy as np
import netCDF4 as nc

from data_filter_Functions import * 

def fileExist(datdir,ftype):
    fCount = 0
    boolexist = False
    
    for file in os.listdir(datdir):
        if file.endswith(ftype):
            fCount += 1
            if(fCount == 1):
                boolexist = True
                break
        else:
            print("NO %s files exist %s", (ftype,datdir))
            boolexist = False 
            
    return boolexist
            
def getAllFiles(datdir,ftype,ishohdr=False):
    
    fExist = fileExist(datdir,ftype)
    if(fExist):    
        path, dirs, files_all = next(os.walk(datdir)) # "./" + datdir))
    
    file_count = len(files_all)
    print("Number of Files in", datdir, ":", file_count)
    
    return files_all

def ncDump(filename):
# Quick dump of NC header files and variable attributes 
# If all else fails, run ncdump -h *filename* from the commandline 
# while in the file directory. 

   ds = nc.Dataset(filename)
   print(ds)
   print(ds.__dict__) 
   print("\nVariable \t//\t Dimension \t//\t Size")
   
   for var in ds.variables:
        print(var, ' , ',ds.variables[var].dimensions, \
              " , ",ds.variables[var].size)
        
def getUniqueFiles(filelist,shoFiles=False):
    
    #path, dirs, files = next(os.walk("./" + datdir))
    file_count = len(filelist)
    #print(file_count)
    #print("regsearch", re.search(r'\d{8}',filelist[2]).span())
    regspan = re.search(r'\d{8}',filelist[2]).span()
    #print(re.findall('001000', files[2]))

    count=0
    dates_int = np.zeros([file_count]).astype(int)
    
    for f in range(file_count):
# Strip 8-digit date stamp in files' name and create integer array
        #print(str(filelist[f])[regspan[0]:regspan[1]])
        dates_int[f] = int(str(filelist[f])[regspan[0]:regspan[1]])
    
# Find all files with 001000. Assume this is a "good" code. Sanity check for unique files
        if(re.findall('001000',filelist[f])):
            count +=1 
    #print("find all count:",count)

# Find unique date stamps with value, index, count   
    u, ui, nu = np.unique(dates_int, return_index=True, return_counts=True)
    
# Determine, locate, and count duplicates when count was higher than 1
    dup = u[nu>1]
    dupi = ui[nu>1]
    ndup = nu[nu>1]
    #print(dates)
    #print(ui)
    #print(nu)
    #print(dupi)
    #print(ndup)

    uniqPatt = np.zeros([ui.size]).astype(int)
    uniqFiles = []*ui.size
    uniqDates = []*ui.size
    
    for n in range(ui.size):
# Append list of files based on unique index     
        uniqFiles.append(filelist[ui[n]])
            
    if(shoFiles):
        #print("List of Unique Files\n", uniqFiles)
        print("Number of Unique Files: ", len(uniqFiles))
    return uniqFiles # , duplFiles

def getUniqueDates(ufilelist,showDates=False):
    
    file_count = len(ufilelist)
    count=0
    dates_int = np.zeros([file_count]).astype(int)
    uniqDates = []*file_count
    
    for f in range(file_count):
# Strip 8-digit date stamp in files' name and create integer array
        dates_int[f] = int(str(ufilelist[f])[13:21])
        uniqDates.append(dt.date(int(str(dates_int[f])[0:4]), \
                             int(str(dates_int[f])[4:6]), \
                             int(str(dates_int[f])[6:8])))

    #for d in range(dupi.size):
#Split duplicate date stamp into array of integers 
        #duplPatt[d] = dates_int[dupi[d]]

        #duplDates.append(dt.date(int(str(duplPatt[d])[0:4]), \
        #                         int(str(duplPatt[d])[4:6]), \
        #                         int(str(duplPatt[d])[6:8])))     
        
    if(showDates):
        #print("List of Unique Dates\n", uniqDates)
        print("Number of Unique Dates\n", len(uniqDates))
    return uniqDates # , duplDates

def getFileSpan(datespan, ufilelist, showFiles=False):
    
    filedates = getUniqueDates(ufilelist)
    startind = filedates.index(datespan[0])
    endind = filedates.index(datespan[-1])
    numfiles = (endind+1)-startind
    
    uniqFileSpan = []*(numfiles)
    for f in range(startind,endind+1):
        uniqFileSpan.append(ufilelist[f])
 
    #print("Files of interest:", uniqSpan)
    if(showFiles):
        print("Results from getFileSpan:", len(uniqFileSpan),"files")
        print(uniqFileSpan[0], "to", uniqFileSpan[-1])
    return uniqFileSpan

def getMissingFiles(dateSpan, ufilespan, showMiss=False):
   
# Determine the span of data from beginning to end, then determine missing days       
    delta = dateSpan[-1]-dateSpan[0]
    #print("Delta Days:", delta.days)    
    filedates = getUniqueDates(ufilespan)
    date_set = set(dateSpan[0] + dt.timedelta(x) for x in range((dateSpan[-1]-dateSpan[0]).days))
    #print("dateset", date_set)
    #print("filedates", filedates)
    missingDates = sorted(date_set - set(filedates))
    #missingDates = dt.datetime.strftime( list( \
    #                                     sorted(date_set - set(filedates))), \
    #                                      "%Y-%m-%d")
    print("Results from getMissingFiles:", len(missingDates),'files')
    
    missingStrings = [date_obj.strftime('%Y-%m-%d') for date_obj in missingDates]
    if(showMiss):     
        #print(dt.datetime.strftime(missingDates[:],"%Y-%m-%d"))
        print(missingStrings)
        # [date_obj.strftime('%Y%m%d') for date_obj in mondays]
    return missingStrings

def checkSumFile(sumdir, sumfilename):
    boolexist = False
    if (os.path.exists(sumdir + sumfilename)):
        print(sumfilename, 'exists in ', sumdir)
        boolexist = True
    else: 
        print('No Wind Summary file found! ', sumdir)
        boolexist = False
    
    return boolexist 
    
def dumpFileLog(unqFiles, uniqDates, missing, span):
# Dump file log to console    
    print("\n##### Data Log #####")
    print("Total Number of Files:",len(unqFiles)) # +len(dplFiles))
    print("Unique Files:", len(unqFiles))
    #print("Duplicate Files", len(dplFiles)) # 10 doubles and 1 quad = 13 extras
    print("Start Date:",uniqDates[0], "\tEnd Date:", uniqDates[-1], "\tNum of Days:", span.days)
        
    ilogMis=False
    if(ilogMis):
        print("\nMissing Dates:")
        for m in range(len(missing)):
            print(missing[m])
    else: 
        print("\nMissing Dates: Hushed")
            
    ilogDup=False
    #if(ilogDup):
    #    print("\nDuplicate Files:")
    #    for p in range(len(dplFiles)):
    #        print(dplFiles[p]) 
    #else: 
    #    print("\nDuplicate Files: Hushed" )
         
    ilogUni=False
    if(ilogUni):
        print("\nUnique File") 
        for f in range(len(unqFiles)):
            print(unqFiles[f])
    else: 
        print("\nUnique Files: Hushed" )  
        print("\n##### End of Data Log #####\n\n")