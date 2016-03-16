#!/usr/bin/env python

import sys
from . import *

'''
This is the main script from vaspirin.py
call it using: vaspirin -$tags -$DesiredFileNames

READING TAGS:
By default, informations are extracted from OUTCAR and PROCAR files. If tag -fromdat is activated, vaspita will only read the information from the given .dat file.

-dos: ask for Density of State informations.
-bs: ask for Electronic Band Structure informations.
-char: ask for Character of electronic bands projected on atomic orbitals (s,p,d,f).
-proj: ask for Character of electronic bands projected on specific atoms.

OUTPUT AND PLOTTING TAGS:
-fromdat: Sets a given .dat file as the source of information ask. 
	e.g.: python vaspita.py -bs -fromdat bandsStructure.dat
	
	If not active, the script will ask for OUTCAR and/or procar files.

-plot: Create .dat, .ps and .pdf files


WRITING TAGS:
-kptgen: generate one KPOINTS file with a desired path




'''



###########################################   FUNCTIONS    #######################################################

def testFlag(tag, defaultName,args):
	fileName=defaultName
	flag=False
	if tag in  args:
		flag=True
		index= (sys.argv).index(tag)
		try:
			newName=sys.argv[index +1]
			if  newName[0]!='-':
				fileName=newName
		except (IOError,IndexError,RuntimeError, TypeError, NameError):
			fileName=defaultName

	return [flag, fileName]


# Same as function testFlag, but receives two arguments for the tag
def testFlag2args(tag, default1, default2, args):
	attribute1 = default1
	attribute2 = default2
	
	flag=False
	
	if tag in  args:
		flag=True
		index= (sys.argv).index(tag)
		
		# Try to read the first attribute
		try:
			newName1 = sys.argv[index + 1]
			if  newName1[0] != '-':
				attribute1 = newName1
			elif newName1[1].isnumeric():
				attribute1 = newName1
				
		# If the reading fails, returns to the default value
		except (IOError,IndexError,RuntimeError, TypeError, NameError):
			attribute1 = default1
		
		# Try to read the second attribute
		try:
			newName2 = sys.argv[index + 2]
			if  newName2[0] != '-':
				attribute2 = newName2
			elif newName2[1].isnumeric():
				attribute2 = newName2
				
		# If the reading fails, returns to the default value
		except (IOError,IndexError,RuntimeError, TypeError, NameError):
			attribute2 = default2	

	return [flag, attribute1, attribute2]

def hello ():
	print ('\n**************************************************')
	print ('WELCOME TO VASPIRIN.PY')
	print ('**************************************************\n')

	print ('Made by Daniel S. Koda and Ivan Guilhon.')
	print ('Group of Semiconductor Materials and Nanotechnology')
	print ('Instituto Tecnologico de Aeronautica')
	print ('http://www.gmsn.ita.br/?q=en')
	print ('STARTING LOG...')

