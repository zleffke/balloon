#!/usr/bin/env python
import socket
import os
import string
import sys
import time
from optparse import OptionParser
from binascii import *
from gps import *
from tnc import *
from astro_func import *

def Print_Data(time_data, loc_state, tar_state, pointing):
    #time_data = [comp_time, loc_time, tar_time]
    #loc_state = [loc_lat, loc_lon, loc_alt, loc_spd, loc_brng]
    #tar_state = [tar_lat, tar_lon, tar_alt, tar_spd, tar_brng]
    #pointing = [rho_mag, az, el]
    os.system('clear')
    #Time Information
    print 'Time Information:'
    print '        Computer Time: %s' % time_data[0]
    print '       Local GPS Time: %s' % time_data[1]
    print '      Target GPS Time: %s' % time_data[2]
    print ' Last Position Report: %s' % time_data[3] 
    print '      Time Since Last: \n'
    
    print 'Local Position:'
    print '         Lat, Lon, Alt: %3.6f [deg], %3.6f [deg], %3.6f [ft] '   % (loc_state[0], loc_state[1], loc_state[2])
    print '        Speed, Bearing: %3.6f [mph], %3.6f [deg] \n'             % (loc_state[3], loc_state[4])

    print 'Target Position:'
    print '         Lat, Lon, Alt: %3.6f [deg], %3.6f [deg], %3.6f [ft] \n' % (tar_state[0], tar_state[1], tar_state[2])
    print '        Speed, Bearing: %3.6f [mph], %3.6f [deg] \n'             % (tar_state[3], tar_state[4])

    print 'Pointing:'
    print '       Range to Target: %3.6f [km]' % (pointing[0]) 
    print '     Azimuth to Target: %3.2f [deg]' % (pointing[1])
    print '   Elevation to Target: %3.2f [deg] \n' % (pointing[2]) 


if __name__ == '__main__':
	
    #--------START Command Line option parser------------------------------------------------
    usage = "usage: %prog -a <Server Address> -p <Server Port> "
    parser = OptionParser(usage = usage)
    gp_help = "GPS Serial Port, default = /dev/ttyACM0"
    gb_help = "GPS Serial Port Baud, default = 4800"
    gf_help = "GPS logfile, 0-none, 1-nmea only, 2-csv, 3-csv+nmea, default = none"
    tp_help = "TNC Serial Port, default = /dev/ttyUSB0"
    tb_help = "TNC Serial Port Baud, default = 4800"
    tf_help = "TNC logfile, 0-none, 1-nmea only, 2-parsed, 3-parsed+nmea, default = none"
    cs_help = "Callsign Filter, Default = KJ4QLP"
    parser.add_option("--gp", dest = "gps_port" , action = "store", type = "string", default="/dev/ttyACM0", help = gp_help)
    parser.add_option("--gb", dest = "gps_baud" , action = "store", type = "int"   , default="4800"        , help = gb_help)
    parser.add_option("--gf", dest = "gps_log"  , action = "store", type = "int"   , default=None          , help = gf_help)
    parser.add_option("--tp", dest = "tnc_port" , action = "store", type = "string", default="/dev/ttyUSB0", help = tp_help)
    parser.add_option("--tb", dest = "tnc_baud" , action = "store", type = "int"   , default="4800"        , help = tb_help)
    parser.add_option("--tf", dest = "tnc_log"  , action = "store", type = "string", default=None          , help = tf_help)
    parser.add_option("--cs", dest = "callsign" , action = "store", type = "string", default="KK4BSM-11"   , help = cs_help)
    (options, args) = parser.parse_args()
    (options, args) = parser.parse_args()
    #--------END Command Line option parser-------------------------------------------------
    
    #--Initialize Variables------------
    time_stamp = 0.0
    loc_lat = 0.0
    loc_lon = 0.0
    loc_alt = 0.0
    loc_spd = 0.0
    loc_cse = 0.0
    loc_date = None
    loc_time = None

    tar_lat = 0.0
    tar_lon = 0.0
    tar_alt = 0.0
    tar_spd = 0.0
    tar_brng = 0.0
    tar_time = None

    comp_time = None
    comp_date = time.strftime("%H:%M:%S UTC", time.gmtime())

    rho_mag = 0.0
    az = 0.0
    el = 0.0
    
    deg2rad = pi / 180
    rad2deg = 180 / pi
    #--End Initialize Variables------------
    
    #--Create GPS thread---
    #gps_thread = GPS_Thread(options.gps_port, options.gps_baud, options.gps_log)
    #gps_thread.daemon = 'True'
    
    #--Create TNC Thread---
    tnc_thread = TNC_Thread(options.tnc_port, options.tnc_baud, options.tnc_log, options.callsign)
    tnc_thread.daemon = 'True'
    
    #--Main Loop----
    try:
        #--Start GPS thread---
        #gps_thread.start()
        print "GPS Thread Launched Successfully"
        #--Start TNC Thread---
        tnc_thread.start()
        print "TNC Thread Launched Successfully"
        while 1:
            #Get Local lat/lon/alt/spd/brng
            #loc_lat, loc_lon, loc_alt   = gps_thread.get_lat_lon_alt()
            #loc_spd, loc_cse            = gps_thread.get_spd_cse()
            #loc_date, loc_time          = gps_thread.get_date_time()
            loc_state = [loc_lat, loc_lon, loc_alt, loc_spd, loc_cse]

            #Get target lat/lon/alt/spd/brng
            tar_lat, tar_lon, tar_alt   = tnc_thread.get_lat_lon_alt()
            tar_spd, tar_cse            = tnc_thread.get_spd_cse()
            tar_time                    = tnc_thread.get_time()
            tar_state = [tar_lat, tar_lon, tar_alt, tar_spd, tar_cse]

            comp_time = time.strftime("%H:%M:%S UTC", time.gmtime())
            time_data = [comp_time, loc_time, tar_time, comp_date, loc_date]

            #Calculate Pointing angles
            pointing = RAZEL(loc_lat,loc_lon,loc_alt*0.0003048,tar_lat, tar_lon, tar_alt*0.0003048)

            

            

            #Update Display
            Print_Data(time_data, loc_state, tar_state, pointing)

            
            print tnc_thread.line
            time.sleep(1)
    
    
    except Exception as e:
        print "Exception Thrown in main, Terminating..."
        print e
        tnc_thread._stop()
        quit()
    sys.exit()

