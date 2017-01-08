# Bat project

Here you find some Python scripts and other resources that were created for bat surveys as part of a fauna, flora and habitat (FFH) monitoring project by an organisation in Germany: <a href="http://bi-wollenberg.org" target="_blank"> BI&nbsp;„Rettet&nbsp;den&nbsp;Wollenberg“&nbsp;e.V.</a><br>
<br>
Some scripts involve mass data handling of bat call recordings from the <a href="http://www.bat-pi.eu/EN/index-EN.html"  target="_blank">Bat-Pi&nbsp;1</a>, a great <a href="https://www.raspberrypi.org/" target=_blank>Raspberry Pi</a> based ultrasonic bat call recorder and the transfer of ultrasonic bat sounds to <a href="http://www.wsl.ch/dienstleistungen/produkte/software/batscope/index_EN" target="_blank">BatScope&nbsp;3</a>, a free bat call analysis and classification software.<br>
<br>
Other scripts will be made available soon and involve georeferencing and handling of sonogram screenshots from the <a href="http://www.mekv.de/bat3/index.htm" target="_blank">SSF&nbsp;BAT&nbsp;3</a> hand held bat detector.<br>
<br>
All code is provided in the hope that it is helpful to other bat friends and nature enthousiasts. We are open for questions or feedback. Please feel free to contact me through GitHub or drop a message in <a href=mailto:ffhmonitor@gmail.com>my mailbox</a>.<br>
<br>
FVG, January 2017
<hr>

## makeBatScopeXml.py
#### Georeferencing Bat-Pi recordings and prepare the transfer to bat call analyzer software
Script for the <a href="http://www.bat-pi.eu/EN/index-EN.html"  target="_blank">Bat-Pi&nbsp;1</a> (first edition). It georeferences all wav files and creates an XML meta data file for each recording, allowing them to be transferred to <a href="http://www.wsl.ch/dienstleistungen/produkte/software/batscope/index_EN" target="_blank">BatScope&nbsp;3</a>, a bat call analyser and classification software for MAc OS X. 

What this script does:
<ul><li>it reads current Bat Pi device settings from /out/bin/recordings.sh
<li>it reads GPS track points from /out/data/gps (gpx-file or an alternative 'fixed-geo.txt') and geo references all recordings
<li>it reads logged temperatures from a /out/ENVLOG.TXT file for each recording
<li>it writes an XML file for each wav recording with device settings, GPS data and temperatures into /out/data/batscope/ 
<li>it writes a session KML file with georeferenced recordings into /out/data/reports/pi-route.kml for use with GIS software
<li>it writes a session XML with archived device settings for the current session into /out/data/reports/pi-session.xml 
<li>it writes a session CSV with archived device settings for the current session into /out/data/reports/pi-session.csv
</ul>
Please note, that the Bat-Pi normally does not log temperatures. We built our own temperature datalogger and provide an environment log file accordingly. The data format is documented in the script.

Also note that a special ImporterModule for the BatScope software is needed in order to read the XML meta data files. (See the Bat-Pi v1 Importer below). 

## Bat-Pi v1 Importer (BatPi1ImporterModule.py)
#### Importer module for the transfer of Bat Pi recordings into a BatScope 3 database

In order to import the <a href="http://www.bat-pi.eu/EN/index-EN.html"  target="_blank">Bat-Pi&nbsp;1</a> wav files and their corresponding XML metadata, this script must reside on the BatScope Computer in the directory where BatScope's importer modules reside. This directory usually is:<br><code>/Library/Application Support/BatScope/ImporterModules</code>

In BatScope 3, the process is called 'SD card conversion'. The /out/data directory of the Bat-Pi has to be copied on to the BatScope computer and is seen by BatScope as an 'SD Card'. The sub directory <code>/out/data/batscope</code> should contain XML files with metadata for each recording. See the makeBatScopeXml.py script above for creating those XML meta data files.

As soon as the importer script is present on your BatScope computer, BatScope will offer a data converter called "Bat-Pi v1 Importer". For more information, please consult the BatScope manual on how to access the convert functionality. Look for a chapter called 'Converting and Importing Foreign Audio Data'. The manual can be found on the <a href="http://www.wsl.ch/dienstleistungen/produkte/software/batscope/index_EN" target="_blank">BatScope&nbsp;homepage</a>.


