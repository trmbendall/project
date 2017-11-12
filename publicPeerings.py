#!/usr/bin/python

""" publicPeerings.py: A Python script to return information on Public Peerings """

__author__      = "Tristan Bendall/tristan@bendall.eu"
__version__     = "v1.3"

# Import various libraries
import json
import os
import requests
import sys

from collections import Counter
from math import *
from os.path import expanduser
from tabulate import tabulate
from time import *

# Set strings to output to UTF-8
# Fixes issues with printing tables to file
reload(sys)
sys.setdefaultencoding('utf-8')


# Function for interactive splash page
def startPage():

	table = []

	
	defDict = {

		1:returnPublicPeers,
		2:execSum,

	}

	# Options to run from Menu
	options = [
		
		"Return Public Peers",
		"Return Executive Summary",
		"Quit"
	]	

	table.append(["Option","Description"])

	# Allow options to start from 1, not 0
	for i in options:

		table.append([(options.index(i)+1),i])
	
	# Prints Menu of options
	print "\n\n"
	print tabulate([["Menu"]],tablefmt="grid")
	print tabulate(table,headers="firstrow",tablefmt="grid",numalign="left") 
	
	# Keeps user at Menu
	while True:

		keyInput = ""
	
		try:	
	
			keyInput = int(raw_input("Option: "))

		except ValueError as e:

			print tabulate([["Please enter a number"]],tablefmt="grid")

			continue
		
		# Validates user's choice
		if (int(keyInput)) in range(len(options)+1):

			if int(keyInput) == len(options):

				exitChoice = "N"

				while exitChoice not in ["N","n"] or exitChoice not in ["Y","y"]:

					exitChoice =  raw_input("Are you sure? [y/n]")

	                               	if exitChoice in ["Y","y"]:
		                
				               print tabulate([["Exiting..."]],tablefmt="grid")

                	                       sleep(2)

                        	               sys.exit()

					elif exitChoice in ["N","n"]:

						break
				print "\n\n"
				print tabulate([["Menu"]],tablefmt="grid")
				print tabulate(table,headers="firstrow",tablefmt="grid",numalign="left")							
				continue


			print tabulate([["You chose '{0}' ".format(options[int(keyInput-1)])]])

			print "Loading..."
		
			# Runs function directly from dict
			defDict[int(keyInput)]()
			
			print "\n\n"
			print tabulate([["Menu"]],tablefmt="grid")
			print tabulate(table,headers="firstrow",tablefmt="grid",numalign="left")
	
		else:

			print  tabulate([["Please pick an option"]],tablefmt="grid")

# Function to connect to PeeringDB and returns the specified Organisation's information
def apiConnect():

	asn = '46489'
	pid = '1956'

	baseurl = "http://peeringdb.com/"

	netUrl = "{0}/api/net/{1}".format(baseurl,str(pid))

	result = requests.get(netUrl)

	jResult = result.json()['data'][0]['netixlan_set']

	return jResult

# Function to print out data to file
def filePrintMode(data):

	# Reads in which function called filePrintMode function
	printType = data[1]

	#printChoice = raw_input("Press "'P'" to print to file, else <CR> to return to menu... ")

	# Keeps user at Print prompt
	while True:

		printChoice = raw_input("Press "'P'" to print to file, else <CR> to return to menu... ")
	
		if printChoice in ["P","p"]:
	
			printLoc = raw_input("Please enter file destination; default is home dir... ")

			# Checks if <CR> was pressed
			if not len(printLoc) > 0:

				printPath = "{0}/{1}.txt".format(expanduser("~"),printType)

				with open(printPath, "w") as f:

					f.write(data[0])

					if os.path.exists(printPath):

						print "\n"
				
						print "**** File created successfully ****"
						
						break
					
					else:
					
						print "WARNING: File not created"
						
						continue

						
			# Validates user-input Path
			elif not os.path.exists(os.path.abspath("{0}/{1}.txt".format(printLoc,printType))):
			
				print "WARNING: Directory not found"
				
			else:
			
				printPath = os.path.abspath("{0}/{1}.txt".format(printLoc,printType))
	
				if os.path.isdir(printLoc):

					try:

						with open(printPath,"w") as f:

							f.write(data[0])

							if os.path.exists(printPath):

								print "\n"
				                
								print "**** File created successfully ****"

								break

					except Exception as e:

						print e 

						break
				
		elif not len(printChoice) > 0:

			break

# Function to return all public peering grouped by IX name
def returnPublicPeers(*args,**kwargs):

	jResult = apiConnect()

	table = []

	unique = []
	
	rowEntry = []

	cells = []

	newDict = {}
	
	for i in jResult:

		if i['ix_id'] in unique:
			
			table.append([i['name'],i['ipaddr4']])
			
		else:
			
        
			unique.append([i['ix_id']]) 
        
			table.append([i['name'],i['ipaddr4']])
	
	outTable = tabulate(table,tablefmt="html")
	
	if 'web' not in kwargs:	

 			outTable = [tabulate(table,tablefmt="grid"),"PublicPeers"]
				
			print outTable[0]
	
			# Calls print function to preset option to print to file
			filePrintMode(outTable)

	return outTable

# Function to return total public peerings
def totalPeerings():

	jResult = apiConnect()

	totPeerings = len(jResult)

	return totPeerings

