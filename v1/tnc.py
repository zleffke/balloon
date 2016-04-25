#!/usr/bin/env python
##################################################
# GPS Interface
# Author: Zach Leffke
# Description: Initial GPS testing
##################################################

from optparse import OptionParser
import threading
from datetime import datetime as date
import os
import serial
import math
import sys
import string
import time

def utc_ts():
    return str(date.utcnow()) + " UTC | "

class TNC_Thread(threading.Thread):
    def __init__ (self, port, baud, log_flag, call_filt):
        threading.Thread.__init__(self)
        self._stop      = threading.Event()
        self.tnc_ser    = serial.Serial(port, baud)
        self.log_flag   = log_flag
        self.line       = ""
        self.call_filt  = call_filt
        self.callsign = ""
        self.path = []
        
        self.raw_log = None
        self.csv_log = None

        self.lat    = 0.0
        self.lon    = 0.0
        self.alt    = 0.0

        self.spd      = 0.0
        self.cse      = 0.0
        self.time_utc = 0.0

        self.log_file=None

        #if self.log_flag!=None:
        #    self.log_file = open(self.log_flag,'a')

    def run(self):
        while (not self._stop.isSet()):
            data = self.tnc_ser.readline()
            #data = "KK4BSM-11>APT314,WIDE1-1,WIDE2-1:/205107h3713.89N/08025.49WO000/000/A=002125/Virginia Tech Project Ellie, Go Hokies!\n"
            #data = "KC8SIR-1>APBL10,WIDE3-1,WIDE4-1:!3733.20N/08106.48WO183/036/A=018991V300"            
            if self.log_flag != None:  
                self.log_file = open(self.log_flag,'a')
                self.log_file.write(utc_ts() + data)
                self.log_file.close()
            self.line = data.strip('\n')
            self.Parse_TNC()
            #print self.line
            time.sleep(1)
            
        sys.exit()

    def Parse_TNC(self):
        #----------Extract Callsign----------
        #--Locate first '>', take characters from beginning, limit search to first ten characters
        idx1 = self.line.find('>', 0, 10)
        self.callsign = self.line[:idx1]
        #print len(self.callsign), self.callsign
        
        #--Verify Callsign matches callsign filter
        idx2 = self.callsign.find(self.call_filt)
        #print idx2
        if (idx2 != -1): #Callsign Match
            #----------extract path----------
            #locate first '>', locate ':', take characters in between
            a = self.line.find(':')
            path_str = self.line[idx1+1:a]
            self.path = path_str.split(',')
            #----------extract time----------
            #locate ':', take next 7 characters
            #hhmmsst, hh - hours, mm - minutes, ss - seconds, t - timezone
            time_str = self.line[a+2:a+2+7]
            if ((time_str[6] == 'h')or(time_str[6] == 'z')): #Zulu Time
                self.time_utc = time_str[0:2] + ":" + time_str[2:4] + ":" + time_str[4:6] + " UTC"
            #----------extract lat----------
            #locate ':', skip 7 char, take next 8 char
            lat_str  = self.line[a+9:a+9+7]
            lat_hemi = self.line[a+9+7:a+9+8]
            lat_f = float(lat_str[0:2]) + float(lat_str[2:]) / 60.0
            if (lat_hemi == 'S'):  lat_f = lat_f * -1
            self.lat = lat_f #decimal degrees
            #----------extract lon----------
            #locate ':', skip 16, take next 9 char
            lon_str  = self.line[a+18:a+18+8]
            lon_hemi = self.line[a+18+8: a+18+9]
            lon_f = float(lon_str[0:3]) + float(lon_str[3:]) / 60.0
            if lon_hemi == "W":  lon_f = lon_f * -1
            self.lon = lon_f # decimal degrees
            #----------extract spd----------
            #locate ':', skip 27, take next 3 char
            spd_str = self.line[a+28:a+28+3]
            self.spd = float(spd_str)*1.15078 #convert from knots to mph
            #----------extract course----------
            #locate ':/', skip 30, take next 3 char
            cse_str = self.line[a+32:a+32+3]
            self.cse = float(cse_str) #in degrees
            #----------extract altitude----------
            #locate 'A=', take next 6
            a = self.line.find('A=')
            alt_str = self.line[a+2:a+2+6]
            self.alt = float(alt_str) #in feet

    def get_last_callsign(self):
        return self.callsign

    def get_lat_lon_alt(self):
        return self.lat, self.lon, self.alt

    def get_spd_cse(self):
        return self.spd, self.cse

    def get_time(self):
        return self.time_utc

    def stop(self):
        #self.tnc_ser.close()
        self._stop.set()
        sys.exit()

    def stopped(self):
        return self._stop.isSet()

