#!/usr/lib/python3.2

#-------------------------------------------------------------------------------------
# Script for processing screenshot (BMP) files from a SSF BAT3 detector
# (See http://www.mekv.de/bat3/index.htm for information on the bat detector)
# What the script does:
# - renames BMP files to meaningfull YYYYMMDD-HHmmss names
# - converts BMP format to valid JPG files and sets EXIF data to correct picture time stamp
# - optionally the script can use a temperature / humidity data logger file 
# - the script can use GPX files and use them for georeferencing 
#   The code was written for GPX files from a Bat Pi recorder
#   GPX from other devices may work as well but the code might need some adaptation
#   For more information on the Raspberry Pi Bat Project please refer to
#   http://www.fledermausschutz.de/forschen/fledermausrufe-aufnehmen/raspberry-pi-bat-project/
#-------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------
# runs on Linux only!
# - since file time stamps are not correctly processed with Python on Windows
# - there are dependencies on ImageMagick and ExifTools Packages
#-------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------
# optional script parameter: base path for all input files. valid paths can be:
# - a subdirectory name of the working directory
# - or a full path on the system
#-------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------
# the script expects directory structure, please make sure that this directories exist:
# <base path>/detector      <--- contains input BMP files from SSF BAT3 (e.g. SCREEN0.BMP etc)
# <base path>/out/data/gps  <--- contains input GPX files from a Bat Pi recorder
#-------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------
# the script expects following clear text files
#
#
# <base path>/ENVLOG.TXT    <--- environment log file from a data logger
# (our data logger is an Arduino Device logging temperature and humidity every 10 minutes)
# Example data format (Date; Time; Temperature; Humidity) :
#    23.9.2016;18:30;21.00;43.00
#    23.9.2016;18:40;22.00;41.00
#
# <base path>/detector/ssf3.txt      <--- archives base settings of a SSF3 Bat bat detector
# Example data format - change it to reflect actual settings during bat session
#   Make:microelectronic Volkmann
#   Detector:SSF BAT3
#   FirmwareVer:0.99
#   FirmwareRev:01
#   Serial:121600239
#   Speaker Boost:1
#   Squelch:2
#   Line out:+0
#   Display Light:7
#   Display Dim:1
#   Eco:30 min
#   Wake:Bat+Key
#   AutoOff:60
#   AutoBat:Fast
#   Level:7
#-------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------
# tasks performed:
# - Read correct screenshot time stamps 
# - Convert BMP file format to JPG file format
# - write EXIF data and correct time stamps to the JPG files
# - georeference screenshots using the gpx file from a Raspberry Pi Bat Recorder
# - read logged temperature / humidity values with timestamp from a ENVLOG.TXT file
#   Format: D.M.Y;H:MM;T;H
# - write a CSV file with georeferenced screenshots and temperatures 
# - write a KML file with georeferenced screenshots for later use within QGIS 
#-------------------------------------------------------------------------------------


#-------------------------------------------------------------------------------------
# Author Fred Van Gestel, BI Rettet den Wollenberg e.V.
# Version 1.2
# 18 October 2016
# Licence: GNU General Public Licence
#-------------------------------------------------------------------------------------

import datetime, glob, linecache, os, sys, getopt, time

# function - gets original file time stamp (linux only)
def modification_date(filename):
    t = os.path.getmtime(filename)
    return datetime.datetime.fromtimestamp(t)

#-------------------------------------------------------------------------------------
# Important: set following parameters as required
#-------------------------------------------------------------------------------------

# set general EXIF data as required
exifCopyright = "CC BY-NC (Creative Commons Attribution-NonCommercial license)"
exifArtist ="BI Rettet den Wollenberg e.V."

# set UTC time correction in hours for time calculation from UTC. 
# For Germany, set this to 1 during winter time, 2 during summer time
utcTimeCorrection = 2

# default base path for raw input data files used
# change this to your own 
basePath = os.getcwd() + '/'

#-------------------------------------------------------------------------------------

