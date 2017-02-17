import numpy as np
import sys

class BandStructure (object):
	
	def __init__(self,fOutcar = "OUTCAR", nKPTignore = 0):
		"""
		Import all properties related to band structures
		"""
		
		self.nKPTignore = nKPTignore
		"""
		The number of k-points to ignore when reading the band structure
		"""
		
		self.soc = False
		"""
		Flag to interpret a spin-orbit coupled calculation
		"""
		
		self.path = self.readPath (fOutcar)
		"""
		Reads the k-point path used in the calculation
		"""
		
		self.nBands = self.readNbands (fOutcar)
		"""
		Reads the number of bands used in the calculation
		"""
		
		self.recLattice = self.readRecLattice (fOutcar)
		"""
		Imports the reciprocal lattice used in the calculation
		"""
		
		self.eigenvals = self.readEigenvals (fOutcar)
		"""
		Imports the eigenvalues obtained from the calculation
		"""
		
		self.eFermi = self.readEFermi (fOutcar)
		"""
		Reads the Fermi energy
		"""
		
		self.nElec = self.readNElec (fOutcar)
		"""
		Imports the number of electrons in the system
		"""
		
		self.eValence = self.readEValence()
		"""
		Determines the energy of the top of the valence band
		"""
		
		self.xAxis = self.createXaxis ()
		"""
		Normalized axis created using the k-point path
		"""
		
		self.reference = self.eValence
		"""
		Reference for the 0 eV
		"""
	
	def setSOC (self, soc):
		'''
		Set whether spin-orbit coupling is on or not
		'''
		
		if soc:
			self.soc = True
		else:
			self.soc = False
	
	def setReference (self, newRef):
		'''
		Set a new reference for the eigenvalues
		'''
		
		self.reference = newRef

	def setReferenceString (self, stringRef):
		"""
		Set a new reference for the eigenvalues using a string as argument
		"""
		
		referenceDict = {
			'vbm' : self.eValence,
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
			self.setReference (referenceDict.get(stringRef.lower(), self.eValence))
		
		
	def readNElec(self,fOutcar):
		"""
		Reads the total number of electrons in the unit cell of the system
		"""

		## Opens the OUTCAR file and extracts the relevant information from it
		try:
			with open(fOutcar,'r') as fileIn:
				outcar = fileIn.read()
				
				## Extracts the relevant information from the OUTCAR file
				nElec = int(float(outcar.split('NELECT =')[1].split('total number of electrons')[0]))
			
			return  nElec 
				
		except FileNotFoundError:
			print ("OUTCAR file not found! Exiting...\n")
			sys.exit (1)		
		
			
	def gap(self):
		"""
		Returns the fundamental gap of the system
		"""
		
		## Checks whether the SOC is turned on
		if self.soc:
			nval = int(self.nElec)
		else:
			nval = int(self.nElec/2)
		
		## Imports the valence and conduction bands from the eigenvalues
		v_band=[]
		c_band=[]	
		for k in range(len(self.path)):
			v_band.append(self.eigenvals[k][nval-1])
			c_band.append(self.eigenvals[k][nval])

		## Calculates the gap
		gap = min(c_band) - max(v_band)

		return gap


	def readEValence(self):
		"""
		Returns the energy of the valence band maximum
		"""
		
		## Checks whether the SOC is turned on
		if self.soc:
			nval=int(self.nElec)
		else:
			nval=int(self.nElec/2)
		
		## Imports the valence band from the eigenvalues
		v_band=[]	
		for k in range(len(self.path)):
			v_band.append(self.eigenvals[k][nval-1])
			
		return max(v_band)


	def dGap(self):
		"""
		Returns the direct gap of the system
		"""
		## Checks whether the SOC is turned on
		if self.soc:
			nval=int(self.nElec)
		else:
			nval=int(self.nElec/2)
		
		## Calculate all direct gaps of the system	
		allGaps=[]
		for k in range(len(self.path)):
			allGaps.append(self.eigenvals[k][nval] - self.eigenvals[k][nval-1])

		## Chooses the direct gap, which is the minimum one
		gap = min (allGaps)

		return gap


	def createXaxis(self):
		"""
		Creates the normalized x-axis by using the distance of the path in the 1BZ.
		
		Variable description: xAxis[k] = (distance between k and the k-point 0)/(1BZ path length)
		"""
		
		x = [0]
		aux = 0
		
		for k in range(1, len(self.path)):
			## aux determines the distance we came through until the k-point k
			aux = aux + distance (self.recLattice, self.path[k], self.path[k-1])
			
			## Saves the correspondence between k and the distance aux
			x.append(aux)
		
		## Normalizing the x axis	
		norm = max(x)
		for k in range(len(x)):
			x[k] = x[k]/norm
		
		return x



	def readEFermi(self,fOutcar):
		"""
		Reads the Fermi level from the calculation
		"""
		try:
			with open(fOutcar,'r') as fileIn:
				## Reads the OUTCAR file
				outcar = fileIn.read()
				
				## Extracts the Fermi level
				ef = float(outcar.split('E-fermi :')[1].split('XC(G=0):')[0])
			
			return  ef 	
				
		except FileNotFoundError:
			print ("OUTCAR file not found! Exiting...\n")
			sys.exit (1)
		

	def readPath(self,fOutcar):
		"""
		Reads the k-points used in the calculation
		
		kpoints = [k-point 1, k-point 2, ...]
		"""
		
		kpoints = []
		
		try:
			with open(fOutcar,'r') as fileIn:
				## Reads the OUTCAR file
				outcar = fileIn.read()
				
				## Selects the text block regarding the k-points info
				text = outcar.split('k-points in reciprocal lattice and weights:')[1].split('position of ions in fractional coordinates')[0] 
				
				## Splits the text block
				lines = text.split('\n')
				
				## Reads all k-points used, putting aside the k-points to be ignored
				for k in range(self.nKPTignore + 1, len(lines)):
					data = lines[k].split()
					
					## Receives the k-points to be calculated
					if len(data) == 4:
						kpoints.append([float(data[0]),float(data[1]),float(data[2])])
				
		except FileNotFoundError:
			print ("OUTCAR file not found! Exiting...\n")
			sys.exit (1)
		
		return  kpoints 
			
		
	def readRecLattice(self,fOutcar):
		"""
		Reads the reciprocal lattice of the cell used in the calculation.
		
		Variables description:
		recLattice = [b1,b2,b3]
		b1 = [b1_x, b1_y, b1_z]
		"""
		
		
		try:
			with open(fOutcar,'r') as fileIn:
				## Reads the OUTCAR file
				outcar = fileIn.read()

				## Extracts the important information
				lines = outcar.split('reciprocal lattice vectors')[1].split('length of vectors')[0].split('\n')
				b1 = [0,0,0]
				b2 = [0,0,0]
				b3 = [0,0,0]
				
				b1[0] = float(lines[1].split()[3])
				b1[1] = float(lines[1].split()[4])	
				b1[2] = float(lines[1].split()[5])	

				b2[0] = float(lines[2].split()[3])
				b2[1] = float(lines[2].split()[4])	
				b2[2] = float(lines[2].split()[5])

				b3[0] = float(lines[3].split()[3])
				b3[1] = float(lines[3].split()[4])	
				b3[2] = float(lines[3].split()[5])
				
		except FileNotFoundError:
			print ("OUTCAR file not found! Exiting...\n")
			sys.exit (1)
			
		return  [b1,b2,b3] 
		

	def readEigenvals(self, fOutcar):
		"""
		Reads the eigenvalues obtained from the calculation.
		
		Variable description: eigenvals[k-point][band]
		"""
		
		try:
			with open(fOutcar,'r') as fileIn:
				
				## Reads the OUTCAR file
				outcar = fileIn.read()

				eigenvals = []
				
				## Extracts the block of relevant information for this analysis
				txtBlock = outcar.split('E-fermi :')[-1].split('---------------------------')[0]
				
				## Separates the block of all eigenvalues into blocks of k-points
				kpoints = txtBlock.split('band No.  band energies     occupation')
				
				## Obtaining the eigenvalues from OUTCAR, putting k-points to be ignored aside
				startingKPT = self.nKPTignore + 1				
				for k in range(startingKPT, len(kpoints)):
					
					## Adds a k-point to be appended
					eigenvals.append([])
					
					## Splits the blocks of k-points into blocks of lines (= bands)
					lines = kpoints[k].split('\n')
					
					## Saves each eigenvalue in its respective band
					for eachLine in lines:
						data = eachLine.split()
						if len(data) == 3:
							eigenvals[k - startingKPT].append (float (data[1]))		

		except FileNotFoundError:
			print ("OUTCAR file not found! Exiting...\n")
			sys.exit (1)
		
		return  eigenvals
			
		

	def readNbands(self,fOutcar):
		"""
		Reads the total number of bands in the calculation
		"""
		try:
			with open(fOutcar,'r') as fileIn:
				outcar = fileIn.read()
				nbands = int (float (outcar.split('NBANDS=')[1].split('number of dos')[0]))
				
		except FileNotFoundError:
			print ("OUTCAR file not found! Exiting...\n")
			sys.exit (1)
			
		return  nbands 


#########################
## AUXILIARY FUNCTIONS ##		
#########################

def distance (basis, p1, p2):
	'''
	Auxiliary function to calculate the cartesian distance between two given points
	p1 and p2, represented in a given basis.
	'''
	
	d = np.linalg.norm (np.dot(np.array(p1)-np.array(p2), np.array(basis)))
	return d
