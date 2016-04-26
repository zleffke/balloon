High Altitude Balloon Tracking Software

Design Goals:
1.  Serial port connection to Terminal Node Controller for APRS ASCII messages
2.  Serial port connection with local GPS for chaser position.
3.  Callsign filtering for target.
4.  Computation of look angles and range from chaser to balloon.
        -Azimuth:  relative to true north
        -Elevation:  relative to local horizon
        -Range:  Slant Range, AKA Line of Sight Distance
        -Bearing:  Angle relative to the direction of travel of the chaser.
5.  Computation of Ascent/Descent Rate.
6.  Computation of time since last packet heard from target.
7.  Logging of raw and filtered TNC messages with time stamps.
8.  Logging of raw and formatted local GPS messages.

Longer Term Goals:
1.  pyQT implementation.  Look angles, plotting, etc.
2.  Serial connection to CAT port of FT-857D for S-meter logging during Packet Bursts.
3.  prediction of look angles between updates based off last packet heard (pos, track, speed).
4.  Serial/Network output for gimbal pointing.


