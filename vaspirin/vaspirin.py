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



###########################################   METHODS    #######################################################
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




def main():
	
	###########################################     CODE     #######################################################
	print ('\n**************************************************')
	print ('WELCOME TO VASPIRIN.PY')
	print ('**************************************************\n')



	print ('Made by: I. Guilhon and D. S. Koda.')
	print ('Group of Semiconductor Materials and Nanotechnology')
	print ('Instituto Tecnológico de Aeronáutica')
	print ('http://www.gmsn.ita.br/?q=en')
	print ('STARTING LOG...')

	###################################     IDENTIFICATING TASKS        #########################################
	'''
	List of useful flags:
	flagFROMDAT= sets from dat
	flagBS=
	flagDOS=
	flagCHAR=
	flagPROJ=
	flagPLOT=
	'''


	# fromdat FLAG
	[flagFROMDAT,DATFile] = testFlag('-fromdat', 'input.dat',sys.argv)
	if flagFROMDAT:
		print ('Info extracted from file:', DATFile)
		#Read dat file


	# BANDSTRUCTURE FLAG
	[flagBS,OUTCARfile] = testFlag('-bs', 'OUTCAR',sys.argv)
	if flagBS and not(flagFROMDAT):
		print ('OUTCAR info extracted from:', OUTCARfile)
		bsData=bandstructure.BandStructure(OUTCARfile)


	# DOS FLAG	
	[flagDOS,DOSCARfile] = testFlag('-dos', 'DOSCAR',sys.argv)
	if flagDOS and not(flagFROMDAT):
		print ('DOSCAR info extracted from:', DOSCARfile)
		dosData=dos.DOS(DOSCARfile)


	# CHAR FLAG
	[flagCHAR,PROCARfile] = testFlag('-char', 'PROCAR',sys.argv)
	if flagCHAR and not(flagFROMDAT):
		print ('Band Character info extracted from:', PROCARfile)
		procarData=bandcharacter.PROCAR(PROCARfile)


	# PROJ FLAG
	[flagPROJ,PROCARfile] = testFlag('-proj', 'PROCAR',sys.argv)
	[flagPROJFILE,PROJECTIONfile] = testFlag('-projfile', 'PROJECTION',sys.argv)
	
	if flagPROJ and not(flagFROMDAT):
		print ('Projection on atomic orbitals info extracted from:', PROCARfile)
		
		projData = bandcharacter.PROCAR (PROCARfile)
		
		# Opens the file 'PROJECTION' if the argument -projdata is not specified
		projData.createIonVsMaterials (PROJECTIONfile)

	[flagKPOINTS,KPOINTSfile] = testFlag('-kpt', 'KPOINTS',sys.argv)
	

	#KPTGEN FLAG
	#these methods will not read files, but only write new ones.  



	###################################     MAKING OUTPUTS        #########################################

	# PLOT FLAG
	[flagPLOT,figureName] = testFlag('-plot', 'figure',sys.argv)
	if flagPLOT:
		dat = plotter.DatFiles ()
		plt = plotter.Grace ()
		
		# Optional argument: markerSize tunes the size of the marker on projected band structures
		markerSize = -1
		
		# Yet to implement: export PDF to figureName
		print ('Printing results on:', figureName, '\n')
		
		# Reading the KPOINTS file:
		try:
			plt.readXticks (KPOINTSfile)
		except:
			print ("KPOINTS file not found. Plotting without k-points on the x axis...")
		
		
		# plot using XMGrace
		if flagBS:
			if flagDOS:
				print ("Feature not yet implemented. Feel free to work on it if you want!")
				# Print DOS with bands
			
			elif flagCHAR:
				dat.datCharacter (bsData, procarData, markerSize)
				plt.printBandCharacter (bsData)
				print ("Print the results using XMgrace\n $ xmgrace -batch bandsCharacter.bfile")
				
			elif flagPROJ:
				dat.datProjected (bsData, projData, markerSize)
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

