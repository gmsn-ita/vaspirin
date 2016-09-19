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
		self.nEDOS = nEDOS
		"""
		The number of points (energies) for this DOS calculation
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
	Atributes:
		NEDOS: list of all k-points from the current run
		eFermi: Fermi energy
		energies= energy values where the DOS are calculated
		states=	calculated density of states
		projDOS= information of DOS projected by atomic orbitals
	"""

	def __init__(self,fDoscar):
		self.fDoscar = fDoscar
		self.nEDOS=self.readNEDOS()
		self.eFermi=self.readEFermi()
		self.energies=self.readEnergies()
		self.states=self.readStates()
		self.projDOS=self.readProjDOS()
		self.ionsVsMaterials = []
		self.materialDOS = []
		self.reference = 0
		
		self.dictMaterials = {}

	def setReference (self, newRef):
		"""
		Set a new reference for the eigenvalues
		"""
		self.reference = newRef
			
#	NEDOS: list of all k-points from the current run
	def readNEDOS(self):
		fileIn=open(self.fDoscar,'r')
		nedos=int(fileIn.read().split('\n')[5].split()[2])
		fileIn.close()		
		return nedos
#	eFermi: Fermi energy
	def readEFermi(self,):
		fileIn=open(self.fDoscar,'r')
		ef=int(float(fileIn.read().split('\n')[5].split()[3]))
		fileIn.close()		
		return ef
#	energies= energy values where the DOS are calculated
	def readEnergies(self):
		fileIn=open(self.fDoscar,'r')
		doscar=fileIn.read()
		energies=[]
		
		lines=doscar.split('\n')
		for k in range(6,5+self.nEDOS):
			energies.append( float(lines[k].split()[0]) )
		fileIn.close()

		return energies

#	states=	calculated density of states
	def readStates(self):
		fileIn=open(self.fDoscar,'r')
		doscar=fileIn.read()
		states=[]
		
		lines=doscar.split('\n')
		for k in range(6,5+self.nEDOS):
			states.append( float(lines[k].split()[1]) )
		fileIn.close()
		return states

#	projDOS= information of DOS projected by atomic orbitals
	def readProjDOS(self):
		"""
		Reads the projected DOS from the DOSCAR file and returns a list of AtomicDOS.
		The list has the format [atom1, atom2, ...].
		"""

		atomsDOS = []
		
		with open (self.fDoscar, 'r') as f:
			atomicBlocks = f.read().split("1.00000000\n")
			del atomicBlocks[0]
			del atomicBlocks[0]
			
			for block in atomicBlocks:
				atom = AtomicDOS (self.nEDOS)
				lines = block.split('\n')
				
				if len(lines) == self.nEDOS + 1:
					del lines[-1]
				
				atom.dos = [ list(map (float, eachLine.split())) for eachLine in lines]
				atom.sumTotalDOS ()
				
				atomsDOS.append(atom)
				
					
		return atomsDOS
	
	def sumContributions (self):
		"""
		Sum contribuions from atoms belonging to the same material
		"""
	
		self.materialDOS = [AtomicDOS(self.nEDOS) for i in range(len(self.dictMaterials))]
		
		for ionIndex in range(len(self.projDOS)):									
			self.materialDOS[self.dictMaterials.get(self.ionsVsMaterials[ionIndex])].sumAtomicDOS (self.projDOS[ionIndex])

		for material in self.materialDOS:
			material.sumTotalDOS ()
			
		return
		
		
	def createIonVsMaterials (self, fileProjection):
		'''
		 The list ionsVsMaterials should indicate the material to which the ion belong, e.g.:
		   i) for two materials based on six atoms: [HfS2, HfS2, HfS2, ZrS2, ZrS2, ZrS2]
		   ii) for three materials based on nine atoms with an odd order: [Mat1, Mat1, Mat3, Mat2, Mat2, Mat2, Mat3, Mat3, Mat1]
		
		 The file PROJECTION (default name) should have the following format:
		 
		 Material1Name ionsBelongingToMat1
		 Material2Name ionsBelongingToMat2
		 Material3Name ionsBelongingToMat3
		 ...
		 
		 For the examples commented above, the file should be:
		   i) PROJECTION
		   
		   HfS2 1,2,3
		   ZrS2 4,5,6
		   
		   i) OR
		   
		   HfS2 1..3
		   ZrS2 4..6
		   
		   ii) PROJECTION
		   Mat1 1,2,9
		   Mat2 4,5,6
		   Mat3 3,7,8
		   
		   ii) OR
		   
		   Mat1 1,2,9
		   Mat2 4..6
		   Mat3 3,7,8
		   
		 The material divider should be the new line feed \n
		 The ion divider should be the comma ,
		 To start listing the ions, use a space
		 The label should not contain spaces
		''' 
		try:
			fileIn=open(fileProjection,'r')
		except FileNotFoundError:
			print ('Projection file not found. Please specify a valid filename.')
			sys.exit()
			
		ionsData = fileIn.read()
		
		matString = ionsData.split('\n')
		matString = [i for i in matString if i]  # removes repeated \n
		
		index = 0
		self.ionsVsMaterials = []
		
		for eachMaterial in matString:
			self.dictMaterials.update ({eachMaterial.split(' ')[0] : index})
			index += 1
			
			belongingIons = eachMaterial.split(' ')[1].split(',')
			
			
			for eachIon in belongingIons:
				if eachIon.find('..') == -1:
					self.ionsVsMaterials.append(eachMaterial.split(' ')[0])
				else:
					ionsInterval = eachIon.split('..')
					nIonsInterval = int(ionsInterval[1]) - int(ionsInterval[0]) + 1
					self.ionsVsMaterials.extend ([eachMaterial.split(' ')[0]]*nIonsInterval)
			
		if len(self.ionsVsMaterials) != len(self.projDOS):
			print ("Error in the argument of the projection on ions: not all ions are specified!")
			sys.exit(1)
		
		self.sumContributions()
		
		return
