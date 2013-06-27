#!/usr/bin/python

####################################################################################################
# Python Script - Calculates Distance, RSSI and checks coverage maps for a single point
#
# STEP:
#	Input: lat-lon (decimal values)	, sectors, txPower(dBm), txTain, rxGain
#	Output: rssi,distance, sector found
#
# OPTIONS:
#	
#
#	info: david.andreatta@brennercom.it
#####################################################################################################

#IMPORT SECTION

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
import re
import getopt
import shutil
import glob
from functions import dBLoss
from functions import distMap
from pygeocoder import Geocoder
from urllib import urlopen
from xml.etree import ElementTree
import keytree
from shapely.geometry import Point, shape


#####################################################################################################
# Help Menu
#####################################################################################################

print '***************************\nWIMAX CHECK COVERAGE:\nINPUT: address or LatLon point\nOUTPUT:rssi,distance,wimax sectors\n***************************'
print 'PARAMETERS:\nPMP320AP\ntxPower: 25.0 dBm\nAntenna Gain: 17 dBi\nPMP320SM\nAntenna Gain: 14.5 dBi'
print '***************************'

#####################################################################################################
# Script
#####################################################################################################

#KML directory
kmlDir = '%s/kml' % os.getcwd()
# Wimax Sectors - NAME,LAT,LON

sitesName = ['RENON0_C320E01','BZNPO0_C320S01','BZOBS0_C320N01','BZBIC0_C320N01','BZBIC0_C320S02','BZFAE0_C320E01','BZFAE0_C320S02','NATUR0_C320O01','TRENS0_C320N01','TRENS0_C320E02','MEMUT0_C320O01','RVLEN0_C320N01','RVLEN0_C320S02','BRION0_C320S01','TNCAL0_C320O01','TNPER0_C320O01','TNALA0_C320O01','TNALA0_C320N02','CLBEV0_C320SE01','CLBEV0_C320S02']
sitesLat = [46.61478,46.419566,46.372265,46.482070,46.482070,46.478638,46.478638,46.628222,46.875396,46.875396,46.699782,45.874752,45.874752,45.884588,46.086633,46.065460,45.764032,45.764032,46.404437,46.404437]
sitesLon = [11.46094,11.427172,11.541982,11.330376,11.330376,11.228185,11.228185,11.020322,11.427326,11.427326,11.132244,10.995029,10.995029,10.874190,11.150569,11.269177,11.017502,11.017502,11.052219,11.052219]
sitesFreq = [3453,3553,3542,3542,3442,3453,3553,3442,3542,3453,3542,3453,3553,3553,3442,3442,3442,3542,3553,3442]
sitesPower = [22.0,19.0,22.0,19.0,22.0,22.0,19.0,19.0,19.0,19.0,22.0,22.0,19.0,19.0,22.0,22.0,19.0,22.0,19.0,22.0]

# Static Parameters (PMP320APSM AntennaGain,  )
#txPower = float(raw_input("Enter txPower (dBm):"))
#For PMP320AP default = 17
#txGain = float(raw_input("Enter TX Antenna Gain (dBi):"))
txGain = 17.0
#For PMP320SM default = 14.5
#rxGain = float(raw_input("Enter RX Antenna Gain (dBi):"))
rxGain = 14.5

sel = raw_input("\n1-SECTOR SELECTION AND COVERAGE CHECK\n2-MANUAL SECTOR SELECTION\n\nSELECT:") 

if sel == '2':
	i = 0
	for i in range(0,len(sitesName)):
		print i, '-',sitesName[i],'-',sitesFreq[i],'MHz'
		i=i+1
	try:
		sector = int(raw_input("SECTOR SELECTION:"))
		if sector not in range(0,len(sitesName)):
			print 'PLEASE SELECT A VALID OPTION!'
			quit()
	except:
		print 'PLEASE SELECT A VALID OPTION!'
		quit()
	lat1 = float(raw_input("INSERT LATITUDE (decimal degrees):"))
	lon1 = float(raw_input("INSERT LONGITUDE (decimal degrees):"))
	txFreq = sitesFreq[sector]
	txPower = sitesPower[sector]
	lat2 = sitesLat[sector]
	lon2 = sitesLon[sector]
	 
	distKM = distMap(lat1,lon1,lat2,lon2)
	rssi = dBLoss(distKM,txFreq,txPower,txGain,rxGain)

	if distKM > 11.0 and distKM < 40.0:
		print 'EXTENDED RANGE NEEDED\nDISTANCE FROM SECTOR ', sitesName[sector],'[',txFreq,'MHz]:', distKM ,'Km'
		print 'RSSI: ', int(rssi)
	elif distKM > 40.0:
		print 'Warning: SITE OUT OF RANGE!\nDistanza Punto dal Settore ', sitesName[sector],'[',txFreq,'MHz]:', distKM ,'Km'
	else:
		print 'DISTANCE FROM SECTOR ', sitesName[sector] ,'[',txFreq,'MHz]:', distKM ,'Km'
		print 'RSSI: ', int(rssi), 'dBm'
	quit()

