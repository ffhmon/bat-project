# Bat project

Here you find some Python scripts and other resources that were created for bat surveys as part of a flora, fauna and habitat (FFH) monitoring project in Germany.<br>
<br>
Some scripts involve mass data handling of bat call recordings from the Bat-Pi, a Raspberry Pi based ultrasonic bat call recorder. For more information on the Bat-Pi device, please see http://www.bat-pi.eu/EN/index-EN.html<br>
<br>
Other scripts involve georeferencing and handling of sonogram screenshots from the SSF BAT 3 hand held bat detector.<br>
Pease see http://www.mekv.de/bat3/index.htm for more information on that device. (German website)<br>
<br>
The code is provided in the hope that it is helpful to other bat friends and nature enthousiasts.

## makeBatScopeXml.py
#### Georeferencing Bat-Pi recordings and prepare the transfer to bat call analyzer software
Script for the Bat Pi v1 (first edition). It georeferences all wav files and creates an XML meta data file for each recording, allowing them to be transferred to BatScope 3, a bat call analyser and classification software. See http://www.batscope.ch/ for more information.

<ul>What this script does:
<li>it reads current Bat Pi device settings from /out/bin/recordings.sh
<li>it reads GPS track points from /out/data/gps (gpx-file or an alternative 'fixed-geo.txt') and geo references all recordings
<li>it reads logged temperatures from a /out/ENVLOG.TXT file for each recording
<li>it writes an XML file for each wav recording with device settings, GPS data and temperatures into /out/data/batscope/ 
<li>it writes a session KML file with georeferenced recordings into /out/data/reports/pi-route.kml for use with GIS software
<li>it writes a session XML with archived device settings for the current session into /out/data/reports/pi-session.xml 
<li>it writes a session CSV with archived device settings for the current session into /out/data/reports/pi-session.csv
</ul>
Please note, that the Bat-Pi normally does not log temperatures. We built our own temperature datalogger and provide an environment log file accordingly. The data format is documented in the script.

Also note that a special ImporterModule for the BatScope software is needed in order to read the XML meta data files. (See the Bat-Pi v1 Importer below). 