def main():
	
	###########################################     CODE     #######################################################
	
	[flagQUIET, quietPostArgument] = testFlag('-quiet', '', sys.argv)
	if not flagQUIET:
		hello()
		

	###################################     IDENTIFICATING TASKS        #########################################
	
	# do not plot the first N k-points if '-ignore N' is given
	[flagIGNORE, nKPTignore] = testFlag('-ignore', 0, sys.argv)
	
	try:
		nKPTignore = int (nKPTignore)
	except ValueError:
		print ('Invalid -ignore argument. Please input an integer number. Using 0 as default...')
		nKPTignore = 0
	
	# fromdat FLAG
	[flagFROMDAT,DATFile] = testFlag('-fromdat', 'input.dat',sys.argv)
	if flagFROMDAT:
		print ('Info extracted from file:', DATFile)
		#Read dat file

	
	# BANDSTRUCTURE FLAG
	[flagBS,OUTCARfile] = testFlag('-bs', 'OUTCAR',sys.argv)
	if flagBS and not(flagFROMDAT):
		print ('OUTCAR info extracted from: ' + OUTCARfile)
		bsData=bandstructure.BandStructure(OUTCARfile, nKPTignore)


	# DOS FLAG	
	[flagDOS,DOSCARfile] = testFlag('-dos', 'DOSCAR',sys.argv)
	if flagDOS and not(flagFROMDAT):
		print ('DOSCAR info extracted from: ' + DOSCARfile)
		dosData=dos.DOS(DOSCARfile)


	# CHAR FLAG
	[flagCHAR,PROCARfile] = testFlag('-char', 'PROCAR',sys.argv)
	if flagCHAR and not(flagFROMDAT):
		print ('Band Character info extracted from: ' + PROCARfile)
		procarData=bandcharacter.PROCAR(PROCARfile, nKPTignore)


	# PROJ FLAG
	[flagPROJ,PROCARfile,PROJECTIONfile] = testFlag2args('-proj', 'PROCAR', 'PROJECTION',sys.argv)
	
	if flagPROJ and not(flagFROMDAT):
		print ('Projection on atomic orbitals info extracted from: ' + PROCARfile)
		
		projData = bandcharacter.PROCAR (PROCARfile, nKPTignore)
		
		# Opens the file 'PROJECTION' if the argument -projdata is not specified
		projData.createIonVsMaterials (PROJECTIONfile)

	[flagKPOINTS,KPOINTSfile] = testFlag('-kpt', 'KPOINTS',sys.argv)
	
	#KPTGEN FLAG
	#these methods will not read files, but only write new ones.  



	###################################     MAKING OUTPUTS        #########################################
	
	# PLOT FLAG
	[flagPLOT,figureName] = testFlag('-plot', 'figure',sys.argv)
	if flagPLOT:
		
		# Load marker size for the plotter
		[flagMARKER, markerSize] = testFlag('-markersize', 0.5, sys.argv)
		
		try:
			markerSize = float (markerSize)
			if markerSize <= 0:
				raise ValueError ('Negative marker size')
		except ValueError:
			print ('Invalid -markersize argument. Please input a float number. Using 0.5 as default...')
			markerSize = 0.5
		
		dat = plotter.DatFiles (markerSize)
		plt = plotter.Grace ()
		
		
		# Yet to implement: export PDF to figureName
		print ('Printing results on:', figureName, '\n')
		
		# Reading the KPOINTS file:
		try:
			plt.readXticks (KPOINTSfile)
		except:
			print ("KPOINTS file not found. Plotting without k-points on the x axis...")
		
		# Read the y axis minimum and maximum values
		[flagYAXIS, yMin, yMax] = testFlag2args ('-yaxis', -3, 3, sys.argv)

		if flagYAXIS:
			plt.setYaxis (min(float(yMin), float(yMax)), max(float(yMin), float(yMax)))
		
		# plot using XMGrace
		if flagBS:
			if flagDOS:
				print ("Feature not yet implemented. Feel free to work on it if you want!")
				# Print DOS with bands
			
			elif flagCHAR:
				dat.datCharacter (bsData, procarData)
				plt.printBandCharacter (bsData)
				print ("Print the results using XMgrace\n $ xmgrace -batch bandsCharacter.bfile")
				
			elif flagPROJ:
				dat.datProjected (bsData, projData)
				plt.printBandProjected (bsData, projData)
				print ("Print the results using XMgrace\n $ xmgrace -batch bandsProjected.bfile")
			else:
				dat.datEigenvals (bsData)
				plt.printBandStructure (bsData)
				print ("Print the results using XMgrace\n $ xmgrace -batch bands.bfile")
		else:
			if flagDOS:
				print ("Feature not yet implemented. Feel free to work on it if you want!")
		

	# PYPLOT FLAG
	[flagPLOT,figureName] = testFlag('-pyplot', 'figure',sys.argv)
	
	if flagPLOT:
		print ('Printing results on:', figureName)

		if flagBS:
			if flagDOS:
				pyplot.plotBSDOS(bsData,dosData,figureName)
			elif flagCHAR:
				pyplot.plotBSCHAR(bsData,procarData,figureName)
			else:
				pyplot.plotBS(bsData,figureName)

		else:
			if flagDOS:
				pyplot.plotDOS(dosData,figureName)

