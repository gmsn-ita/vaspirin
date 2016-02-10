#!/usr/bin/env python

class BandStructure (object):

	def __init__(self,fOutcar):
		self.path=self.readPath(fOutcar)
		self.Nbands=self.readNbands(fOutcar)
		self.recLattice=self.readRecLattice(fOutcar)
		self.eigenvals=self.readEigenvals(fOutcar)
		self.eFermi=self.readEFermi(fOutcar)
		self.nElec=self.NElec(fOutcar)
		self.eValence=self.readEValence()

	'''
	Atributes:
		path=[]
		eigenvalues=[]
		nbands=[]
		efermi=[]
		vbm=[]	
		cbm=[]
	'''

	def readNElec(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()
		nElec=int(float(outcar.split('NELECT =')[1].split('total number of electrons')[0]))
		fileIn.close()
		return  nElec 

	def gap(self):
		nval=self.nElec/2
		v_band=[]
		c_band=[]	
		for k in range(len(self.path)):
			v_band.append(self.eigenvals[k][nval-1])
			c_band.append(self.eigenvals[k][nval])

		gap=min(c_band)-max(v_band)

		return gap

	def readEValence(self):
		nval=self.nElec/2
		v_band=[]	
		for k in range(len(self.path)):
			v_band.append(self.eigenvals[k][nval-1])
		return max(v_band)


	def dGap(self):
		nval=self.nElec/2
		allGaps=[]
			
		for k in range(len(self.path)):
			allGaps.append(self.eigenvals[k][nval] - self.eigenvals[k][nval-1])

		gap=min(allGaps)

		return gap


	def xAxis(self):
		x=[0]
		aux=0
		
		for k in range(1, len(self.path)):
			aux=aux+distance(self.recLattice,self.path[k],self.path[k-1])
			x.append(aux)	
		norm=max(x)
		for k in range(len(x)):
			x[k]=x[k]/norm
		
		return x




	def readEFermi(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()
		ef=float(outcar.split('E-fermi :')[1].split('XC(G=0):')[0])#l1621
		fileIn.close()
		return  ef 	



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

	def readEigenvals(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()

		eigenvals=[]
		txtBlock=outcar.split('E-fermi :')[-1].split('---------------------------')[0]


		kpoints=txtBlock.split('band No.  band energies     occupation')


		for k in range(1,len(kpoints)):
			eigenvals.append([])
			lines=kpoints[k].split('\n')
			for i in lines:
				data=i.split()
				if len(data)==3:
					eigenvals[k-1].append(float(data[1]))		
		fileIn.close()
		return  eigenvals 




	def readNbands(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()
		nbands=int(float(outcar.split('NBANDS=')[1].split('number of dos')[0])) #l256
		fileIn.close()
		return  nbands 


