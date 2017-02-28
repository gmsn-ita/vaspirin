import copy

class AtomicDOS (object):
	"""
	Density of states projected onto an atom.
	Contains a list of lists (matrix-like) of the following format:
		[energy1, energy2, ...]
	
	Each `energy` list is a list itself, which contains the energy of the line and the
	density of states projected onto each orbital:
		[energy, s, py, pz, px, dxy, dyz, dz2, dxz, dx2]
	"""
	
	def __init__(self, nEDOS):
		"""
		Configures each atom within the DOS calculation
		"""
		
		self.nEDOS = nEDOS
		"""
		The number of points (energies sampled) for this DOS calculation
		"""
		
		self.dos = []
		"""
		List of lists of the kind:
			[energy, s, py, pz, px, dxy, dyz, dz2, dxz, dx2]
		"""
		
		self.totalDOS = []
		"""
		List of lists of the kind:
			[energy, s + py + pz + px + dxy + dyz + dz2 + dxz + dx2]
		"""
	
	def sumTotalDOS (self):
		"""
		Sums the total DOS from self.dos list
		"""
		
		self.totalDOS = []
		
		for energy in self.dos:
			self.totalDOS.append([energy[0], sum(energy[-9:])])
		
		return
	
	def sumAtomicDOS (self, AtomicDOS_atom):
		"""
		Sum this atomic DOS with another one energy-wise
		"""
		
		if self.nEDOS != AtomicDOS_atom.nEDOS:
			print ("Summing different atomic DOS! Exiting...")
			return 1
			
		if not self.dos:
			self.dos = AtomicDOS_atom.dos
		else:
			for i in range (len(self.dos)):
				self.dos[i] = [self.dos[i][0]] + [self.dos[i][j] + AtomicDOS_atom.dos[i][j] for j in range(1,len(self.dos[i]))]
		
		return


class DOS (object):
	"""
	Describes a DOSCAR file.
	"""

	def __init__(self,fDoscar="DOSCAR"):
		"""
		Initializes the reading of the DOSCAR file
		"""
		
		self.fDoscar = fDoscar
		"""
		The file being read
		"""
		
		self.nEDOS = self.readNEDOS()
		"""
		The number of energy points used to calculate the DOS
		"""
		
		self.eFermi = self.readEFermi()
		"""
		The Fermi energy calculated within the system
		"""
		
		self.energies = self.readEnergies()
		"""
		The energies used as points for calculation of the DOS
		"""
		
		self.states = self.readStates()
		"""
		The total density of states in the system
		"""
		
		self.atomsDOS = self.readAtomsDOS()
		"""
		List of atoms containing the density of states projected onto atomic orbitals
		"""
		
		self.orbitalDOS = self.sumOrbitalContributions()
		"""
		Returns an AtomicDOS class containing the density of states projected onto atomic orbitals
		"""
		
		self.materialDOS = []
		"""
		For projecting the DOS onto groups of atomic sites (materials)
		"""
		
		self.reference = self.eFermi
		"""
		Reference for the DOS calculation
		"""
		
		
	def setReference (self, newRef):
		"""
		Set a new reference for the eigenvalues
		"""
		self.reference = newRef
	
	def setReferenceString (self, stringRef):
		"""
		Set a new reference for the eigenvalues using a string as argument
		"""
		
		referenceDict = {
			'efermi' : self.eFermi,
			'e-fermi' : self.eFermi,
			'ef' : self.eFermi,
			'0' : 0,
		}
		
		try:
			## If the argument stringRef is simply a number, use it as reference
			ref = float(stringRef)
			self.setReference (ref)
			
		except ValueError:
			## If the argument stringRef is not a number, checks whether this string
			## is compatible with the referenceDict
			self.setReference (referenceDict.get(stringRef.lower(), self.eFermi))		

	def setProjection (self, projection):
		"""
		Set a new projection object
		"""
		self.prj = projection


	def readNEDOS(self):
		"""
		Read the number of energy points used in this calculation
		"""
		with open(self.fDoscar,'r') as fileIn:
			nedos = int (fileIn.read().split('\n')[5].split()[2])
		
		return nedos
		

	def readEFermi(self):
		"""
		Read the Fermi energy from the DOSCAR
		"""
		
		with open(self.fDoscar,'r') as fileIn:
			ef = float (fileIn.read().split('\n')[5].split()[3])

		return ef
		

	def readEnergies(self):
		"""
		Read the energies in which the density of states is calculated within the system
		"""
		with open(self.fDoscar,'r') as fileIn:
			doscar=fileIn.read()
			
		energies=[]
		
		lines=doscar.split('\n')
		
		## Extracts the energies calculated within the system
		for k in range(6,6+self.nEDOS):
			energies.append( float(lines[k].split()[0]) )
		fileIn.close()

		return energies

	def readStates(self):
		"""
		Read the total density of states of the system.
		"""
		
		with open(self.fDoscar,'r') as fileIn:
			doscar=fileIn.read()
			
		states=[]
		
		lines=doscar.split('\n')
		
		## Extracts the total density of states from the system
		for k in range(6,6+self.nEDOS):
			states.append( float(lines[k].split()[1]) )
			
		return states

	def readAtomsDOS(self):
		"""
		Provides information of DOS projected by atomic orbitals. Reads the projected DOS from the DOSCAR file and returns a list of AtomicDOS.
		The list has the format [atom1, atom2, ...].
		"""

		atomsDOS = []
		
		with open (self.fDoscar, 'r') as f:
			## Throw away the first 5 lines
			for i in range(6):
				f.readline()
			
			## Divider between each DOSCAR file
			atomicBlocks = f.read().split(" 1.00000000\n")
			## Throw away the total DOS
			del atomicBlocks[0]
			
			for block in atomicBlocks:
				atom = AtomicDOS (self.nEDOS)
				lines = block.split('\n')
				lines = [x for x in lines if x]
				
				if len(lines) == self.nEDOS + 1:
					del lines[-1]
				
				## Creates a vector of (vectors of floats)
				atom.dos = [ list(map (float, eachLine.split())) for eachLine in lines]
				atom.sumTotalDOS ()
				
				atomsDOS.append(atom)
					
		return atomsDOS

	def sumOrbitalContributions (self):
		"""
		Sum orbital contribuions from atoms
		"""
	
		orbitalDOS = AtomicDOS(self.nEDOS)
		
		## Sums the atomic dos from each atom and compiles it into a single material
		for eachAtom in self.atomsDOS:									
			orbitalDOS.sumAtomicDOS (copy.deepcopy(eachAtom))
		
		orbitalDOS.sumTotalDOS ()
		
		return orbitalDOS
	
	def sumContributions (self):
		"""
		Sum contribuions from atoms belonging to the same material
		"""
		
		self.materialDOS = [AtomicDOS(self.nEDOS) for i in range(len(self.prj.dictMaterials))]
		
		## Sums the atomic dos from each atom and compiles it into a single material
		for ionIndex in range(len(self.atomsDOS)):									
			
			self.materialDOS[self.prj.dictMaterials.get(self.prj.ionsVsMaterials[ionIndex])].sumAtomicDOS (copy.deepcopy(self.atomsDOS[ionIndex]))

		## Finishes compiling the total DOS from each material
		for material in self.materialDOS:
			material.sumTotalDOS ()
		
		return