if sel == '1':
	visSite = []
	dists = []
	rssiArray = []
	sel2 = raw_input("1: INSERT ADDRESS (GMaps FORMAT)\n2: INSERT LAT-LON\nSELECT:")
	if sel2 == '':
		print 'PLEASE SELECT A VALID OPTION'
		quit()
	if sel2 == '1':
		address = raw_input("INSERT ADDRESS:")
		if address == "":
			print 'INSERT ADDRESS.'
			quit()
		try:
			result = Geocoder.geocode(address)
			lat1 = result.latitude
			lon1 = result.longitude
		except: 
			print 'WARNING NO ADDRESS FOUND OR INTERNET CONNECTION IS NOT WORKING'
			quit()
	if sel2 == '2':
		lat1 = float(raw_input("INSERT LATITUDE (decimal degrees):"))
		lon1 = float(raw_input("INSERT LONGITUDE (decimal degrees):"))
	if sel2 != '1' and sel2 != '2':
		print 'PLEASE SELECT A VALID OPTION'
		quit()
	for files in os.listdir(kmlDir):
		doc = urlopen("%s" % os.path.join(kmlDir,files)).read()
		tree = ElementTree.fromstring(doc)
		kmlns = tree.tag.split('}')[0][1:]
		elems = tree.findall(".//{%s}Polygon" % kmlns)
		p = Point(lon1,lat1)
		inPol = filter(lambda e: shape(keytree.geometry(e)).contains(p), elems)
		if len(inPol) == 1:
			visSite.append(os.path.splitext(files)[0])
	#Nessun Settore Trovato
	if len(visSite) == 0:
		print 'LATITUDE: ', lat1
		print 'LONGITUDE: ', lon1
		print 'NO WIMAX COVERAGE FOUND!'
		quit()
	#Calculate RSSI for each visSite
	for k in range(0,len(visSite)):
		idx = sitesName.index("%s" % visSite[k])
		lat2 = sitesLat[idx]
		lon2 = sitesLon[idx]
		txPower = sitesPower[idx]
		txFreq = sitesFreq[idx]
		distKM = distMap(lat1,lon1,lat2,lon2)
		rssi = dBLoss(distKM,txFreq,txPower,txGain,rxGain)
		dists.append(distKM)
		rssiArray.append(rssi)
	print '----------------------------------'
	print 'COORDINATES:'
	print '----------------------------------'
	print 'LATITUDE: ', lat1
	print 'LONGITUDE: ', lon1 
	print '----------------------------------'
	print 'FOUND %i SECTOR(S)' % len(visSite)
	print '----------------------------------'
	for k in range(0,len(visSite)):
		if dists[k] > 11.0 and dists[k] < 40.0:
			print '----------------------------------'
			print 'EXTENDED RANGE NEEDED\nDISTANCE FROM SECTOR ', visSite[k],'\n[Radio txPower:', sitesPower[sitesName.index("%s" % visSite[k])], ' dBm,', sitesFreq[sitesName.index("%s" % visSite[k])],'MHz]:', dists[k] ,'Km'
			print 'RSSI: ', int(rssiArray[k])
			print '----------------------------------'
		elif dists[k] > 40.0:
			print '----------------------------------'
			print 'Warning: SITE OUT OF RANGE!\nDISTANCE FROM SECTOR', visSite[k],':', dists[k],'Km\n[',sitesFreq[sitesName.index("%s" % visSite[k])],'MHz]'
			print '----------------------------------'
		else:
			print 'DISTANCE FROM SECTOR', visSite[k] ,':', dists[k] ,'Km\n[Radio txpower:', sitesPower[sitesName.index("%s" % visSite[k])], ' dBm,', sitesFreq[sitesName.index("%s" % visSite[k])],'MHz]'
			print 'RSSI: ', int(rssiArray[k]), 'dBm'
			print '----------------------------------'

quit()
