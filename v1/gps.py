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

def utc_ts(self):
    return str(date.utcnow()) + " UTC | "

class gpgga_object(object):
    def __init__(self):
        self.latitude = 0.0		#degrees
        self.longitude = 0.0	#degrees
        self.altitude = 0.0		#meters
        self.utc_time = ''		#string
        self.fix_quality = 0	#0=invalid, 1=gps fix, 2 = dgps fix
        self.num_sats = 0		#number of locked satellites
        self.hdop = 0.0			#Horizontal Dilution of preceision, meters
        self.wgs84 = 0.0		#Height of Geoid above WGS84 Ellipsoid, meters

class gprmc_object(object):
    def __init__(self):
        self.utc_time = ''
        self.nav_warn = ''
        self.latitude = 0.0
        self.longitude = 0.0
        self.speed = 0.0
        self.track = 0.0
        self.utc_date = ''

class GPS_Thread(threading.Thread):
    def __init__ (self, port, baud, log_flag):
        threading.Thread.__init__(self)
        self._stop = threading.Event()
        self.gps_ser  = serial.Serial(port, baud)
        self.log_flag = log_flag
        self.gpgga    = gpgga_object()
        self.gprmc    = gprmc_object()

        self.raw_log = None
        self.csv_log = None

        if self.log_flag==1:
            self.raw_log = 'gps_raw.txt'
        elif self.log_flag==2:
            self.csv_log = 'gps_csv.txt'
        elif self.log_flag==3:
            self.raw_log = 'gps_raw.txt'
            self.csv_log = 'gps_csv.txt'

    def run(self):
        while (not self._stop.isSet()):
            data = self.gps_ser.readline()
            if self.raw_log != None:
                rl = open(self.raw_log,'a')
                rl.write(data)
                rl.close()
            line = ((data).strip()).split(',')
            #print line
            if   line[0] == '$GPGGA': self.GPGGA_Parse(line)
            elif line[0] == '$GPRMC': self.GPRMC_Parse(line)

            
        sys.exit()
	
    def get_lat_lon_alt(self):
        return self.gpgga.latitude, self.gpgga.longitude, self.gpgga.altitude

    def get_spd_cse(self):
        return self.gprmc.speed, self.gprmc.track
    
    def get_date_time(self):
        return self.gprmc.utc_date, self.gpgga.utc_time

    def GPGGA_Parse(self, line):
        self.gpgga.utc_time = line[1]
        lat_str = line[2]
        self.gpgga.latitude = float(line[2][:2]) + float(line[2][2:]) / 60
        if line[3] == 'S':
            self.gpgga.latitude = -1 * self.gpgga.latitude
        self.gpgga.longitude = float(line[4][:3]) + float(line[4][3:]) / 60		
        if line[5] == 'W':
            self.gpgga.longitude = -1 * self.gpgga.longitude
        self.gpgga.fix_quality = int(line[6])
        self.gpgga.num_sats = int(line[7])
        self.gpgga.hdop = float(line[8])
        self.gpgga.altitude = float(line[9])*3.28084
        self.gpgga.wgs84 = float(line[11])		#Height of geoid above WGS84 ellipsoid
        #print self.gpgga.utc_time, self.gpgga.latitude, self.gpgga.longitude
	
    def GPRMC_Parse(self, line):
        self.gprmc.utc_time = line[1]
        self.gprmc.nav_warn = line[2]
        self.gprmc.latitude = float(line[3][:2]) + float(line[3][2:]) / 60
        if line[4] == 'S':
            self.gprmc.latitude = -1 * self.gprmc.latitude
        self.gprmc.longitude = float(line[5][:3]) + float(line[5][3:]) / 60		
        if line[6] == 'W':
            self.gprmc.longitude = -1 * self.gprmc.longitude

        #speed in knots, need to convert to m/s or mph
        #1 knot = 1.15078 mph
        #1 knot = 0.514444 meters/second
        if line[7] != '': self.gprmc.speed = float(line[7])*1.15078
        else:  self.gprmc.speed = 0.0

        if line[8] != '': self.gprmc.track = float(line[8])
        else:  self.gprmc.track = 0.0
        
        self.gprmc.utc_date = float(line[9])

    def stop(self):
        self.gps_ser.close()
        self._stop.set()
        sys.quit()

    def stopped(self):
        return self._stop.isSet()

if __name__ == '__main__':
	#--------START Command Line option parser------------------------------------------------------
    usage = "usage: %prog "
    parser = OptionParser(usage = usage)
    p_help = "GPS Serial Port, default = /dev/ttyACM0"
    b_help = "GPS Serial Port Baud, default = 4800"
    f_help = "GPS logfile, 0-none, 1-nmea only, 2-parsed, 3-parsed+nmea, default = none"
    parser.add_option("-p", dest = "port"    , action = "store", type = "string", default="/dev/ttyACM0", help = p_help)
    parser.add_option("-b", dest = "baud"    , action = "store", type = "int"   , default="4800"        , help = b_help)
    parser.add_option("-f", dest = "log_file", action = "store", type = "string", default=None          , help = f_help)
    (options, args) = parser.parse_args()
    #--------END Command Line option parser------------------------------------------------------
    
    gps_serial = GPS_Thread(options.port, options.baud, options.log_file)
    
    try:
        gps_serial.start()
        while 1:
            x = 1
            lat, lon, alt = gps_serial.get_lat_lon_alt()
            spd, cse = gps_serial.get_spd_cse()
            print lat, lon, alt, spd, cse
            time.sleep(0.250)
        sys.exit()
    except Exception as e:
        gps_serial.stop()
        print "Exception Thrown, Terminating..."
        print e
        sys.exit()
