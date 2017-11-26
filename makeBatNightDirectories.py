#!/usr/lib/python3.2

# General description:
# This will prepare your bat recordings for further automatic data processing, e.g. with SCAN'R
# creating a consistent directory structure for each bat observation night
# bat nights are organized in bat observation sites
# recordings are moved preserving original file timestamps

# Organisation: BI Rettet den Wollenberg e.V. see http://bi-wollenberg.org/ (German site)
# Author      : FVG - ffhmonitor@gmail.com

# Tested on Linux Mint 17.3 Rosa and on Mac OS X 10.7.5
# Works with both Bat-Pi Versions (Bat-Piv1, 2015 and Bat-Piv2, 2016)
# See http://www.bat-pi.eu/ for more information

#--------------------------------------------------------------------------------
# Inputs expected:
#--------------------------------------------------------------------------------
# 1) a command line parameter with a site name where the bat observation was made. Example:
# makeBatNightDirectories.py home-monitor
#
# 2)typical output paths of the Bat-Pi and a supplemental ENVLOG.TXT, a comma separated file with temperatures
# Bat-Piv1
# - /out
# - /out/ENVLOG.TXT
#
# Bat-Piv2
# - /etc/batpi
# - /out
# - /out/ENVLOG.TXT
#--------------------------------------------------------------------------------

#--------------------------------------------------------------------------------
# Outputs
#--------------------------------------------------------------------------------
# Creates a directory for the site name
# move recordings in sub directories - one subdirectory for each bat observation night
# move invalid recordings to a subdirectory
# move log files to a subdirectory
# copy all available metadata to their sub directories, preserving Bat-Pi directory structure
#--------------------------------------------------------------------------------

# This file is on GitHub: https://github.com/ffhmon/bat-project/makeBatNightDirectories.py
# Licence: GNU General Public Licence v3

# Script history:
# 20171126 - Version 1.0

#----------------------------------------------------------------------------------
def parseWavFileDateTime(wavFileName):
        returnValue = 0
        try:
                theYear = int(wavFileName[10:14])
                theMonth = int(wavFileName[14:16])
                theDay = int(wavFileName[16:18])
                theHour = int(wavFileName[19:21])
                theMinute = int(wavFileName[21:23])
                theSecond = int(wavFileName[23:25])
                theDateTime = datetime.datetime(theYear, theMonth, theDay, theHour, theMinute, theSecond)
                
                returnValue = dict(wavYear=theYear, wavMonth=theMonth, wavDay=theDay, \
                    wavHour=theHour, wavMinute=theMinute, wavSecond = theSecond, \
                    wavDateTime=theDateTime)

        except:
                print('Error parsing date time values from wav file name.')
                
        return returnValue

# ==================================================================================================================
# Main program
# ==================================================================================================================

import datetime, glob, linecache, os, sys
from shutil import copyfile

# default variables - can be changed by sys.argv ###

# default base path - user's working directory
basePath = os.getcwd() + '/'
siteName = ''

### parse command line args
try:    
    args = (len(sys.argv))

    if (args!=2):
        raise ValueError('Missing site name argument.')
    else:
        candidateSiteName = str(sys.argv[1])
        if candidateSiteName != '':
            siteName = candidateSiteName.replace('/','')

except Exception as error:
    print("Invalid command arguments. Usage: makeBatNightDirectories.py <site name>")
    print (siteName)
    sys.exit(1)
    
print ("Base path: " + basePath)
print ("Site name: " + siteName)
print('----------------------------------------------------------------')

try:
    # set input directory an check if there is anything to process
    piRawDataPath = basePath + "out/data/"

    if not os.path.exists(piRawDataPath):
        print('Sorry, can not find the Bat-Pi raw data input directory:')
        print(piRawDataPath)
        sys.exit(1)

except:
    print("Error accessing Bat-Pi files.")
    sys.exit(1)

try:
    # see if there are any valid wav files
    wavFiles = glob.glob(piRawDataPath + "*.wav")
    wavNumber=0
    for index, item in enumerate(wavFiles):
        with open(wavFiles[index]) as wav:
            wav.seek(0, os.SEEK_END)
            wavSize=wav.tell()
            if wavSize > 1000:
                if "-N-" in wavFiles[index]:
                    wavNumber=wavNumber+1

except:
    print("Error reading Bat Pi *.wav")
    sys.exit(1)

try:
    # if no recordings found, there is nothing to do
    if wavNumber==0:
        print('Sorry, no recordings found. Nothing to do here. Bye now.')
        sys.exit(2)

    # create site directory if not exist
    if not os.path.exists(basePath + siteName):
            os.makedirs(basePath + siteName)

    # move everything to the new directory
    theFiles = glob.glob(basePath + "*.*")
    for index, item in enumerate(theFiles):
        theFile = os.path.basename(item)
        os.rename(item, basePath + siteName + '/' + theFile)
    os.rename(basePath + 'out', basePath + siteName + '/out')
    if os.path.exists(basePath + "etc/batpi"):    #only batpiv2 has /etc/batpi
        os.rename(basePath + 'etc', basePath + siteName + '/etc')

    # set a new base path and create a file for the site
    basePath = basePath + siteName + '/'
    fTXT = open(basePath + 'SITE.TXT', 'w')
    fTXT.write(siteName)
    fTXT.close()

except:
    print("Unexpected error creating output directory for the site.")
    sys.exit(1)

