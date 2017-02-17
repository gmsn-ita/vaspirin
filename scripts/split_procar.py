from vaspirin import outcar,splitter,graceIO,projection
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
	
	helloDescription = ("Big PROCAR files splitter\n" + 
						"Written by Daniel S. Koda\n" +
						"Group of Semiconductor Materials and Nanotechnology\n" +
						"Instituto Tecnologico de Aeronautica, Brazil\n" +
						"http://www.gmsn.ita.br/?q=en"
						)
						
	parser = argparse.ArgumentParser(description=helloDescription,
									epilog= "Last revision: Jan. 2017.",
									prog="split_procar.py")

	# Configurations
	parser.add_argument('-q', '--quiet', action='store_true',
						help="do not display text on the output window (default: False)")
	
	parser.add_argument('-v', '--version', action='version', version='%(prog)s 1.0')
							
	# Band structure tweaking					
	parser.add_argument('-i', '--ignore', type=positive_int, default=0,
						help="ignore the first N k-points when plotting bands (default: 0)")
						
	parser.add_argument('-m', '--marker', type=float, default=0.5,
						help="size of the marker for projected bands (default: 0.5)")
						
	parser.add_argument('-y', '--yaxis', type=float, nargs=2, default=[-3, 3],
						help="set the y-axis range for the band structure" +
						" (default: -3 to 3).",
						metavar=('Y_MIN', 'Y_MAX'))					

	parser.add_argument('-r', '--ref', default='vbm',
						help="reference for the 0 eV in band structures (default: vbm)")

	parser.add_argument('-s', '--split', action='store_true',
						help="whether or not split the big PROCAR file (default: False)")
						
	parser.add_argument('-o', '--orbitals', action='store_true',
						help="whether or not split the big PROCAR file onto atomic orbitals (default: False)")
	
	parser.add_argument('-f', '--fill', action='store_true',
						help="whether or not fill the symbols in the plot (default: False)")
						
	return parser.parse_args()

def printHello ():
	'''
	Print hello message.
	'''
	
	print ("*****************************")
	print (" vaspirin v2.0: split_procar ")
	print ("*****************************")

def printRunDescription (args):
	'''
	Print description of the options chosen and the crystals input.
	'''
	
	leftJustSpace = 20
	print ("required files:".ljust(leftJustSpace) + "OUTCAR, KPOINTS, PROCAR, PROJECTION")
	print ("marker size:".ljust(leftJustSpace) + "%.2f" % (args.marker))
	print ("fill markers?".ljust(leftJustSpace) + ("yes" if args.fill else "no"))
	print ("reference:".ljust(leftJustSpace) + "%s" % args.ref)
	print ("ignoring:".ljust(leftJustSpace) + "%d k-point(s)" % args.ignore)
	print ("axis:".ljust(leftJustSpace) + "from %.1f to %.1f" % (args.yaxis[0],args.yaxis[1]))
	print ("split file?".ljust(leftJustSpace) + ("yes" if args.split else "no"))
	print ("projected onto:".ljust(leftJustSpace) + ("orbitals" if args.orbitals else "sites"))


def printBandProjected (grace, bands, projectedBands):
	"""
	Prints a .bfile for a band structure projected onto the specified materials (as from file PROJECTION)
	This method contains all needed settings
	"""
	
	## Read the file
	with open ('bandsProjected.bfile', 'w') as outputFile:				
				
		grace.printFontSection (outputFile)
		grace.printTracesProjected (outputFile, bands, projectedBands)
		grace.printAxis (outputFile, bands)			
		grace.printLabel (outputFile)


def printBandCharacter (self, bands):
	"""
	Prints a .bfile for a band structure projected onto orbitals
	The variable markerSize specifies the size of the marker while printing the bands
	"""
	
	## Read the file
	with open ('bandsCharacter.bfile', 'w') as outputFile:				
		
		self.printFontSection (outputFile)
		self.printTracesCharacter (outputFile, bands)
		self.printAxis (outputFile, bands)
		self.printLabel (outputFile)


def main():
	'''
	Split big PROCAR files into .dat files according to the projection data
	'''
	
	## Parse arguments from the command line
	args = parseArgs()
	
	## Print information on the screen only if the user wants to receive it
	if not args.quiet:
		printHello ()
		printRunDescription (args)
	
	## Import band structures
	bands = outcar.BandStructure (fOutcar = "OUTCAR", nKPTignore = args.ignore)
	bands.setReferenceString(args.ref)

	## Import PROJECTION customization file
	prj = projection.PROJECTION (fProjection = 'PROJECTION')
	
	## Import and split PROCAR file
	p = splitter.PROCAR_splitter('PROCAR', prj, bands, marker = args.marker, nKPTignore = args.ignore)
	
	if args.split:
		if args.orbitals:
			p.splitOrbitals ()
		else:
			p.splitPROCAR ()

	## Plotting the files just created
	plt = graceIO.Grace ()
	
	## Set whether the symbols are filled within xmgrace
	plt.setSymbolFill (args.fill)
	
	# Reading the KPOINTS file:
	try:
		plt.readXticks ('KPOINTS')
	except:
		print ("Wrong header formatting in KPOINTS file. Plotting without k-points on the x axis...")
	
	## Set the range of the y axis
	plt.setYaxis (args.yaxis[0], args.yaxis[1])
	
	if args.orbitals:
		printBandCharacter (plt,bands)
	else:
		## Set the colors for the plots
		plt.setProjectedColors (prj.projectedColors)
		printBandProjected(plt,bands,p)


if __name__ == "__main__":
	main ()
