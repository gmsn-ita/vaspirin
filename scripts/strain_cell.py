#/usr/bin/env python3

from vaspirin import poscar
import numpy as np
import argparse
import copy
	
def parseArgs():
	"""
	Parse arguments from the command line. Uses the `argparse` package to
	establish all positional and optional arguments.
	"""
	parser = argparse.ArgumentParser(description='Strain unit cells from POSCAR files.',
									epilog= "Written by Daniel S. Koda (jan. 2017).",
									prog="strain_cell.py")

	parser.add_argument('input_file', help="POSCAR input file")
	
	parser.add_argument('-o', '--output', default='POSCAR', help="output name for the generated files. Default: POSCAR_displacement")
	
	parser.add_argument('-s', '--strain', type=float, nargs=2, default=[0.0, 0.0], help="interval of strains (in %%) to generate (default: 0%%)", metavar=('DELTA_MIN', 'DELTA_MAX'))
	
	parser.add_argument('-t', '--step', type=float, default=0.5, help="step (in %%) for the displacement (in Angstrom) while generating POSCARs (default: 0.5%%)")
	
	parser.add_argument('-x', action='store_true', help="strain is applied to the first lattice vector")
	parser.add_argument('-y', action='store_true', help="strain is applied to the second lattice vector")
	parser.add_argument('-z', action='store_true', help="strain is applied to the third lattice vector")
	
	parser.add_argument('-q', '--quiet', action='store_true', help="do not display text on the output window (default: False)")
	
	return parser.parse_args()

def printRunDescription (args):
	'''
	Print description of the options chosen and the crystals input.
	'''
	
	leftJustSpace = 20
	print ("input file:".ljust(leftJustSpace) + "%s" % args.input_file)
	print ("output file:".ljust(leftJustSpace) + "%s" % args.output)
	print ("range of strains:".ljust(leftJustSpace) + "from % 2.1f to % 2.1f %%" % (args.strain[0], args.strain[1]))
	print ("strains step:".ljust(leftJustSpace) + "%1.2f " % args.step)
	print ("vectors to strain:".ljust(leftJustSpace) + ("x " if args.x else "") + ("y " if args.y else "") + ("z " if args.z else ""))
                     
                     
def strainCell (args, poscar, strain):
	'''
	Moves selected atoms in the POSCAR as specified by args. Translation has to be made in
	cartesian coordinates, since the arguments are described in these
	coordinates.
	
	The lattice is described by A = transpose([a_1 a_2 a_3]), in which a_n is the nth lattice vector
	The strain matrix is diagonal and contains the straining factors for each lattice vector
	'''
	
	## All atoms are displaced according to the strain
	if poscar.coordinates == 'cartesian':
		poscar.cart2dir()
	
	## Defining a matrix with strain-related information
	strainMatrix = np.ones((3,3))
	
	## The strain is defined as percentage
	if args.x:
		strainMatrix[:,0] += strain/100.0
	
	if args.y:
		strainMatrix[:,1] += strain/100.0
		
	if args.z:
		strainMatrix[:,2] += strain/100.0
	
	## Straining the lattice
	poscar.lattice = strainMatrix*poscar.lattice
	
	poscar.writePoscar (args.output + "_%2.1f" % strain)
	

def main():
	'''
	Strains the unit cell by the quantities specified in arguments
	'''
	
	args = parseArgs()
	
	if not args.quiet:
		print ("******************************")
		print ("  vaspirin v1.2: strain_cell  ")
		print ("******************************")
		
		printRunDescription (args)
	
	strainCreated = np.linspace(args.strain[0], args.strain[1], np.ceil((args.strain[1] - args.strain[0])/args.step) + 1)
	
	poscar_file = poscar.POSCAR (args.input_file)
	
	for strain in strainCreated:
		## The deepcopy makes sure we don't screw the original POSCAR file in the function
		strainCell (args, copy.deepcopy(poscar_file), strain)
		
if __name__ == "__main__":
	main ()

