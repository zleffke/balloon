#!/usr/bin/env python
import re

def Parse_APRS_NEW(data):
    time_str = data[63:69]
    lat_str = data[70:77]
    ns_hemi = data[77]
    lon_str = data[79:87]
    ew_hemi = data[87]
    bearing_str = data[89:92]
    speed_str = data[93:96]
    alt_str = data[127:133]

    time_str = time_str[0:2] + ":" + time_str[2:4] + ":" + time_str[4:6] + " UTC"
    lat_f = float(lat_str[0:2]) + float(lat_str[2:]) / 60.0
    if ns_hemi == "S":  lat_f = lat_f * -1
    lon_f = float(lon_str[0:3]) + float(lon_str[3:]) / 60.0
    if ew_hemi == "W":  lon_f = lon_f * -1
    bearing_f = float(bearing_str) # degrees
    speed_f_mph = float(speed_str)
    speed_f_ms  = speed_f_mph * 0.44704
    alt_f = float(alt_str) * 0.0003048 #km
    
    return time_str, lat_f, lon_f, alt_f, speed_f_ms, bearing_f

def Parse_APRS(word):
    #file = open('APRS_example.txt')
	#word = file.read()

	# Parsing algorithm	
    m = re.search('pid=F0\n(.+?)>', word)
    if m:
        mark = m.group(1)
    #a = re.search('A=(.+?)', mark)
    #if a:
    #    alt = a.group(1)
    time_str = word[63:69]
    lat_str = word[70:77]
    ns_hemi = word[77]
    lon_str = word[79:87]
    ew_hemi = word[87]
    bearing_str = word[89:92]
    speed_str = word[93:96]
    alt_str = word[127:133]
    print time_str, lat_str, ns_hemi, lon_str, ew_hemi, bearing_str, speed_str, alt_str
    alt = float(word[127:133]) * 0.0003048

    try:
        l = re.search('h(.+?)N', mark)
        nsSign = 0
    except:
        l = re.search('h(.+?)S', mark)
        nsSign = 1
    if l:
        lat = l.group(1)

    try:
        o = re.search('N/(.+?)W', mark)
        ewSign = 1
    except:
        o = re.search('N/(.+?)E', mark)
        ewSign = 0
    if o:
        lon = o.group(1)
	# End parsing algorithm

    lat_f = float(lat[0:2]) + float(lat[2:]) / 60.0
    if nsSign:
        lat_f = lat_f * (-1)
    lon_f = float(lon[0:3]) + float(lon[3:]) / 60.0
    if ewSign:
        lon_f = lon_f * (-1)
    #print lat, lon, alt, lon[0:2]

    list = [lat_f, lon_f, alt]
    return list


