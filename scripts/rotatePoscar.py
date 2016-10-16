#/usr/bin/env python
# coding: utf-8

'''
Rotate a molecule in a POSCAR file by angleDegrees
The refAtom is taken as reference to the rotation
'''

import sys
import numpy as np
import argparse
import math
import re
import copy

class Atom (object):
	'''
	Class to describe an atom interfaced with POSCAR files
	'''
	
	def __init__ (self, element, position, dynamicsOptions):
		self.element = element		
		self.position = position
		self.dynamicsOptions = dynamicsOptions

	
	
class POSCAR (object):
	'''
	Class to import and describe POSCAR files. Contains the following information:
	 
	 - unit cell dimensions
	 - basis constituents and their positions
	 - selective dynamics for each atom
	 
	Each atom is represented by its class.
	'''
	
	def __init__ (self, filename):
		'''
		Get the lattice vectors (self.lattice), the atomic basis (self.basis),
		the atom summary (which atoms are represented and how many of each one are there, self.atomSummary)
		and the coordinates of the system (cartesian or direct). The comment is also included.
		'''
	
		self.comment = self.getComment (filename)
		self.dynamics = self.getSelectiveDynamics (filename)
		self.lattice = self.getLattice (filename)
		self.atomSymbols = self.getAtomSymbols (filename)
		self.atomNumbers = self.getAtomNumbers (filename)
		
		self.allAtoms = []
		for i in range (len(self.atomNumbers)):
			self.allAtoms += [self.atomSymbols[i]]*self.atomNumbers[i]
		
		self.coordinates = self.getCoordinates (filename)
		self.basis = self.getBasis (filename)			
		
	def getComment (self, filename):
		'''
		Get the comment from the POSCAR file
		'''
		
		try:
			with open (filename,'r') as f:
				return f.readline().strip()
				
		except FileNotFoundError:
			print ("Please specify a valid filename!")
			return FileNotFoundError
	
	def getSelectiveDynamics (self, filename):
		'''
		Verify whether the Selective Dynamics option is set
		'''
		
		try:
			with open (filename,'r') as f:
				dynBoolean = False
				
				for i,line in enumerate(f):
					if i == 7:
						dynamics = re.split(' +', line.strip())[0].lower()
						if dynamics == 'selective':
							dynBoolean = True
							
					elif i > 7:
						break
					
				return dynBoolean
				
		except FileNotFoundError:
			print ("Please specify a valid filename!")
			return FileNotFoundError
			
			
	def getLattice (self, filename):
		'''
		Get the lattice vectors from the POSCAR file
		'''
		
		try:
			with open (filename,'r') as f:
				lattice = []
				
				for i,line in enumerate(f):
					if i == 1:
						multiplier = float (line.strip())
					elif i >= 2 and i <= 4:
						v = [multiplier*float(x) for x in re.split(' +', line.strip())]
						lattice.append (np.array(v))
					elif i > 4:
						break
					
				return np.asarray(lattice)
				
		except FileNotFoundError:
			print ("Please specify a valid filename!")
			return FileNotFoundError
	
	def getAtomSymbols (self, filename):
		'''
		Get the atomic symbols from the POSCAR file
		'''
		
		try:
			with open (filename,'r') as f:
				for i,line in enumerate(f):
					if i == 5:
						lineSymbols = re.split(' +', line.strip())
						return lineSymbols							
				
		except FileNotFoundError:
			print ("Please specify a valid filename!")
			return FileNotFoundError
	
	def getAtomNumbers (self, filename):
		'''
		Get the atomic numbers from the POSCAR file
		'''
		
		try:
			with open (filename,'r') as f:
				for i,line in enumerate(f):
					if i == 6:
						lineNumbers = re.split(' +', line.strip())
						return [int(x) for x in lineNumbers]
				
		except FileNotFoundError:
			print ("Please specify a valid filename!")
			return FileNotFoundError
			
			
	def getCoordinates (self, filename):
		'''
		Get the coordinates (direct or cartesian) from the POSCAR file
		'''
		
		try:
			with open (filename,'r') as f:
				
				if self.dynamics:
					addLine = 1
				else:
					addLine = 0
					
				for i,line in enumerate(f):
					if i == (7 + addLine):
						coordinates = re.split(' +', line.strip())[0].lower()
					elif i > (7 + addLine):
						break
				
				return coordinates
				
		except FileNotFoundError:
			print ("Please specify a valid filename!")
			return FileNotFoundError
	
	def getBasis (self, filename):
		'''
		Get the basis from the POSCAR file
		'''
		
		try:
			atoms = []
			with open (filename,'r') as f:
				if self.dynamics:
					addLine = 1
				else:
					addLine = 0
					
				for i,line in enumerate(f):
					if i >= (8 + addLine) and i <= (8 + addLine + sum (self.atomNumbers)):
						l = re.split(' +', line.strip())
						pos = np.array([float(l[0]), float(l[1]), float(l[2])])
										
						if self.dynamics:
							dyn = [l[3], l[4], l[5]]
						else:
							dyn = ['F','F','F']											
						
						thisAtom = Atom (self.allAtoms[i - (9 + addLine)], pos, dyn)
						atoms.append (thisAtom)
						
					elif i > (8 + addLine + sum (self.atomNumbers)):
						break
			
			return atoms
				
		except FileNotFoundError:
			print ("Please specify a valid filename!")
			return FileNotFoundError
	
	def dir2cart (self):
		'''
		Convert direct to cartesian coordinates
		
		Demonstration of the formula:
		
		c1_vec = d_11 * a1_vec + d_12 * a2_vec + d_13 * a3_vec
		c2_vec = d_21 * a1_vec + d_22 * a2_vec + d_23 * a3_vec
		c3_vec = d_31 * a1_vec + d_32 * a2_vec + d_33 * a3_vec
		
		[c1_vec c2_vec c3_vec] = [a1_vec a2_vec a3_vec] * [d1_vec d2_vec d3_vec]
		C = A*D
		'''
		
		if self.coordinates == 'direct':
			for eachAtom in self.basis:
				eachAtom.position = np.dot(self.lattice.transpose(), eachAtom.position)
			self.coordinates = 'cartesian'	
				
		return
	
	def cart2dir (self):
		'''
		Convert direct to cartesian coordinates
		
		Demonstration of the formula:
		
		D = inv(A)*C
		'''
		
		if self.coordinates == 'cartesian':
			for eachAtom in self.basis:
				eachAtom.position = np.dot(np.linalg.inv(self.lattice.transpose()), eachAtom.position)
			self.coordinates = 'direct'
			
		return
	
	def writePoscar (self, outputFilename):
		'''
		Writes the POSCAR class to outputFilename.
		Selective Dynamics is always written, and the coordinates are preserved.
		'''
		
		with open (outputFilename,'w') as fOut:
			fOut.write ("%s\n" % (self.comment))
			fOut.write ("1.00\n")
			
			justSpace = 10
			
			
			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[0][0])
			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[0][1])
			fOut.write ("% 4.8f\n".rjust(justSpace) % self.lattice[0][2])

			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[1][0])
			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[1][1])
			fOut.write ("% 4.8f\n".rjust(justSpace) % self.lattice[1][2])
			
			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[2][0])
			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[2][1])
			fOut.write ("% 4.8f\n".rjust(justSpace) % self.lattice[2][2])
			
			for eachAtom in self.atomSymbols:
				fOut.write ("%s " % eachAtom)
			fOut.write ("\n")
			
			for eachAtom in self.atomNumbers:
				fOut.write ("%s " % eachAtom)
			fOut.write ("\n")
			
			fOut.write ("Selective Dynamics\n")
			fOut.write ("%s\n" % self.coordinates)
			
			#print ([x.position for x in self.basis])
			
			for eachAtom in self.basis:
				fOut.write ("% 1.8f % 1.8f % 1.8f " % (eachAtom.position[0], eachAtom.position[1], eachAtom.position[2]))
				fOut.write ("%s %s %s\n" % (eachAtom.dynamicsOptions[0], eachAtom.dynamicsOptions[1], eachAtom.dynamicsOptions[2]))
				
	
def parseArgs():
	"""
	Parse arguments from the command line. Uses the `argparse` package to
	establish all positional and optional arguments.
	"""
	parser = argparse.ArgumentParser(description='Rotate molecules within POSCAR files.',
									epilog= "Written by Daniel S. Koda (oct. 2016).")

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
	args = parseArgs()
	
	if not args.quiet:
		print ("***********************")
		print ("   rotatePoscar v1.0   ")
		print ("***********************")
		
		printRunDescription (args)
	
	anglesCreated = np.linspace(args.angles[0], args.angles[1], np.ceil((args.angles[1] - args.angles[0])/args.angles_step) + 1)
	
	poscar = POSCAR (args.input_file)
	
	for angle in anglesCreated:
		rotateAngle (args, copy.deepcopy(poscar), angle)

		
		
if __name__ == "__main__":
	main ()

