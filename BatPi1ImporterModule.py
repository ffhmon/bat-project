# -*- coding: utf-8 -*-
import sys,os,string,time,wave,datetime,shutil,fnmatch,glob,xml.etree.ElementTree as ET
#===============================================================================================
class ConverterModule(object):
	#-------------------------
	def __init__(self, log):
		self.log = log
	#-------------------------
	def info(self, item=None):
		infodict = dict()
		infodict['Name']="Bat-Pi v1 Importer"
		infodict['Version']="1.0"
		infodict['Author']="RBO, adaptation for the Bat-Pi by FVG"
		infodict['Mail']="batscope@wsl.ch"
		infodict['Web']="www.wsl.ch"
		infodict['Notes']="Reads wave files from a /out/data directory created by a Raspberry Bat-Pi v1 (first edition) with a Dodotronic mic. A sub directory /out/data/batscope should contain XML files with metadata for each recording. The device name and recording date must be contained in the filename. Format example: batpi01-N-20160710_003324.wav"
		if item==None:
			return infodict
		else:
			return infodict[item] 
	#-------------------------
	def audioFilePattern(self):
		return "*.wav"
	#-------------------------
	def requiredFileNamePattern(self):
		return "*.wav"
	#-------------------------
	def metaDataList(self, sdcardPath):
		
                dictlist = list()
                
                metadataPath = sdcardPath + "/BatScope/"
                waveFiles = self.getAllFilesByExtension(sdcardPath, "wav")
                
                                                                       
		for wavFilePath in waveFiles:

                        (wfp,wavFile) = os.path.split(wavFilePath)
                        (fileName,fileExtension) = os.path.splitext(wavFile)

       			d = dict()
       			
        		d["FileName"] = wavFile
			d["BatRecBitsPerSample"] = 16
			d["BatRecChannel"] = 1

			wr = wave.open(wavFilePath)
			d["BatRecSampleRate"] = wr.getframerate()
			wr.close()

                        try:

                                xmlFile = metadataPath + fileName + '.xml'
                                tree = ET.parse(xmlFile)
                                root = tree.getroot()
                                
                                d["BatRecDeviceName"] = root.find('BatRecDeviceName').text
                                d["BatRecDate"] = root.find('BatRecDate').text
                                d["BatRecSpeed"] = root.find('BatRecSpeed').text
        			d["BatRecLocationDevice"] = root.find('BatRecLocationDevice').text
                                d["BatRecGPSValid"] = root.find('BatRecGPSValid').text
                                d["BatRecGPSLat"] = root.find('BatRecGPSLat').text
                                d["BatRecGPSLong"] = root.find('BatRecGPSLong').text
                                d["BatRecGPSAltitude"] = root.find('BatRecGPSAltitude').text
                                d["BatRecGPSHDOP"] = root.find('BatRecGPSHDOP').text
                                d["BatRecGPSSatsUsed"] = root.find('BatRecGPSSatsUsed').text
                                d["BatRecTemperature"] = root.find('BatRecTemperature').text
                                d["BatRecDeviceID"] = root.find('BatRecDeviceID').text
                                d["BatRecDeviceFirmware"]  = root.find('BatRecDeviceFirmware').text
        			d["BatRecTriggerCutOffFreqEff"]  = root.find('BatRecTriggerCutOffFreqEff').text
        			d["BatRecPreTriggerTime"]  = root.find('BatRecPreTriggerTime').text
        			d["BatRecPostTriggerTime"]  = root.find('BatRecPostTriggerTime').text        			
                                metadataFound = 1
                                
                        except:
                                metadataFound = 0
                                		

			if metadataFound == 0:
				dt = datetime.datetime.fromtimestamp(os.path.getmtime(wavFilePath))
				d["BatRecDate"] = dt.strftime("%Y%m%d%H%M%S")

			dictlist.append(d)
			
		return dictlist
	#-------------------------
	def getAllFilesByExtension(self, ThePath, AnExtension):
		return filter(os.path.isfile, glob.glob(ThePath + '/*' + AnExtension))
	#-------------------------
	def audioConvert(self, inputPath, outputPath):
		shutil.copy2(inputPath, outputPath)
	#-------------------------
	def cleanUp(self):
		pass
	#-------------------------
	def userMustEnterSpeed(self):
		return False
	#-------------------------
        