# check if user passed his own new base path
args = (len(sys.argv))
if args > 1:
    candidatePath = sys.argv[1]
    if not os.path.exists(candidatePath):
        # maybe user just entered a new sub dir
        if not os.path.exists(basePath + candidatePath):
            print ("Given base path not found. Trying default path.")
        else:
            basePath = basePath + candidatePath + "/"
    else:
        basePath = candidatePath + "/"

print ("Using base path: " + basePath)

# set working directories 
baseDataPath = basePath + "detector/"
baseGpsPath  = basePath + "out/data/gps/"
outputPath = basePath + "reports/"

# paths for the input files
bmpFiles = glob.glob(baseDataPath + "*.*")
gpxFiles = glob.glob(baseGpsPath + "*.gpx")
settingsFile = baseDataPath + "ssf3.txt"
environmentFile = basePath + "ENVLOG.TXT"



# see if all paths exist
if not os.path.exists(baseDataPath):
    print('Sorry, can not find data directory. Check base path and try again.')
    print('Hint: you can pass a valid base path by calling ')
    print (sys.argv[0] +  " <new/base/path>")
    sys.exit()

if not os.path.exists(baseGpsPath):
    print('Sorry, can not find GPS directory. Check path and try again.')
    sys.exit()

if not os.path.exists(settingsFile):
    print('Sorry, can not find SSF3 Detector settings. Check path and try again.')
    sys.exit()

# seems like everything's ok -
# create output directory if it does not exist
if not os.path.exists(outputPath):
    os.makedirs(outputPath)

# and create an new empty output file with headers in it
outputCsv = outputPath + 'detector.csv'
fCsv = open(outputCsv, 'w')
fCsv.write("ScreenshotDate;ScreenshotTime;JpgFileName;Temperature;Latitude;Longitude;Altitude;HDOP;detectorType;detectorFirmware;detectorFirmwareRev;detectorSerial;detectorAutoBat;detectorLevel\n")
fCsv.close()

# get current SSF3 settings
with open(settingsFile) as batDetector:
    for i, line in enumerate(batDetector):
        pos1=line.find(':')+1
        pos2=len(line)-1
        if 'Make' in line:            
            detectorMake = line[pos1:pos2]
        if 'Detector' in line:            
            detectorType = line[pos1:pos2]
        if 'FirmwareVer' in line:
            detectorFirmware = line[pos1:pos2]
        if 'FirmwareRev' in line:
            detectorFirmwareRev = line[pos1:pos2]
        if 'Serial' in line:
            detectorSerial = line[pos1:pos2]
        if 'AutoBat' in line:
            detectorAutoBat = line[pos1:pos2]
        if 'Level' in line:
            detectorLevel = line[pos1:pos2]

# and inform user 
print(detectorType + " v" + detectorFirmware + " Rev" + detectorFirmwareRev + " SN:" + detectorSerial)
print('---------------------------------------')

# see if there are valid bitmap files (file is bigger as 1000 bytes and contains the bmp string)
bmpNumber=0
validBmpFiles = list()
for index, item in enumerate(bmpFiles):
    with open(bmpFiles[index]) as bmp:
        bmp.seek(0, os.SEEK_END)
        bmpSize=bmp.tell()
        if bmpSize > 1000:
            if ".bmp" in bmpFiles[index].lower() :
                validBmpFiles.append(item)
                bmpNumber=bmpNumber+1                
print (str(bmpNumber) + ' valid bmp file(s).')

# see if there are GPS data logged (gpx file is bigger as 398 bytes)
gpxNumber=0
validGpxFiles = list()
for index, item in enumerate(gpxFiles):
    with open(gpxFiles[index]) as gpx:
        gpx.seek(0, os.SEEK_END)
        gpxSize=gpx.tell()
        if gpxSize > 398:
            points=list()            
            validGpxFiles.append(item)
            gpxNumber=gpxNumber+1            
print (str(gpxNumber) + ' valid gpx file(s).')

# see if there is a temperature log
if not os.path.exists(environmentFile):
    print('No ENVLOG.TXT found.')
else:
    print('ENVLOG.TXT found.')

print('---------------------------------------')
    
