import re
import numpy as np

class Atom (object):
	'''
	Class to describe an atom interfaced with POSCAR files. Works like a struct do group certain qualities from the atomic representation.
	'''
	
	def __init__ (self, element, position, dynamicsOptions):
		self.element = element	
		'''
		The chemical element being represented
		'''
			
		self.position = position
		'''
		Position of the atom
		'''
		
		self.dynamicsOptions = dynamicsOptions
		'''
		Selective dynamics options
		'''

	
	
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
		'''
		Comment for the POSCAR file
		'''
		
		self.dynamics = self.getSelectiveDynamics (filename)
		'''
		Verify if the selective dynamics options is set
		'''
		
		self.lattice = self.getLattice (filename)
		'''
		Lattice vectors of the unit cell
		'''
		
		self.atomSymbols = self.getAtomSymbols (filename)
		'''
		Chemical elements used in the unit cell
		'''
		
		self.atomNumbers = self.getAtomNumbers (filename)
		'''
		Number of atoms of each material being used to represent the unit cell
		'''
		
		## self.allAtoms is a list of atomic symbols
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
				## The comment is always the first line
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
				
				## Go to the 8th (index 7) line and check if there is a 'selective dynamics' option
				for i,line in enumerate(f):
					if i == 7:
						dynamics = re.split(' +', line.strip())[0].lower()
						if dynamics == 'selective':
							## There is, indeed, a 'selective dynamics' option
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
				## lattice is a vector of vectors, namely a matrix containing the lattice vectors
				lattice = []
				
				for i,line in enumerate(f):
					## Go to the second line (index 1) to get the multiplier
					if i == 1:
						multiplier = float (line.strip()[0])
					## Get the lattice vectors
					elif i >= 2 and i <= 4:
						## Separates the vector coordinates using multiple spaces as divider.
						## Then, multiplies it by the multiplier and transform it into a vector
						v = [multiplier*float(x) for x in re.split(' +', line.strip()) if x]
						
						## Includes the new vector into the lattice
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
					## The atomic symbols are located on the 6th line of the POSCAR file,
					## and are separated by spaces
					if i == 5:
						lineSymbols = re.split(' +', line.strip())
						return lineSymbols							
				
		except FileNotFoundError:
			print ("Please specify a valid filename!")
			return FileNotFoundError
	
	def getAtomNumbers (self, filename):
		'''
		Get the number of atoms of each element from the POSCAR file
		'''
		
		try:
			with open (filename,'r') as f:
				for i,line in enumerate(f):
					## The 7th line contains the number of atoms of each element
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
				
				## It is important to check whether the selective dynamics are on or off
				## to make sure we select the correct line
				if self.dynamics:
					addLine = 1
				else:
					addLine = 0
				
				## Get the coordinates system (direct or cartesian) from the POSCAR file
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
		
		After all definitions are set within the POSCAR class, we import all properties of all atoms. Each atom is described using a well-defined coordinate system, a symbol and its selective dynamics options.
		'''
		
		try:
			atoms = []
			with open (filename,'r') as f:
				## To ensure we get the correct lines
				if self.dynamics:
					addLine = 1
				else:
					addLine = 0
					
				for i,line in enumerate(f):
					if i >= (8 + addLine) and i < (8 + addLine + sum (self.atomNumbers)):
						## l represents the line containing the information of the atom
						l = re.split(' +', line.strip())
						
						## pos is the position of the atom in the specified coordinates
						pos = np.array([float(l[0]), float(l[1]), float(l[2])])
						
						## If is there selective dynamics, import it.										
						if self.dynamics:
							dyn = [l[3], l[4], l[5]]
						else:
							dyn = ['F','F','F']											
						
						## The index of this atom can be related to the number of the line (i)
						thisAtomIndex = i - (9 + addLine)
						
						## Creates an atom using the Atom class and the information collected
						thisAtom = Atom (self.allAtoms[thisAtomIndex], pos, dyn)
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
		C = (A)*D
		
		Our matrix self.lattice, however, represents the transpose of the A matrix, since it is written this way on the POSCAR file
		'''
		
		if self.coordinates == 'direct':
			for eachAtom in self.basis:
				eachAtom.position = np.dot(self.lattice.transpose(), eachAtom.position)
			self.coordinates = 'cartesian'	
				
		return
	
	def cart2dir (self):
		'''
		Convert direct to cartesian coordinates
		
		Demonstration of the formula (see function dir2cart):
		
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
			## Write comment
			fOut.write ("%s\n" % (self.comment))
			
			## Multiplier
			fOut.write ("1.00\n")
			
			## justSpace allows us to format the POSCAR file beautifully, with blank spaces
			justSpace = 10
			
			## Lattice vectors
			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[0][0])
			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[0][1])
			fOut.write ("% 4.8f\n".rjust(justSpace) % self.lattice[0][2])

			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[1][0])
			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[1][1])
			fOut.write ("% 4.8f\n".rjust(justSpace) % self.lattice[1][2])
			
			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[2][0])
			fOut.write ("% 4.8f ".rjust(justSpace) % self.lattice[2][1])
			fOut.write ("% 4.8f\n".rjust(justSpace) % self.lattice[2][2])
			
			## Atom symbols
			for eachAtom in self.atomSymbols:
				fOut.write ("%s " % eachAtom)
			fOut.write ("\n")
			
			## Atom numbers
			for eachAtom in self.atomNumbers:
				fOut.write ("%s " % eachAtom)
			fOut.write ("\n")
			
			fOut.write ("Selective Dynamics\n")
			fOut.write ("%s\n" % self.coordinates)
			
			#print ([x.position for x in self.basis])
			
			## Prints all atoms and their positions
			for eachAtom in self.basis:
				fOut.write ("% 1.8f % 1.8f % 1.8f " % (eachAtom.position[0], eachAtom.position[1], eachAtom.position[2]))
				fOut.write ("%s %s %s\n" % (eachAtom.dynamicsOptions[0], eachAtom.dynamicsOptions[1], eachAtom.dynamicsOptions[2]))
