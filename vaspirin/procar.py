import sys, os, shutil
from . import projection

class PROCAR (object):
	'''
	Deals with PROCAR-related information, such as band composition, projection
	onto orbitals and atomic sites. The PROCAR file should be passed as input to this class.
	The PROCAR class cannot deals with very large (~ GB) PROCAR files, since a memory error
	happens in this case. To solve this problem, another class named PROCAR_splitter has been created to directly create the .dat file from a large PROCAR file.
	'''

	def __init__ (self, fProcar, projection, nKPTignore = 0):
		self.nKPTignore = nKPTignore
		"""
		Number of k-points to be ignored
		"""
		
		self.nKpoints,self.nBands,self.nIons = self.readHeader (fProcar)
		"""
		Number of k-points, bands and ions in the system
		"""

		self.orbitalContributions = self.readOrbitalContribution (fProcar)
		"""
		Reads the composition of the bands, for each k-point, projected onto atomic orbitals
		"""
		
		self.ionContributions = self.readIonContribution (fProcar)
		"""
		Reads the composition of the bands, for each k-point, projected onto atomic sites
		"""
		
		self.prj = projection
		"""
		PROJECTION information
		"""
		
		self.materialContributions = []
		"""
		For projecting bands onto groups of atomic sites (materials)
		"""
		
		self.sumContributions()
		
	
	def readHeader (self,fProcar):
		'''
		Reads the number of k-points, bands and ions in the simulation from
		the header of the PROCAR file. Uses only the first two lines.
		'''
		try:
			with open(fProcar,'r') as f:
				# 1st line: comment
				f.readline()
				
				# 2nd line: important information!
				header = f.readline().strip() 
				
		except FileNotFoundError:
			print ("PROCAR file not found! Exiting...\n")
			sys.exit (1)
			
		# header read!
		nkpt = int(header.split(':')[1].split()[0])
		nbands = int(header.split(':')[2].split()[0])
		nions = int(header.split(':')[3].split()[0])

		return nkpt,nbands,nions
		

	def readOrbitalContribution (self,fProcar):
		"""
		Creates a matrix containing the contribution of each orbital.
		"""
		
		try:
			with open(fProcar,'r') as fileIn:
				procar = fileIn.read()
		except FileNotFoundError:
			print ("PROCAR file not found! Exiting...\n")
			sys.exit (1)
			
			
		## contributions[kpoint][band] returns the list [s,px+py,pz,d]
		contributions = []
		
		kptBlock = procar.split('k-point')
		
		## The first two blocks are the header, thus should be ignored
		## Loops over each k-point
		for k in range (2 + self.nKPTignore,len(kptBlock)):
			contributions.append([])
			
			## Splits the k-point block into bands
			bands = kptBlock[k].split('band')
			
			## Loops over each band, ignoring the first block (the header)
			for j in range (1,self.nBands+1):
				contributions[k - (self.nKPTignore + 2)].append([])
				lines = bands[j].split('\n')
				
				## The line 3+self.nIons represents the total contribution in terms of
				## atomic orbitals. It is about the last line in the block being manipulated
				totCont = float(lines[3+self.nIons].split()[10])
				
				if totCont > 0:
					sCont = float(lines[3+self.nIons].split()[1])/totCont
					pyCont = float(lines[3+self.nIons].split()[2])/totCont
					pzCont = float(lines[3+self.nIons].split()[3])/totCont
					pxCont = float(lines[3+self.nIons].split()[4])/totCont
					dxyCont = float(lines[3+self.nIons].split()[5])/totCont
					dyzCont = float(lines[3+self.nIons].split()[6])/totCont
					dz2Cont = float(lines[3+self.nIons].split()[7])/totCont
					dxzCont = float(lines[3+self.nIons].split()[8])/totCont
					dx2Cont = float(lines[3+self.nIons].split()[9])/totCont
					contributions[k-self.nKPTignore-2][j-1].extend([sCont, pyCont + pxCont, pzCont, dxyCont + dyzCont + dz2Cont + dxzCont + dx2Cont])
				else:
					contributions[k-self.nKPTignore-2][j-1].extend([0,0,0,0])       
		
		return contributions
			

	def readIonContribution (self,fProcar):
		"""
		Reads the relative contribution of all ions to the formation of the band, for each k-point.
		Allows to study the character of the band.
		"""
		
		try:
			with open(fProcar,'r') as fileIn:
				procar = fileIn.read()
		except FileNotFoundError:
			print ("PROCAR file not found! Exiting...\n")
			sys.exit (1)
					
		## contributions[k-point][band][ion]
		contributions = []
		
		kptBlock = procar.split('k-point')
		
		## Loops over each k-point, ignoring the header and the first k-points (if applicable)
		for k in range (2 + self.nKPTignore,len(kptBlock)):
			
			contributions.append([])
			bands = kptBlock[k].split('band')
			
			## Now loops over each band
			for j in range (1,self.nBands+1):
				contributions[k-self.nKPTignore-2].append([])
				lines = bands[j].split('\n')
				
				## Total contribution for the specified k-point and band
				totCont = float(lines[3+self.nIons].split()[10])
				
				if totCont > 0:
					ionsContributionsThisBand = []
					
					## Loops over all ions to get their contribution to the band
					for i in range(self.nIons):
						## The first ion is seen in lines[3] and the block index 10 (11th column) is the ionic contribution to the system
						thisIonContribution = float(lines[3+i].split()[10])/totCont
						ionsContributionsThisBand.append(thisIonContribution)
					
					## Saves the information and goes on to a new band
					contributions[k-self.nKPTignore-2][j-1].extend(ionsContributionsThisBand)
				else:
					contributions[k-self.nKPTignore-2][j-1].extend([0]*self.nIons)      
		
		return contributions
			
		
	def sumContributions (self):
		"""
		Sum the contributions from the ions into N materials based on the list ionsVsMaterials.
		The list ionsVsMaterials simply labels the ions to be summed.
		"""

		## Variable to store the contributions of the N materials
		## projectedContribution [k-point][band][material in index form]
		projectedContributions = []
		
		## Loops over each k-point not ignored
		for kpt in range(self.nKpoints - self.nKPTignore):
			projectedContributions.append ([])
			
			for band in range (self.nBands):
				projectedContributions[kpt].append ([])
				projectedContributions[kpt][band].extend ([0]*len(self.prj.dictMaterials))
				
				for eachIon in range(self.nIons):		
					## Variable which groups ions pertaining to the same material
					ionLabel = self.prj.dictMaterials.get(self.prj.ionsVsMaterials[eachIon])
					
					## Sums contribution of ions labeled together
					projectedContributions[kpt][band][ionLabel] += self.ionContributions[kpt][band][eachIon]
		
		self.materialContributions = projectedContributions
		return
