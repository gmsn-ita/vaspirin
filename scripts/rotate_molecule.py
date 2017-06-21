#/usr/bin/env python3
# coding: utf-8

from vaspirin import poscar
import numpy as np
import argparse
import math
import copy
	
def parseArgs():
	"""
	Parse arguments from the command line. Uses the `argparse` package to
	establish all positional and optional arguments.
	"""
	parser = argparse.ArgumentParser(description='Rotate molecules within POSCAR files.',
									epilog= "Written by Daniel S. Koda (jan. 2017).",
									prog="rotate_molecule.py")

	parser.add_argument('input_file', help="POSCAR input file")
	
	parser.add_argument('-o', '--output', default='POSCAR', help="output name for the generated files. Default: POSCAR_angle")
	
	parser.add_argument('-a', '--angles', type=float, nargs=2, default=[0.0, 0.0], help="interval of angles (in degrees) to generate (default: only 0 deg)", metavar=('ANGLE_MIN', 'ANGLE_MAX'))
	
	parser.add_argument('-s', '--angles_step', type=float, default=10, help="step for the angles (in degrees) while generating POSCARs (default: 10)")
	
	parser.add_argument('-m', '--molecule', type=int, nargs=2, default=[1, 1], help="index of atoms which define the molecule including the ones specified starting from 1 (default: 1)", metavar=('ATOM_MIN', 'ATOM_MAX'))
	
	parser.add_argument('-r', '--ref', type=int, default=1, help="index of the reference atom to define the origin of the rotation (default: 1)")
	
	parser.add_argument('-x', '--axis', choices=['x','y','z'], default='z', help="reference axis to rotate (default: z)")
	
	parser.add_argument('-q', '--quiet', action='store_true', help="do not display text on the output window (default: False)")
	
	return parser.parse_args()

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
	

def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis by theta radians.
    Taken from http://stackoverflow.com/questions/6802577/python-rotation-of-3d-vector
    """
    axis = np.asarray(axis)
    axis = axis/math.sqrt(np.dot(axis, axis))
    a = math.cos(theta/2.0)
    b, c, d = -axis*math.sin(theta/2.0)
    aa, bb, cc, dd = a*a, b*b, c*c, d*d
    bc, ad, ac, ab, bd, cd = b*c, a*d, a*c, a*b, b*d, c*d
    return np.array([[aa+bb-cc-dd, 2*(bc+ad), 2*(bd-ac)],
                     [2*(bc-ad), aa+cc-bb-dd, 2*(cd+ab)],
                     [2*(bd+ac), 2*(cd-ab), aa+dd-bb-cc]])
                     
                     
def rotateAngle (args, poscar, angle):
	'''
	Rotate the POSCAR as specified by args. Rotation has to be made in
	cartesian coordinates, since the matrix above is described in these
	coordinates. The implemented formula is demonstrated below:
	
	c1_vec = d_11 * a1_vec + d_12 * a2_vec + d_13 * a3_vec
	c2_vec = d_21 * a1_vec + d_22 * a2_vec + d_23 * a3_vec
	c3_vec = d_31 * a1_vec + d_32 * a2_vec + d_33 * a3_vec
	
	[c1_vec c2_vec c3_vec] = [a1_vec a2_vec a3_vec] * [d1_vec d2_vec d3_vec]
	C = A*D,
	
	in which A = POSCAR.lattice.transpose()
	
	Let ~C = M * C. Then,
	
	~D = inv(A) * ~C = inv(A) * M * C = (inv(A) * M * A) * D.
	'''
	
	axisDict = {
	'x' : np.array([1,0,0]),
	'y' : np.array([0,1,0]),
	'z' : np.array([0,0,1])
	}

	axis = axisDict.get (args.axis)
	ref = np.copy(poscar.basis[args.ref-1].position)
	M = rotation_matrix (axis, math.radians(angle))
	
	if poscar.coordinates == 'cartesian':
		rotMatrix = M
	elif poscar.coordinates == 'direct':
		A = poscar.lattice.transpose()
		rotMatrix = np.dot (np.dot (np.linalg.inv(A), M), A)

	# Setting the new reference, rotating and going back to the new reference
	
	#newAtomicPositions = []
	
	for eachAtom in poscar.basis[args.molecule[0]-1:args.molecule[1]]:
		eachAtom.position -= ref
		eachAtom.position = np.dot(rotMatrix, eachAtom.position)
		eachAtom.position +=  ref
		
		#newAtomicPositions.append (eachAtom)
	
	#poscar.basis[args.molecule[0]-1:args.molecule[1]] = newAtomicPositions
	
	poscar.writePoscar (args.output + "_%2.1f" % angle)
	

def main():
	'''
	Rotates a molecule in a POSCAR file by angleDegrees
	The refAtom is taken as reference to the rotation
	'''
	
	args = parseArgs()
	
	if not args.quiet:
		print ("********************************")
		print (" vaspirin v2.0: rotate_molecule ")
		print ("********************************")
		
		printRunDescription (args)
	
	anglesCreated = np.linspace(args.angles[0], args.angles[1], np.ceil((args.angles[1] - args.angles[0])/args.angles_step) + 1)
	
	poscar_file = poscar.POSCAR (args.input_file)
	
	for angle in anglesCreated:
		rotateAngle (args, copy.deepcopy(poscar_file), angle)
		
if __name__ == "__main__":
	main ()

