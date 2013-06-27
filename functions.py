#!/usr/bin/python

####################################################################################################
# Function file of pathloss.py
#	
#	dBLoss: calculates RSSI theoretical value
#	distMap: calculates distance in KM between two coordinates
# 
#	info: david.andreatta@brennercom.it
#####################################################################################################

import os
import subprocess
import commands
import sys
import socket
import tarfile
import zipfile
import datetime
import time
import email
import logging
import subprocess
import math



def dBLoss(dist,txFreq,txPower,txGain,rxGain):
	txPowerW = 10**(txPower/10)/1000
	txPowerdBW = 10*math.log10(txPowerW)
	eirpdBW = txGain + txPowerdBW
	rxPowerdBW = eirpdBW + rxGain - 32.4 - 20*math.log10(dist) - 20*math.log10(txFreq)
	rxRSSI = rxPowerdBW + 30.0
	return rxRSSI


def distMap(lat1,lon1,lat2,lon2):

	degrees_to_radians=math.pi/180.0
	# phi = 90 - latitude
	phi1 = (90.0 - lat1)*degrees_to_radians
	phi2 = (90.0 - lat2)*degrees_to_radians
	# theta = longitude
	theta1 = lon1*degrees_to_radians
	theta2 = lon2*degrees_to_radians

    # Compute spherical distance from spherical coordinates.    
    # For two locations in spherical coordinates 
    # (1, theta, phi) and (1, theta, phi)
    # cosine( arc length ) = 
    #    sin phi sin phi' cos(theta-theta') + cos phi cos phi'
    # distance = rho * arc length
    
	cos = (math.sin(phi1)*math.sin(phi2)*math.cos(theta1 - theta2) + 
           math.cos(phi1)*math.cos(phi2))
	arc = math.acos( cos )

    # Remember to multiply arc by the radius of the earth 
    # in your favorite set of units to get length.
	distKm = arc*6373
	return distKm

