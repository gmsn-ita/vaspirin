#/usr/bin/env python
# coding: utf-8

from vaspirin import poscar
import numpy as np
import argparse
import copy
	
def parseArgs():
	"""
	Parse arguments from the command line. Uses the `argparse` package to
	establish all positional and optional arguments.
	"""
	parser = argparse.ArgumentParser(description='Move atoms within POSCAR files.',
									epilog= "Written by Daniel S. Koda (jan. 2017).",
									prog="move_atoms.py")

	parser.add_argument('input_file', help="POSCAR input file")
	
	parser.add_argument('-o', '--output', default=None, help="output name for the generated files. Default: input_file_displacement")
	
	parser.add_argument('-d', '--displacement', type=float, nargs=2, default=[0.0, 0.0], help="interval of displacements (in Angstrom) to generate (default: only 0 Angs)", metavar=('DELTA_MIN', 'DELTA_MAX'))
	
	parser.add_argument('-s', '--step', type=float, default=0.2, help="step for the displacement (in Angstrom) while generating POSCARs (default: 0.2)")
	
	parser.add_argument('-m', '--atoms', type=int, nargs=2, default=[1, 1], help="index of atoms which define the system to be moved, starting from 1 (default: 1)", metavar=('ATOM_MIN', 'ATOM_MAX'))
	
	parser.add_argument('-x', '--axis', choices=['x','y','z'], default='z', help="reference axis to move (default: z)")
	
	parser.add_argument('-q', '--quiet', action='store_true', help="do not display text on the output window (default: False)")
	
	return parser.parse_args()

def printRunDescription (args):
	'''
	Print description of the options chosen and the crystals input.
	'''
	
	leftJustSpace = 20
	print ("input file:".ljust(leftJustSpace) + "%s" % args.input_file)
	print ("output file:".ljust(leftJustSpace) + "%s" % args.output)
	print ("atoms to move:".ljust(leftJustSpace) + "from atom %d to %d" % (args.atoms[0], args.atoms[1]))
	print ("displacements:".ljust(leftJustSpace) + "from %.2f to %.2f Angs" % (args.displacement[0], args.displacement[1]))
	print ("displacements_step:".ljust(leftJustSpace) + "%.2f Angs" % args.step)
	print ("axis:".ljust(leftJustSpace) + "%s" % args.axis)
                     
                     
def moveAtoms (args, poscar, delta):
	'''
	Moves selected atoms in the POSCAR as specified by args. Translation has to be made in
	cartesian coordinates, since the arguments are described in these
	coordinates.
	'''
	
	axisDict = {
	'x' : np.array([1,0,0]),
	'y' : np.array([0,1,0]),
	'z' : np.array([0,0,1])
	}

	axis = axisDict.get (args.axis)
	
	if poscar.coordinates == 'direct':
		poscar.dir2cart()

	for eachAtom in poscar.basis[args.atoms[0]-1:args.atoms[1]]:
		eachAtom.position += delta*axis
	
	## The 1e-8 ensures 0.0 is not written as -0.0
	poscar.writePoscar (args.output + "_%2.1f" % (delta + 1e-8))
	

def main():
	'''
	Rotates a molecule in a POSCAR file by angleDegrees
	The refAtom is taken as reference to the rotation
	'''
	
	args = parseArgs()
	
	## Setting the default output to the input filename
	args.output = args.output if args.output else args.input_file	
	
	if not args.quiet:
		print ("***************************")
		print (" vaspirin v2.0: move_atoms ")
		print ("***************************")
		
		printRunDescription (args)
	
	deltasCreated = np.linspace(args.displacement[0], args.displacement[1], np.ceil((args.displacement[1] - args.displacement[0])/args.step) + 1)
	
	poscar_file = poscar.POSCAR (args.input_file)
	
	for delta in deltasCreated:
		moveAtoms (args, copy.deepcopy(poscar_file), delta)
		
if __name__ == "__main__":
	main ()