# if no BMP found, there is nothing to do
if bmpNumber==0:
    print('Sorry, nothing to do here. Bye now.')
    sys.exit()

print('Converting / georeferencing ' + str(bmpNumber) + ' detector files. Please hang on...')
print('---------------------------------------')

processedFiles = 0
referenced = list()
validBmpFiles.sort()

for bmpFile in validBmpFiles:

    # store original file name, date and time for later use in the csv outputs
    d = modification_date(bmpFile)
    originalFile = os.path.basename(bmpFile)
    originalFileDate = ("%04d-%02d-%02d" % (d.year, d.month, d.day))
    originalFileTime = ("%02d:%02d" % (d.hour, d.minute))

    # rename each BMP file to meaningfull date-time string.
    # get the original file date for this (only possible on Linux hosts!)    
    newFileName = ("%04d%02d%02d_%02d%02d%02d" % (d.year, d.month, d.day, d.hour, d.minute, d.second))
    os.rename(bmpFile, baseDataPath + newFileName + ".bmp")

    # convert the BMP screenshot to a jpg file, using mogrify command
    # this command needs ImageMagick package installed
    os.system("mogrify -format jpg " + baseDataPath + newFileName + ".bmp")    

    # compose and set EXIF metadata of the new picture
    # this command needs exiftools package installed
    exifString = ("%04d%02d%02d%02d%02d%02d" % (d.year, d.month, d.day, d.hour, d.minute, d.second))        
    os.system("exiftool -alldates=" + exifString + " " + baseDataPath + newFileName + ".jpg")
    os.system("exiftool -copyright='" + exifCopyright + "' " + baseDataPath + newFileName + ".jpg")
    os.system("exiftool -artist='" + exifArtist + "' " + baseDataPath + newFileName + ".jpg")
    os.system("exiftool -make='" + detectorMake + "' " + baseDataPath + newFileName + ".jpg")
    os.system("exiftool -model='" + detectorType +"' " + baseDataPath + newFileName + ".jpg")
    

    currentJpg = newFileName + ".jpg"

     # make UTC timestamp
    jpgYear=(currentJpg[0:4])
    jpgMonth=(currentJpg[4:6])
    jpgDay=(currentJpg[6:8])
    jpgHour=(currentJpg[9:11])
    jpgMinute=(currentJpg[11:13])
    jpgSecond=(currentJpg[13:15])

    jpgDateTime = datetime.datetime(int(jpgYear), int(jpgMonth), int(jpgDay), int(jpgHour), int(jpgMinute), int(jpgSecond))
    jpgDateTime = jpgDateTime - datetime.timedelta(hours=utcTimeCorrection)

    # get temperature from environment file
    # if no valid temperature can be found, we use 99 and create an empty temperature string afterwards
    tempTemperature = 99
    if os.path.exists(environmentFile):
        with open (environmentFile) as tempFile:
            for t, tline in enumerate(tempFile):
                pos1=tline.find('.')
                tempDay=tline[0:pos1]
                
                pos2=tline.find('.',pos1+1)
                tempMonth=tline[pos1+1:pos2]

                pos3=tline.find(';')
                tempYear=tline[pos2+1:pos3]

                pos4=tline.find(':',pos3)
                tempHour=tline[pos3+1:pos4]

                pos5=tline.find(';',pos4)
                tempMinute=tline[pos4+1:pos5]                
                if int(tempMinute) == 50:
                    tempMinute="59"

                tempDateTime=datetime.datetime(int(tempYear), int(tempMonth), int(tempDay), int(tempHour), int(tempMinute), 0)
                tempDateTime= tempDateTime - datetime.timedelta(hours=utcTimeCorrection)
                if int(tempDay) == int(jpgDay):                    
                    if int(tempMonth) == int(jpgMonth):                        
                        if int(jpgYear) == int(tempYear):                        
                            if int(tempHour) == int(jpgHour):                                
                                if int(tempMinute) >= int(jpgMinute):                                    
                                    pos6=tline.find(';',pos5)
                                    pos7=tline.find(';',pos6+1)
                                    tempTemperature=tline[pos6+1:pos7]                                      
                                    break;

    theTemperature = str(round(float(tempTemperature)))
    if tempTemperature == 99:
        theTemperature=""

    # try to georeference the screenshot
    gpsTimeString = jpgHour + ":" + jpgMinute + ":" + jpgSecond + "+" + str(utcTimeCorrection) + "h"

    jpgTimeUpper=jpgDateTime + datetime.timedelta(seconds=5)
    jpgTimeLower=jpgDateTime - datetime.timedelta(seconds=5)
    
    jpgDate=jpgYear+jpgMonth+jpgDay
    jpgTime=jpgHour+jpgMinute+jpgSecond

    found=0
    
    for currentGpx in validGpxFiles:        
        with open (currentGpx) as gpxf:
            points=list()
            for i, line in enumerate(gpxf):
                if '<trkpt' in line:
                    points.append(i+1)
        for index, pitem in enumerate(points):

            lat = ""
            long = ""
            altitude = ""
            hdop = ""
            gpsTime = ""

            trackpoint=linecache.getline(currentGpx,pitem)
            elevation=linecache.getline(currentGpx,pitem+1)
            timestamp=linecache.getline(currentGpx,pitem+2)
            hdopString=linecache.getline(currentGpx,pitem+6)

            if '<time>' in timestamp:
                if '</time>' in timestamp:
                    yearString=timestamp[10:14]
                    monthString=timestamp[15:17]
                    dayString=timestamp[18:20]
                    hourString=timestamp[21:23]
                    minuteString=timestamp[24:26]
                    secondString=timestamp[27:29]

                    pointDateTime=datetime.datetime(int(yearString), int(monthString), int(dayString), int(hourString), int(minuteString), int(secondString))

                    if pointDateTime<jpgTimeUpper and pointDateTime>jpgTimeLower:
          
                        lat = trackpoint[15:24]
                        long = trackpoint[31:39]
                        altitude = elevation[9:19]
                        hdop = hdopString[10:13]
                        gpsTime = timestamp[21:29]+ "+" + str(utcTimeCorrection) + "h"                                            

                        referenced.append([currentJpg,lat,long,altitude])
                        processedFiles=processedFiles+1                                                            
                        break
    

    # output some feedback to the screen and the output file
    outputString1 =  originalFileDate + ";" + originalFileTime + ";" + currentJpg + ";" + theTemperature + ";" + lat + ";" + long + ";" + altitude + ";" + hdop
    outputString = outputString1 + ";" + detectorType+ ";" + detectorFirmware + ";" + detectorFirmwareRev + ";" + detectorSerial + ";" + detectorAutoBat + ";" + detectorLevel
    print (outputString1)

    # write to the csv
    fCsv = open(outputCsv, 'a')
    fCsv.write(outputString + "\n")
    fCsv.close()