try:

    # read invalid recordings (wav file is smaller as 1000 bytes) from the new base path
    wavNumber=0
    wavFiles = glob.glob(basePath + "out/data/*.wav")
    invalidWavFiles = list()
    for index, item in enumerate(wavFiles):
        with open(wavFiles[index]) as wav:
            wav.seek(0, os.SEEK_END)
            wavSize=wav.tell()
            if wavSize < 1000:
                invalidWavFiles.append(item)
                wavNumber=wavNumber+1
    print (str(wavNumber) + ' invalid wav files.')

    # move invalid recordings if any
    if wavNumber > 0:
        # create output directory if not exist
        if not os.path.exists(basePath + "out/data/invalid-wav"):
            os.makedirs(basePath + "out/data/invalid-wav")
        for index, item in enumerate(invalidWavFiles):
            currentWav = os.path.basename(item)
            os.rename(item, basePath + "out/data/invalid-wav/" + currentWav)
            print(currentWav + ' --> moved to invalid-wav path')

except:
    print("Error processing invalid Bat Pi *.wav data.")
    sys.exit()

print('----------------------------------------------------------------')

try:
    # see if there are log files, move them if any

    logFiles = glob.glob(basePath + "out/data/*.log*")
    print (str(len(logFiles)) + ' log files.')
    if (len(logFiles)) > 0:
        # create output directory if not exist
        if not os.path.exists(basePath + "out/data/logs"):
            os.makedirs(basePath + "out/data/logs")
        for index, item in enumerate(logFiles):
            currentLog = os.path.basename(item)
            os.rename(item, basePath + "out/data/logs/" + currentLog)
            print(currentLog + ' --> moved to logs path')
except:
    print("Error processing Bat Pi log files.")
    sys.exit()

print('----------------------------------------------------------------')

try:

    # now read actual wav files from the new base path
    wavNumber = 0
    wavFiles = glob.glob(basePath + "out/data/*.wav")
    validWavFiles = list()
    for index, item in enumerate(wavFiles):
        with open(wavFiles[index]) as wav:
            wav.seek(0, os.SEEK_END)
            wavSize = wav.tell()
            if wavSize > 1000:
                if "-N-" in wavFiles[index]:
                    validWavFiles.append(item)
                    wavNumber = wavNumber + 1
    print (str(wavNumber) + ' valid wav files found.')

except:
    print("Error reading Bat Pi *.wav data.")
    sys.exit()
    
print('----------------------------------------------------------------')
print('Reading a bunch of files. This may take some time. Please hang on...')
print('====================================================================')

batNights = list()
processedFiles = 0
processedNights = 0
lastBatNight = ""

validWavFiles.sort()

try:
    for wavFile in validWavFiles:

            currentWav = os.path.basename(wavFile)

            wavFileDateElements = parseWavFileDateTime(currentWav)
            theWavDateTime = wavFileDateElements['wavDateTime']


            if (wavFileDateElements['wavHour']) < 12:
                theBatNight = theWavDateTime - datetime.timedelta(days = 1)
            else:
                theBatNight = theWavDateTime

            currentBatNight = theBatNight.strftime("%Y%m%d")

            if (lastBatNight!=currentBatNight):
                batNights.append(currentBatNight)
                lastBatNight = currentBatNight
                processedNights = processedNights + 1

            nightPath = basePath + currentBatNight + "/"
            if not os.path.exists(nightPath):
                print('Processing bat night: ' + currentBatNight)
                os.makedirs(nightPath)
                os.makedirs(nightPath + 'out')
                os.makedirs(nightPath + 'out/data')

                # copy environment file - if found
                if os.path.exists(basePath + 'ENVLOG.TXT'):
                    copyfile(basePath + 'ENVLOG.TXT', nightPath + 'ENVLOG.TXT')

                # copy site name file - if found
                if os.path.exists(basePath + 'SITE.TXT'):
                    copyfile(basePath + 'SITE.TXT', nightPath + 'SITE.TXT')

                # copy log data to the bat night - if found
                os.makedirs(nightPath + 'out/data/logs')
                if os.path.exists(basePath + 'out/data/logs'):
                    theFiles = glob.glob(basePath + "out/data/logs/*.*")
                    for index, item in enumerate(theFiles):
                        theFile = os.path.basename(item)
                        copyfile(item, nightPath + 'out/data/logs/' + theFile)

                # copy gps data to the bat night - if found
                os.makedirs(nightPath + 'out/data/gps')
                if os.path.exists(basePath + 'out/data/gps'):
                    theFiles = glob.glob(basePath + "out/data/gps/*.*")
                    for index, item in enumerate(theFiles):
                        theFile = os.path.basename(item)
                        copyfile(item, nightPath + 'out/data/gps/' + theFile)

                # copy settings directory for batpi v1 - if found
                os.makedirs(nightPath + 'out/bin')
                if os.path.exists(basePath + 'out/bin'):
                    theFiles = glob.glob(basePath + "out/bin/*.*")
                    for index, item in enumerate(theFiles):
                        theFile = os.path.basename(item)
                        copyfile(item, nightPath + 'out/bin/' + theFile)

                # copy setting directories for batpi v2 - if found
                os.makedirs(nightPath + 'etc/batpi')
                if os.path.exists(basePath + "etc"):
                    theFiles = glob.glob(basePath + "etc/batpi/*.*")
                    for index, item in enumerate(theFiles):
                        theFile = os.path.basename(item)
                        copyfile(item, nightPath + 'etc/batpi/' + theFile)

            # copyfile(wavFile,nightPath + 'out/data/' + currentWav) - copying files would result in changed time stamps and occupies a lot of disk space
            os.rename(wavFile, nightPath + 'out/data/' + currentWav)    # moving the wav-files is the better solution

            processedFiles = processedFiles +1
except:
        print('Error reading recording files.')

print('----------------------------------------------------------------')
print (str(processedFiles) + ' files processed, ' + str(processedNights) + ' bat nights found.')
print('----------------------------------------------------------------')
print('All done. Bye now.')
