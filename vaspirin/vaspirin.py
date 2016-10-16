#!/usr/bin/env python

import sys
from . import *
import argparse

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
						"Written by Daniel S. Koda and Ivan Guilhon\n" +
						"Group of Semiconductor Materials and Nanotechnology\n" +
						"Instituto Tecnologico de Aeronautica, Brazil\n" +
						"http://www.gmsn.ita.br/?q=en"
						
	parser = argparse.ArgumentParser(description=helloDescription,
									epilog= "Last revision: Oct. 2016.",
									prog="Vaspirin")

	# Vaspirin configurations
	parser.add_argument('-q', '--quiet', action='store_true',
						help="do not display text on the output window (default: False)")
	
	parser.add_argument('-k', '--kpoints', default='KPOINTS',
						help="select KPOINTS file (default: KPOINTS)")
	
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.2')
						
	# Band structure options					
	parser.add_argument('-b', '--bands', action='store_true',
						help="generate simple band structures with XMGrace (default: False)")
	
	parser.add_argument('-o', '--orbital', action='store_true',
						help="generate band structures projected onto atomic orbitals with XMGrace" +
						" (default: False).")
	
	parser.add_argument('-p', '--projected', action='store_true',
						help="generate band structures projected onto atomic sites with XMGrace" +
						" (default: False).")

	parser.add_argument('-c', '--compare', action='store_true',
						help="generate band structures by comparing two input files" +
						" (inputs: eigenv1.dat eigenv2.dat).",
						)
						
	# Band structure tweaking					
	parser.add_argument('-i', '--ignore', type=positive_int, default=0,
						help="ignore the first N k-points when plotting bands (default: 0)")
	
	parser.add_argument('-t', '--interpolate', type=positive_int, default=0,
						help="interpolate N k-points between each pair of k-points when plotting bands (default: 0)")
						
	parser.add_argument('-m', '--marker', type=float, default=0.5,
						help="size of the marker for projected bands (default: 0.5)")
						
	parser.add_argument('-y', '--yaxis', type=float, nargs=2, default=[-3, 3],
						help="set the y-axis range for the band structure" +
						" (default: -3 to 3).",
						metavar=('Y_MIN', 'Y_MAX'))					

	parser.add_argument('-r', '--reference', default='vbm',
						help="reference for the 0 eV in band structures (default: vbm)")

	parser.add_argument('-s', '--soc', action='store_true',
						help="plot bands from non-collinear calculations (default: False)")
	
	# Density of states options
	
	parser.add_argument('-d', '--dos', default='DOSCAR',
						help="generate simple density of states with XMGrace")
	
	return parser.parse_args()

def printHello ():
	'''
	Print hello message.
	'''
	
	print ("***********************")
	print ("     vaspirin v1.2     ")
	print ("***********************")

def printRunDescription (args):
	'''
	Print description of the options chosen and the crystals input.
	'''
	
	leftJustSpace = 20
	print ("input file:".ljust(leftJustSpace) + "%s" % args.input_file)
	print ("output file:".ljust(leftJustSpace) + "%s" % args.output)
	print ("molecule:".ljust(leftJustSpace) + "from atom %d to %d" % (args.molecule[0], args.molecule[1]))
	print ("angles:".ljust(leftJustSpace) + "from %.2f to %.2f deg" % (args.angles[0], args.angles[1]))
	print ("angles_step:".ljust(leftJustSpace) + "%.2f deg" % args.angles_step)
	print ("reference:".ljust(leftJustSpace) + "atom %s" % args.ref)
	print ("axis:".ljust(leftJustSpace) + "%s" % args.axis)


def main():
	'''
	vaspirin main function
	
	By default, informations are extracted from typical VASP files, such as:
	OUTCAR, PROCAR, KPOINTS, DOSCAR
	'''
	
	## Parse arguments from the command line
	args = parseArgs()
	
	## Print information on the screen only if the user wants to receive it
	if not args.quiet:
		printHello ()
		printRunDescription (args)

	## Create classes responsible for processing files
	dat = plotter.DatFiles ()
	dat.setInterpolateOptions (args.interpolate)
	plt = plotter.Grace ()
	
	# Reading the KPOINTS file:
	try:
		plt.readXticks (KPOINTSfile)
	except:
		print ("Wrong header formatting in KPOINTS file. Plotting without k-points on the x axis...")
			
		
	# plot using XMGrace
	if flagBS:
		if flagDOS:
			print ("Feature not yet implemented. Feel free to work on it if you want!")
			# Print DOS with bands
		
		elif flagCHAR:
			dat.datCharacter (bsData, procarData)
			plt.printBandCharacter (bsData)
			print ("Print the results using XMgrace\n xmgrace -batch bandsCharacter.bfile")
			
		elif flagPROJ:
			dat.datProjected (bsData, projData)
			plt.printBandProjected (bsData, projData)
			print ("Print the results using XMgrace\n xmgrace -batch bandsProjected.bfile")
		else:
			dat.datEigenvals (bsData)
			plt.printBandStructure (bsData)
			print ("Print the results using XMgrace\n xmgrace -batch bands.bfile")
	
	elif flagCOMPARE:
			dat.datEigenvals (bsData1, datName='eigenv1.dat')
			dat.datEigenvals (bsData2, datName='eigenv2.dat')
			plt.printComparisonBands (bsData1, bsData2)
			print ("Print the results using XMgrace\n xmgrace -batch bandsComparison.bfile")
			
	else:
		if flagDOS:
			print ("Feature not yet implemented. Feel free to work on it if you want!")
	
	print ("(add -hardcopy -nosafe to the xmgrace command if you want to print it directly)")
