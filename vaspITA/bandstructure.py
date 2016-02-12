import numpy as np

class BandStructure (object):
	'''
	Atributes:
		path: list of all k-points from the current run
		eigenvals: matrix eigenvalues[k-point - 1][band]
		nBands: total number of bands simulated
		eFermi: Fermi energy
		nElec: total number of electrons in the cell
		recLattice: list of the reciprocal lattice vectors
	'''
	
	# Import all properties related to band structures
	def __init__(self,fOutcar):
		self.path = self.readPath(fOutcar)
		self.nBands = self.readNbands(fOutcar)
		self.recLattice = self.readRecLattice(fOutcar)
		self.eigenvals = self.readEigenvals(fOutcar)
		self.eFermi = self.readEFermi(fOutcar)
		self.nElec = self.readNElec(fOutcar)
		self.eValence = self.readEValence()
		self.xAxis = self.createXaxis()
		self.reference = 0
	
	'''
	Set a new reference for the eigenvalues
	'''
	def setReference (self, newRef):
		self.reference = newRef

	# nElec = total number of electrons in the cell
	def readNElec(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()
		nElec=int(float(outcar.split('NELECT =')[1].split('total number of electrons')[0]))
		fileIn.close()
		return  nElec 

	# return the fundamental gap
	def gap(self):
		nval=self.nElec/2
		v_band=[]
		c_band=[]	
		for k in range(len(self.path)):
			v_band.append(self.eigenvals[k][nval-1])
			c_band.append(self.eigenvals[k][nval])

		gap=min(c_band)-max(v_band)

		return gap

	# return the valence band maximum
	def readEValence(self):
		nval=int(self.nElec/2)
		v_band=[]	
		for k in range(len(self.path)):
			v_band.append(self.eigenvals[k][nval-1])
		return max(v_band)

	# return the direct gap
	def dGap(self):
		nval=self.nElec/2
		allGaps=[]
			
		for k in range(len(self.path)):
			allGaps.append(self.eigenvals[k][nval] - self.eigenvals[k][nval-1])

		gap=min(allGaps)

		return gap

	# xAxis[k-point] = normalized value from 0 to 1 to favor plotting
	def createXaxis(self):
		x=[0]
		aux=0
		
		for k in range(1, len(self.path)):
			aux=aux + distance(self.recLattice,self.path[k],self.path[k-1])
			x.append(aux)	
		norm=max(x)
		for k in range(len(x)):
			x[k]=x[k]/norm
		
		return x



	# eFermi = x.xxxx eV
	def readEFermi(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()
		ef=float(outcar.split('E-fermi :')[1].split('XC(G=0):')[0])#l1621
		fileIn.close()
		return  ef 	


	# path = [k-point 1, k-point 2, ...]
	def readPath(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()

		kpoints=[]	
		text=outcar.split('k-points in reciprocal lattice and weights:')[1].split('position of ions in fractional coordinates')[0] 
		#l487	
		lines=text.split('\n')
		for k in range(len(lines)):
			dados=lines[k].split()
			if len(dados)==4:
				kpoints.append([float(dados[0]),float(dados[1]),float(dados[2])])

		fileIn.close()
		return  kpoints 
	
	# recLattice = [b1,b2,b3]
	# b1 = [b1_x, b1_y, b1_z]
	def readRecLattice(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()

		lines=outcar.split('reciprocal lattice vectors')[1].split('length of vectors')[0].split('\n') #linha 432
		b1=[0,0,0]
		b2=[0,0,0]
		b3=[0,0,0]
	
		b1[0]=float(lines[1].split()[3])
		b1[1]=float(lines[1].split()[4])	
		b1[2]=float(lines[1].split()[5])	

		b2[0]=float(lines[2].split()[3])
		b2[1]=float(lines[2].split()[4])	
		b2[2]=float(lines[2].split()[5])

		b3[0]=float(lines[3].split()[3])
		b3[1]=float(lines[3].split()[4])	
		b3[2]=float(lines[3].split()[5])

		fileIn.close()
		return  [b1,b2,b3] 

	# eigenval[k-point][band]
	def readEigenvals(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()

		eigenvals=[]
		txtBlock=outcar.split('E-fermi :')[-1].split('---------------------------')[0]
		kpoints=txtBlock.split('band No.  band energies     occupation')

		# Obtaining the eigenvalues from OUTCAR
		for k in range(1,len(kpoints)):
			eigenvals.append([])
			lines=kpoints[k].split('\n')
			for i in lines:
				data=i.split()
				if len(data)==3:
					eigenvals[k-1].append(float(data[1]))		
		fileIn.close()
		return  eigenvals 

	# nBands = total number of bands
	def readNbands(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()
		nbands=int(float(outcar.split('NBANDS=')[1].split('number of dos')[0])) #l256
		fileIn.close()
		return  nbands 

'''
Auxiliary functions
'''

def distance (basis, p1, p2):
	d = np.linalg.norm (np.dot(np.array(p1)-np.array(p2), np.array(basis)))
	return d
