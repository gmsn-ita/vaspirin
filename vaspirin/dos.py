class DOS (object):

	'''
	Atributes:
		NEDOS: list of all k-points from the current run
		eFermi: Fermi energy
		energies= energy values where the DOS are calculated
		states=	calculated density of states
		projDOS= information of DOS projected by atomic orbitals

	'''

	def __init__(self,fDoscar):
		self.NEDOS=self.readNEDOS(fDoscar)
		self.eFermi=self.readEFermi(fDoscar)
		self.energies=self.readEnergies(fDoscar)
		self.states=self.readStates(fDoscar)
		self.projDOS=self.readProjDOS(fDoscar)	
		self.reference = 0

	'''
	Set a new reference for the eigenvalues
	'''
	def setReference (self, newRef):
		self.reference = newRef
			
#	NEDOS: list of all k-points from the current run
	def readNEDOS(self,fDoscar):
		fileIn=open(fDoscar,'r')
		nedos=int(fileIn.read().split('\n')[5].split()[2])
		fileIn.close()		
		return nedos
#	eFermi: Fermi energy
	def readEFermi(self,fDoscar):
		fileIn=open(fDoscar,'r')
		ef=int(float(fileIn.read().split('\n')[5].split()[3]))
		fileIn.close()		
		return ef
#	energies= energy values where the DOS are calculated
	def readEnergies(self,fDoscar):
		fileIn=open(fDoscar,'r')
		doscar=fileIn.read()
		energies=[]
		
		lines=doscar.split('\n')
		for k in range(6,5+self.NEDOS):
			energies.append( float(lines[k].split()[0]) )
		fileIn.close()

		return energies

#	states=	calculated density of states
	def readStates(self,fDoscar):
		fileIn=open(fDoscar,'r')
		doscar=fileIn.read()
		states=[]
		
		lines=doscar.split('\n')
		for k in range(6,5+self.NEDOS):
			states.append( float(lines[k].split()[1]) )
		fileIn.close()
		return states

#	projDOS= information of DOS projected by atomic orbitals
	def readProjDOS(self,fDoscar):
		return 0
