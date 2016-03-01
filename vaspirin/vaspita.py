#!/usr/bin/env python
import numpy as np
import math
import procar
import sys
import dos
import bandstructure
import bandcharacter
import procar
import plotter
import pyplot

'''
This is the main script from vaspita.py
call it using: vaspita -$tags -$DesiredFileNames

READING TAGS:
By default, the informations are extracted from OUTCAR and PROCAR files. If tag -fromdat is activated, vaspita will only read the information from the given .dat file.

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
-kptgen: generate one a KPOINTS file with a desired path




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





###########################################     CODE     #######################################################
print '\n**************************************************\n**************************************************'
print 'WELCOME TO VASPITA.PY \n'



print 'Made by: I. Guilhon and D. S. Koda.\n'
print 'STARTING LOG...'

###################################     IDENTIFICATING TASKS        #########################################
print ('\n**************************************************\n**************************************************')
print ('WELCOME TO VASPIRIN.PY \n')



print ('Made by: I. Guilhon and D. S. Koda.\n')
print ('Group of Semiconductor Materials and Nanotechnology\n')
print ('Instituto Tecnologico de Aeronautica\n')
print ('http://www.gmsn.ita.br/?q=en\n')
print ('STARTING LOG...')
###################################     IDENTIFICATING TASKS        #########################################
'''
List of useful flags:
flagFROMDAT= sets from dat
flagBS= Build bandstructure
flagDOS= Build density of states
flagCHAR= Add informations of projections on atomic orbitals to BandStructure  
flagPROJ= Add informations of projections on atomic sites to BandStructure 
flagPLOT= Activate plot mode
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


#CHAR FLAG
[flagCHAR,PROCARfile] = testFlag('-char', 'PROCAR',sys.argv)
if flagCHAR and not(flagFROMDAT):
	print ('Band Character info extracted from:', PROCARfile)
	procarData=bandcharacter.PROCAR(PROCARfile)


print (sys.argv)
#PROJ FLAG
[flagPROJ,PROCARfile] = testFlag('-proj', 'PROCAR',sys.argv)
if flagPROJ and not(flagFROMDAT):
	print ('Projection on atomic orbitals info extracted from:', PROCARfile)

		
	#reading [projection settings]:  -proj >>[mat1=...;mat2=...;...]<< -othertags
	readingProj=True
	projectionArgs=''
	k =(sys.argv).index('-proj')+1
	while k < len(sys.argv) and readingProj:
		projectionArgs=projectionArgs+sys.argv[k]
		try:		
			if(sys.argv[k+1][0]=='-'):
				readingProj=False
		except (IOError,IndexError,RuntimeError, TypeError, NameError):
			readingProj=False
		k=k+1
	print (projectionArgs)
		

			

			
		

	#call projection methods

	#KPTGEN FLAG
	#these methods will not read files, but only write new ones.  



	###################################     MAKING OUTPUTS        #########################################

#PLOT FLAG
[flagPLOT,figureName] = testFlag('-plot', 'figure',sys.argv)
if flagPLOT:
	print ('Printing results on:', figureName)

	#call plotter methods

#PYPLOT FLAG
[flagPLOT,figureName] = testFlag('-pyplot', 'figure',sys.argv)
if flagPLOT:
	print ('Printing results on:', figureName)

	#call plotter methods
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

		


