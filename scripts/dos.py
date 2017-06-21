#!/usr/bin/env python3

import sys
from vaspirin import doscar,projection
from vaspirin import graceIO,datIO
import argparse

################################
## PARSING AND HELLO MESSAGES ##
################################

def positive_int (value):
	'''
	Type for allowing only positive int values for argparser
	taken from http://stackoverflow.com/questions/14117415/using-argparse-allow-only-positive-integers
	'''

	ivalue = int(value)
	if ivalue < 0:
		raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
	return ivalue
    
def parseArgs():
	"""
	Parse arguments from the command line. Uses the `argparse` package to
	establish all positional and optional arguments.
	"""
	
	helloDescription = ("Painless VASP postprocessing tool: " + 
						"Generates density of states from VASP files\n" + 
						"Written by Daniel S. Koda, " +
						"Group of Semiconductor Materials and Nanotechnology, " +
						"Instituto Tecnologico de Aeronautica, Brazil " +
						"(http://www.gmsn.ita.br/?q=en)")
						
	parser = argparse.ArgumentParser(description=helloDescription,
									epilog= "Last revision: Feb. 2017.",
									prog="dos.py")

	# Vaspirin configurations
	parser.add_argument('-q', '--quiet', action='store_true',
						help="do not display text on the output window (default: False)")
	
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.2')
						
	# Band structure options					
	parser.add_argument('-o', '--orbital', action='store_true',
						help="generate density of states projected onto atomic orbitals with XMGrace" +
						" (default: False).")
	
	parser.add_argument('-p', '--projected', action='store_true',
						help="generate density of states projected onto atomic sites with XMGrace" +
						" (default: False).")
						
	parser.add_argument('-f', '--fill', action='store_true',
						help="whether or not fill the lines in the plot (default: False)")
						
	parser.add_argument('-y', '--yaxis', type=float, nargs=2, default=[-3, 3],
						help="set the energy axis range for the density of states" +
						" (default: -3 to 3).",
						metavar=('Y_MIN', 'Y_MAX'))	
									
	parser.add_argument('-d', '--dos_axis', type=float, default=40.0,
						help="set the maximum range for the density of states axis" +
						" (default: 40.0).")					

	parser.add_argument('-r', '--ref', default='e-fermi',
						help="reference for the 0 eV in density of states (default: e-fermi)")
	
	return parser.parse_args()

def printHello ():
	'''
	Print hello message.
	'''
	
	print ("********************")
	print (" vaspirin v2.0: dos ")
	print ("********************")

def printRunDescription (args):
	'''
	Print description of the options chosen and the crystals input.
	'''
	
	leftJustSpace = 20
	print ("required files:".ljust(leftJustSpace) + "DOSCAR" + (", PROJECTION" if args.projected else ""))

	print ("fill lines?".ljust(leftJustSpace) + ("yes" if args.fill else "no"))
	print ("reference:".ljust(leftJustSpace) + "%s" % args.ref)
	print ("energy axis:".ljust(leftJustSpace) + "from %.1f to %.1f" % (args.yaxis[0],args.yaxis[1]))
	print ("DOS axis:".ljust(leftJustSpace) + "from 0.0 to %.1f" % (args.dos_axis))
	print ("projected onto:".ljust(leftJustSpace) + ("orbitals" if args.orbital else "sites" if args.projected else "not projected"))
	print ("")

########################
## PLOTTING FUNCTIONS ##
########################

def printDOS (xmgrace, dos):
	"""
	Prints a .bfile for a common DOS
	This method contains all needed settings
	"""

	## Read the file
	with open ('dos.bfile', 'w') as outputFile:				
		
		outputFile.write ("READ NXY \"dos.dat\" \n")
		
		xmgrace.printFontSection (outputFile)
		xmgrace.printView (outputFile)
		xmgrace.printDOSAxis (outputFile)
		xmgrace.printDOS (outputFile, dos, traceColor='black')
		xmgrace.printDOSLabel (outputFile)
		

def printDOSorbital (xmgrace, dos):
	"""
	Prints a .bfile for a band structure projected onto orbitals
	"""
	
	## Read the file
	with open ('dosOrbital.bfile', 'w') as outputFile:				
		
		outputFile.write ("READ NXY \"dosOrbital.dat\" \n")
		
		xmgrace.printFontSection (outputFile)
		xmgrace.printView (outputFile)
		xmgrace.printDOSAxis (outputFile)
		xmgrace.printDOSCharacter (outputFile, dos)
		xmgrace.printDOSLabel (outputFile)

def printDOSprojected (xmgrace, dos):
	"""
	Prints a .bfile for a band structure projected onto the specified materials (file PROJECTION)
	This method contains all needed settings
	"""
	
	## Read the file
	with open ('dosProjected.bfile', 'w') as outputFile:				
		
		outputFile.write ("READ NXY \"dosProj.dat\" \n")
		
		xmgrace.printFontSection (outputFile)
		xmgrace.printView (outputFile)
		xmgrace.printDOSAxis (outputFile)
		xmgrace.printDOSProjected (outputFile, dos)
		xmgrace.printDOSLabel (outputFile)

			

###################
## MAIN FUNCTION ##
###################
	
def main():
	'''
	vaspirin main function
	
	By default, informations are extracted from typical VASP files, such as OUTCAR, PROCAR, KPOINTS,
	and from personalized data, such as PROJECTION files
	'''
	
	## Parse arguments from the command line
	args = parseArgs()
	
	## Print information on the screen only if the user wants to receive it
	if not args.quiet:
		printHello ()
		printRunDescription (args)

	## Create classes responsible for processing files
	dat = datIO.DatFiles ()
	xmgrace = graceIO.Grace ()
	
	## Set whether the symbols are filled within xmgrace
	xmgrace.setSymbolFill (args.fill)
	
	## Set the range of the y axis
	xmgrace.setXaxis (args.yaxis[0], args.yaxis[1])		
	xmgrace.setYaxis (0, args.dos_axis)		
	
	## Set the DOS view for the plot
	xmgrace.setView (graceIO.GraceConstants.dosView)
	
	dos = doscar.DOS(fDoscar = "DOSCAR")
	dos.setReferenceString (args.ref)
	
	## Atomic orbital-projected DOS
	if args.orbital:
		
		dat.datDOSorbital (dos)
		printDOSorbital (xmgrace, dos)
		
		if not args.quiet:
			print ("Print the results using XMgrace:\n xmgrace -batch dosOrbital.bfile")
	
	## Atomic site-projected DOS
	elif args.projected:
		prj = projection.PROJECTION (fProjection = 'PROJECTION')
		dos.setProjection (prj)
		dos.sumContributions ()
		
		dat.datDOSproj (dos)
		
		xmgrace.setProjectedColors (prj.projectedColors)
		printDOSprojected (xmgrace, dos)
		
		if not args.quiet:
			print ("Print the results using XMgrace:\n xmgrace -batch dosProjected.bfile")
	
	## Standard DOS	
	else:
		dat.datDOS (dos)
		printDOS (xmgrace, dos)
		
		if not args.quiet:
			print ("Print the results using XMgrace:\n xmgrace -batch dos.bfile")
	
	#~ print ("(add -hardcopy -nosafe to the xmgrace command if you want to print it directly)")

if __name__ == "__main__":
	main ()
