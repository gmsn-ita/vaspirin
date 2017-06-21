#!/usr/bin/env python3

import sys
from vaspirin import outcar,graceIO,datIO
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
						"Generates compared band structures from VASP files\n" + 
						"Written by Daniel S. Koda and Ivan Guilhon\n" +
						"Group of Semiconductor Materials and Nanotechnology\n" +
						"Instituto Tecnologico de Aeronautica, Brazil\n" +
						"http://www.gmsn.ita.br/?q=en")
						
	parser = argparse.ArgumentParser(description=helloDescription,
									epilog= "Last revision: Feb. 2017.",
									prog="plot_compared_bands.py")

	# Vaspirin configurations
	parser.add_argument('-q', '--quiet', action='store_true',
						help="do not display text on the output window (default: False)")
	
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.2')
						
	# Band structure options					
	parser.add_argument('input_folders', nargs=2,
						help="paths to the folders in which the calculations can be found")
						
	# Band structure tweaking					
	parser.add_argument('-i', '--ignore', type=positive_int, default=0,
						help="ignore the first N k-points when plotting bands (default: 0)")
	
	parser.add_argument('-t', '--interpolate', type=positive_int, default=0,
						help="interpolate N k-points between each pair of k-points when plotting bands (default: 0)")
						
	parser.add_argument('-c', '--colors', nargs = 2, default=['black','red'],
						help="colors of the bands to be compared (default: black and red)",
						metavar=('COLOR_1', 'COLOR_2'))
						
	parser.add_argument('-y', '--yaxis', type=float, nargs=2, default=[-3, 3],
						help="set the y-axis range for the band structure" +
						" (default: -3 to 3).",
						metavar=('Y_MIN', 'Y_MAX'))					

	parser.add_argument('-r', '--ref', nargs = 2, default=['e-fermi','e-fermi'],
						help="reference for the 0 eV in band structures (default: e-fermi for both)",
						metavar=('REF_1', 'REF_2'))

	parser.add_argument('-s', '--soc', action='store_true',
						help="plot bands from non-collinear calculations (default: False)")
	
	return parser.parse_args()

def printHello ():
	'''
	Print hello message.
	'''
	
	print ("************************************")
	print (" vaspirin v2.0: plot_compared_bands ")
	print ("************************************")

def printRunDescription (args):
	'''
	Print description of the options chosen and the crystals input.
	'''
	
	leftJustSpace = 20
	print ("required files:".ljust(leftJustSpace) + "OUTCAR, KPOINTS")
	print ("colors:".ljust(leftJustSpace) + "%s and %s" % (args.colors[0],args.colors[1]))
	print ("references:".ljust(leftJustSpace) + "%s and %s" % (args.ref[0],args.ref[1]))
	print ("ignoring:".ljust(leftJustSpace) + "%d k-point(s)" % args.ignore)
	print ("interpolating:".ljust(leftJustSpace) + "%d k-point(s)" % args.interpolate)
	print ("y axis:".ljust(leftJustSpace) + "from %.1f to %.1f" % (args.yaxis[0],args.yaxis[1]))
	print ("")

########################
## PLOTTING FUNCTIONS ##
########################

def printComparisonBands (xmgrace, colors, bands1, bands2):
	"""
	Prints a .bfile for a common band structure
	This method contains all needed settings
	"""
		
	with open ('bandsComparison.bfile', 'w') as outputFile:				
		outputFile.write ("READ NXY \"eigenv1.dat\" \n")
		
		xmgrace.printFontSection (outputFile)
		xmgrace.printTraces (outputFile, bands1, traceColor=colors[0], firstBand=0)
		
		outputFile.write ("READ NXY \"eigenv2.dat\" \n")
		
		xmgrace.printTraces (outputFile, bands2, traceColor=colors[1], firstBand=bands1.nBands)

		xmgrace.printAxis (outputFile, bands1)			
		xmgrace.printLabel (outputFile)
			

################################
## MAIN FUNCTION FOR VASPIRIN ##
################################
	
def main():
	'''
	plot_compared_bands main function
	
	By default, informations are extracted from typical VASP files, such as OUTCAR, KPOINTS in each specified path
	'''
	
	## Parse arguments from the command line
	args = parseArgs()
	
	## Print information on the screen only if the user wants to receive it
	if not args.quiet:
		printHello ()
		printRunDescription (args)

	## Read and configure the paths
	try:
		path_1 = args.input_folders[0]
		path_2 = args.input_folders[1]
	except IndexError:
		print ("Two paths must be specified! Exiting...")
		sys.exit(1)
	
	if path_1[-1] != '/':
		path_1 += '/'
	if path_2[-1] != '/':
		path_2 += '/'
		
	## Create classes responsible for processing files
	dat = datIO.DatFiles ()
	dat.setInterpolateOptions (args.interpolate)
	xmgrace = graceIO.Grace ()
	
	# Reading the KPOINTS file from path 1
	try:
		xmgrace.readXticks (path_1 + 'KPOINTS')
	except:
		print ("Wrong header formatting in KPOINTS file. Plotting without k-points on the x axis...")
	
	## Set the range of the y axis
	xmgrace.setYaxis (args.yaxis[0], args.yaxis[1])		
	
	## Configuring the band structure data
	bsData_1 = outcar.BandStructure (fOutcar = path_1 + 'OUTCAR', nKPTignore = args.ignore)
	bsData_1.setReferenceString(args.ref[0])
	bsData_1.setSOC(args.soc)
	
	bsData_2 = outcar.BandStructure (fOutcar = path_2 + 'OUTCAR', nKPTignore = args.ignore)
	bsData_2.setReferenceString(args.ref[1])
	bsData_2.setSOC(args.soc)
	
	dat.datEigenvals (bsData_1, datName='eigenv1.dat')
	dat.datEigenvals (bsData_2, datName='eigenv2.dat')
	printComparisonBands (xmgrace, args.colors, bsData_1, bsData_2)
	
	print ("Print the results using XMgrace\n xmgrace -batch bandsComparison.bfile")
	
	#~ print ("(add -hardcopy -nosafe to the xmgrace command if you want to print it directly)")

if __name__ == "__main__":
	main ()