print('---------------------------------------')

# now build a kml file from mulidimensional array with referenced files
if gpxNumber!=0:
    currentKml = outputPath + 'detector-session.kml'

    fKml = open(currentKml, 'w')
    fKml.write("<?xml version='1.0' encoding='UTF-8'?>\n")
    fKml.write("<kml>\n")        
    fKml.write("<Document>\n")
    fKml.write("    <name>" + currentKml +"</name>\n")
    for geoPoint in referenced:
        fKml.write("   <Placemark>\n")
        fKml.write("       <name>" + geoPoint[0] + "</name>\n")
        fKml.write("       <description>" + str(jpgDateTime) +  "</description>\n")
        fKml.write("       <Point>\n")
        fKml.write("           <coordinates>" + geoPoint[2] + "," + geoPoint[1] + "," + geoPoint[3] + "</coordinates>\n")
        fKml.write("       </Point>\n")
        fKml.write("   </Placemark>\n")
    fKml.write("</Document>\n")
    fKml.write("</kml>\n")
    fKml.close()
    print("KML file: " + currentKml)
    
# clean up   
os.system("rm " + baseDataPath + "*.jpg_original")
os.system("rm " + baseDataPath + "*.bmp")

print('---------------------------------------')
print ("All done. " + str(processedFiles) + " files processed. Bye now.")