# Function to return total unique public peering points	
def uniqueOrgPeering():

	jResult = apiConnect()

	unique = []

	uniPeerings = {}

	[unique.append([i['name']]) for j in jResult for i in jResult if [i['name']] not in unique]

	uniPeerings['numUnique'] = len(unique)

	d = Counter()
	
	# Adds each "speed" per unique peering point
	for i in jResult:

		d[i['name']] += i['speed']	

	# This is the Counter of speed per name
	uniPeerings['speedUnique'] = dict(d)
	
	# Adds up all speeds (for a later function)
 	uniPeerings['totSpeedUnique'] = sum((dict(d)).values())

	return uniPeerings

# Function to return total Organisation Speed 	
def totalOrgSpeed():

	jResult = apiConnect()

	count = 0

	totSpeed = 0

	totalFig = {}

	totalFig['result'] = jResult

	for i in jResult:

		totSpeed += i['speed']

	totalFig['sum'] = totSpeed

	totalFig['len'] = len(jResult)

	totalFig['gig'] = int(totalFig['sum']) / 1000

	return totalFig

# Function to calculate standard deviation of public peering points' capacities	
def stdDevSpeed():
	
	avgStdDev = {}

	# Gets the unique peering points from earlier function
	valDict = uniqueOrgPeering()

	# Calculates Average Mean unique peering capacity
	mean = (valDict['totSpeedUnique'] / int(valDict['numUnique']))	
	
	# Gives the mean average in Gbps (peeringDB API returns in Mbps)
	avgStdDev['meanGig'] = mean / 1000

	speedDict = valDict['speedUnique']

	# Gives squared values of unique speed minus the average mean speed
	speedDictSq = {key:(((int(value) - int(mean))**2)) for key,value in speedDict.items()} 

	# Gives standard deviation value
	stdDevVal = sqrt((sum(speedDictSq.values()) / len(speedDictSq)))

	# Gives the amount of standard deviations for each unique peering pont
	stdDevUnOrg =  {key:(abs((value - mean))/stdDevVal) for key,value in speedDict.items()}

	# Gives the average amount of standard deviations a given unique peering point is, to two decimal places
	avgStdDev['deviation'] = round(float((sum(stdDevUnOrg.values()) / len(stdDevUnOrg))),2)

	# Gives the mode average of unique peering points
	avgStdDev['mode'] = ((Counter(speedDict.values()).most_common(1))[0][0] / 1000)

	return avgStdDev

# Function to construct out Executive summary
def execSum(*args,**kwargs):

	stdDevSpeedIn = stdDevSpeed()

	outTable =	tabulate(

				[
		
				["Executive Summary"],
				[tabulate([["Total Public Peering Points"],[totalPeerings()]],tablefmt="html",headers="firstrow",stralign="left",numalign="left")],
				[tabulate([["\r\n"]])],
				[tabulate([["Unique Peering Points"],[uniqueOrgPeering()['numUnique']]],tablefmt="html",headers="firstrow",stralign="left",numalign="left")],
				[tabulate([["Total Public Peering Capacity"],["{:,} Gbps Public Peering Capacity".format(int(totalOrgSpeed()['gig']))]],tablefmt="html",headers="firstrow",stralign="left",numalign="left")],
				[tabulate([["Mean Average # of Standard Deviations of Unique Peering Point Capacity"],["{0}".format(stdDevSpeedIn['deviation'] ) ]],headers="firstrow",tablefmt="html",stralign="left",numalign="left")],
				[tabulate([["Standard Deviation of Unique Public Peering Capacity"],["{:,}G".format(int(round(stdDevSpeedIn['meanGig'],2)))]],tablefmt="html",headers="firstrow",stralign="left",numalign="left")],
				[tabulate([["Mode Average Unique Peering Point Capacity"],["{0}G".format(stdDevSpeedIn['mode'])]],tablefmt="html",headers="firstrow",stralign="left",numalign="left")]			
	
				],headers="firstrow",tablefmt="html",stralign="left")
				
				

        if 'web' not in kwargs:

			outTable = [tabulate(

                                [

                                        ["Executive Summary"],
                                        [tabulate([["Total Public Peering Points"],[totalPeerings()]],tablefmt="grid",headers="firstrow")],
                                        [tabulate([["Unique Peering Points"],[uniqueOrgPeering()['numUnique']]],tablefmt="grid",headers="firstrow")],
                                        [tabulate([["Total Public Peering Capacity"],["{:,} Gbps Public Peering Capacity".format(int(totalOrgSpeed()['gig']))]],tablefmt="grid",headers="firstrow")],
                                        [tabulate([["Mean Average # of Standard Deviations of Unique Peering Point Capacity"],["{0}".format(stdDevSpeedIn['deviation'] ) ]],tablefmt="grid",stralign="right")],
                                        [tabulate([["Standard Deviation of Unique Public Peering Capacity"],["{:,}G".format(int(round(stdDevSpeedIn['meanGig'],2)))]],tablefmt="grid",headers="firstrow",stralign="right")],
                                        [tabulate([["Mode Average Unique Peering Point Capacity"],["{0}G".format(stdDevSpeedIn['mode'])]],tablefmt="grid",headers="firstrow",stralign="right")]

				],tablefmt="fancy_grid",stralign="right")

			,
			"ExecutiveSummary"]

			print outTable[0]
			
                        # Calls print function to preset option to print to file
                        filePrintMode(outTable)

	return outTable

	
# Command line initialiser
if __name__ == "__main__":

	startPage()
	
