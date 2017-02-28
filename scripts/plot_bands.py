#!/usr/bin/env python

import sys
from vaspirin import outcar,procar,projection
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
	
	helloDescription = ("Painless VASP postprocessing tool\n" + 
						"Generates band structures from VASP files\n" + 
						"Written by Daniel S. Koda and Ivan Guilhon\n" +
						"Group of Semiconductor Materials and Nanotechnology\n" +
						"Instituto Tecnologico de Aeronautica, Brazil\n" +
						"http://www.gmsn.ita.br/?q=en")
						
	parser = argparse.ArgumentParser(description=helloDescription,
									epilog= "Last revision: Feb. 2017.",
									prog="plot_bands.py")

	# Vaspirin configurations
	parser.add_argument('-q', '--quiet', action='store_true',
						help="do not display text on the output window (default: False)")
	
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.2')
						
	# Band structure options					
	parser.add_argument('-o', '--orbital', action='store_true',
						help="generate band structures projected onto atomic orbitals with XMGrace" +
						" (default: False).")
	
	parser.add_argument('-p', '--projected', action='store_true',
						help="generate band structures projected onto atomic sites with XMGrace" +
						" (default: False).")
						
	# Band structure tweaking					
	parser.add_argument('-i', '--ignore', type=positive_int, default=0,
						help="ignore the first N k-points when plotting bands (default: 0)")
	
	parser.add_argument('-t', '--interpolate', type=positive_int, default=0,
						help="interpolate N k-points between each pair of k-points when plotting bands (default: 0)")
						
	parser.add_argument('-m', '--marker', type=float, default=0.5,
						help="size of the marker for projected bands (default: 0.5)")
	
	parser.add_argument('-f', '--fill', action='store_true',
						help="whether or not fill the symbols in the plot (default: False)")
						
	parser.add_argument('-y', '--yaxis', type=float, nargs=2, default=[-3, 3],
						help="set the y-axis range for the band structure" +
						" (default: -3 to 3).",
						metavar=('Y_MIN', 'Y_MAX'))					

	parser.add_argument('-r', '--ref', default='vbm',
						help="reference for the 0 eV in band structures (default: vbm)")

	parser.add_argument('-s', '--soc', action='store_true',
						help="plot bands from non-collinear calculations (default: False)")
	
	return parser.parse_args()

def printHello ():
	'''
	Print hello message.
	'''
	
	print ("***************************")
	print (" vaspirin v2.0: plot_bands ")
	print ("***************************")

def printRunDescription (args):
	'''
	Print description of the options chosen and the crystals input.
	'''
	
	leftJustSpace = 20
	print ("required files:".ljust(leftJustSpace) + "OUTCAR, KPOINTS" + (", PROCAR" if (args.projected or args.orbital) else "") + (", PROJECTION" if args.projected else ""))

	if (args.projected or args.orbital):
		print ("marker size:".ljust(leftJustSpace) + "%.2f" % (args.marker))
		print ("fill markers?".ljust(leftJustSpace) + ("yes" if args.fill else "no"))

	print ("reference:".ljust(leftJustSpace) + "%s" % args.ref)
	print ("ignoring:".ljust(leftJustSpace) + "%d k-point(s)" % args.ignore)
	print ("interpolating:".ljust(leftJustSpace) + "%d k-point(s)" % args.interpolate)
	print ("y axis:".ljust(leftJustSpace) + "from %.1f to %.1f" % (args.yaxis[0],args.yaxis[1]))
	print ("projected onto:".ljust(leftJustSpace) + ("orbitals" if args.orbital else "sites" if args.projected else "not projected"))
	print ("")

########################
## PLOTTING FUNCTIONS ##
########################

def printBandStructure (xmgrace, bands):
	"""
	Prints a .bfile for a common band structure
	This method contains all needed settings
	"""

	## Read the file
	with open ('bands.bfile', 'w') as outputFile:				
		
		outputFile.write ("READ NXY \"eigenv.dat\" \n")
		
		xmgrace.printFontSection (outputFile)
		xmgrace.printAxis (outputFile, bands)
		xmgrace.printTraces (outputFile, bands, traceColor='black', firstBand=0)
		xmgrace.printLabel (outputFile)
		
		if xmgrace.exportPS:
			xmgrace.printExportPS (outputFile, self.psFilename)

def printBandCharacter (xmgrace, bands):
	"""
	Prints a .bfile for a band structure projected onto orbitals
	"""
	
	## Read the file
	with open ('bandsCharacter.bfile', 'w') as outputFile:				
		
		xmgrace.printFontSection (outputFile)
		xmgrace.printTracesCharacter (outputFile, bands)
		xmgrace.printAxis (outputFile, bands)
		xmgrace.printLabel (outputFile)

def printBandProjected (xmgrace, bands, projectedBands):
	"""
	Prints a .bfile for a band structure projected onto the specified materials (file PROJECTION)
	This method contains all needed settings
	"""
	
	## Read the file
	with open ('bandsProjected.bfile', 'w') as outputFile:				
		
		xmgrace.printFontSection (outputFile)
		xmgrace.printTracesProjected (outputFile, bands, projectedBands)
		xmgrace.printAxis (outputFile, bands)			
		xmgrace.printLabel (outputFile)

			

################################
## MAIN FUNCTION FOR VASPIRIN ##
################################
	
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
	dat.setInterpolateOptions (args.interpolate)
	xmgrace = graceIO.Grace ()
	
	# Reading the KPOINTS file:
	try:
		xmgrace.readXticks ('KPOINTS')
	except:
		print ("Wrong header formatting in KPOINTS file. Plotting without k-points on the x axis...")
	
	## Set whether the symbols are filled within xmgrace
	xmgrace.setSymbolFill (args.fill)
	
	## Set the range of the y axis
	xmgrace.setYaxis (args.yaxis[0], args.yaxis[1])		
		
	bsData = outcar.BandStructure (nKPTignore = args.ignore)
	bsData.setSOC (args.soc)
	bsData.setReferenceString (args.ref)
	
	## Atomic orbital-projected band structure
	if args.orbital:
		prj = projection.PROJECTION (fProjection = 'PROJECTION')
		procarData = procar.PROCAR ('PROCAR', prj, nKPTignore = args.ignore)
		
		dat.datCharacter (bsData, procarData)
		printBandCharacter (xmgrace, bsData)
		
		if not args.quiet:
			print ("Print the results using XMgrace:\n xmgrace -batch bandsCharacter.bfile")
	
	## Atomic site-projected band structure	
	elif args.projected:
		prj = projection.PROJECTION (fProjection = 'PROJECTION')
		procarData = procar.PROCAR ('PROCAR', prj, nKPTignore = args.ignore)
		
		dat.datProjected (bsData, procarData)
		
		xmgrace.setProjectedColors (prj.projectedColors)
		printBandProjected (xmgrace, bsData, procarData)
		
		if not args.quiet:
			print ("Print the results using XMgrace:\n xmgrace -batch bandsProjected.bfile")
	
	## Standard band structure	
	else:
		dat.datEigenvals (bsData)
		printBandStructure (xmgrace, bsData)
		
		if not args.quiet:
			print ("Print the results using XMgrace:\n xmgrace -batch bands.bfile")
	
	#~ print ("(add -hardcopy -nosafe to the xmgrace command if you want to print it directly)")

if __name__ == "__main__":
	main ()
