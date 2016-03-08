import numpy as np
import math

class ebs(object):	
	# Import all properties related to band structures
	def __init__(self,fPrjcar,fOutcar):
		self.recLattice = self.readRecLattice(fOutcar)
		self.kPrim=self.readkPrim(fPrjcar)
		self.bs=self.readBS(fPrjcar)
		self.data = self.look4Kpt(fPrjcar)
		self.eFermi = self.readEFermi(fOutcar)
		self.reference = self.eFermi

	
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

	def readkPrim(self,fPrjcar):
		prjcar=open(fPrjcar, 'r')
		text=prjcar.read()
		kPrimf=text.split('             b1            b2            b3      weight')[1].split('spin component:')[0].split('\n')
		kPrim=[]
		for line in kPrimf:
			fields=line.split() 
			if len(fields)==5:
				kPrim.append([float(fields[1]),float(fields[2]),float(fields[3])])
		prjcar.close()
		return (kPrim)

	def readBS(self,fPrjcar):
		tol=0.001
		bs=[]
		for k in range(len(self.kPrim)):
			bs.append([])
		#laco sobre os vetores k da rede reciproca reduzida
		prjcar=open(fPrjcar, 'r')
		lista=prjcar.read().split('energy:')

		for k in range(1, len(lista)):
			fields=lista[k].split()
			energia=fields[0]

			for k1 in range(1,len(self.kPrim)+1):
				if float(fields[k1])>tol:				
					bs[k1-1].append([energia, fields[k1]])
		prjcar.close()
		return (bs)

	def printUnfoldedEigenval(self):
		NewEigen=open('EiGENVAL.unfold','w')
		for k in range(len(self.kPrim)):
			NewEigen.write('kpoint:'+str(self.kPrim[k][0])+ ' '+str(self.kPrim[k][1])+ ' '+str(self.kPrim[k][2])+' ;\n')
			cont=1
			for k1 in range(len(self.bs[k])):
				NewEigen.write(str(cont)+' '+str(self.bs[k][k1][0])+' '+str(self.bs[k][k1][1])+'\n')
				cont=cont+1
		NewEigen.close()
		return (True)

	def printEBS(self):
		estrutura_bandas=open('EBS','w')
		lixo=[]
		k0=0
		campos=len(self.data[k0])

		while (not (len(self.data[k0])==3)):
			k0=k0+1

		estrutura_bandas.write(str(self.data[k0][0])+' '+str(self.data[k0][1])+' '+str(self.data[k0][2])+' \n')
		old=self.data[k0]

		for k in range(1,len(self.data)):
			if len(self.data[k])==3:	
				new=self.data[k]
	
				if (not equal(old,new)):
					estrutura_bandas.write(str(self.data[k][0])+' '+str(self.data[k][1])+' '+str(self.data[k][2])+' \n')
				old=new

		return 0


	# path = [k-point 1, k-point 2, ...] <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
	def look4Kpt(self,fPrjcar):
		#High symmetry points
		Pgama=np.matrix( (0,0,0) ).transpose()
		Pm=np.matrix( (0,0.5,0) ).transpose()
		Pk=np.matrix( (1.0/3.0,2.0/3.0,0) ).transpose()
		Pkk=np.matrix( (-1.0/3.0,1.0/3.0,0) ).transpose()

		#m= matrix of basis change
		baseaux=self.recLattice
		m = np.matrix( ((baseaux[0][0],baseaux[0][1],baseaux[0][2]), (baseaux[1][0],baseaux[1][1],baseaux[1][2]),(baseaux[2][0],baseaux[2][1],baseaux[2][2])) ).transpose()
		invm=np.linalg.inv(m)
		#rot=60o degrees rotation matrix
		rot = invm*np.matrix( ((0.5,0.5*math.sqrt(3),0), (-0.5*math.sqrt(3),0.5,0),(0,0,1)) )*m

		norm=dist(m,Pgama, Pm)+dist(m, Pm, Pk)+dist(m, Pgama, Pk)

		
		#fatores de escala de cada um dos caminhos (ajustar para obter vel de fermi e massa reduzida)
		d1=dist(m, Pgama, Pm)/norm
		d2=dist(m, Pm, Pk)/norm
		d3=dist(m, Pgama, Pk)/norm
		out_banda=[]
		

		#montando a linha gama-m
		p1=Pgama
		p2=Pm

		x0=0.0
		for k in range(6):
	
			p1=rot*p1
			p2=rot*p2
			#print '####p1,p2=',p1.getT(),p2.getT()
			for n in range(len(self.kPrim)):
				kponto=np.matrix( (self.kPrim[n][0],self.kPrim[n][1],self.kPrim[n][2]) ).transpose()
				if (isBetween(kponto,p1,p2)):

					x=d1*(dist(m,p1,kponto)/dist(m,p1,p2))
					#print x0+x,kponto.getT(), 'isBetween:',p1.getT(),p2.getT()
					for estado in self.bs[n]:								
						out_banda.append([x0+x, float(estado[0]),float(estado[1])])
		#montando a linha m-k
		p1=Pm
		p2=Pkk

		#print '#####################  Caminho m-k' 
		x0=d1
		#print x0
		for k in range(6):	
			p1=rot*p1
			p2=rot*p2
			#print '####p1,p2=',p1.getT(),p2.getT()
			for n in range(len(self.kPrim)):
				kponto=np.matrix( (self.kPrim[n][0],self.kPrim[n][1],self.kPrim[n][2]) ).transpose()
				if (colinear(kponto,p1,p2)):
			
					x=d2*(dist(m,p1,kponto)/dist(m,p1,p2))
					#print x0+x,kponto.getT(), 'colinear:',p1.getT(),p2.getT()	
					if x<d2:		
						for estado in self.bs[n]:								
							out_banda.append([x0+x, float(estado[0]),float(estado[1])])


		#montando a linha k-gama
		p1=Pk
		p2=Pgama
		x0=d1+d2
		for k in range(6):	
			p1=rot*p1
			p2=rot*p2
			#print '####p1,p2=',p1.getT(),p2.getT()
			for n in range(len(self.kPrim)):
				kponto=np.matrix( (self.kPrim[n][0],self.kPrim[n][1],self.kPrim[n][2]) ).transpose()
				if (isBetween(kponto,p1,p2)):

					x=d3*(dist(m,p1,kponto)/dist(m,p1,p2))
					#print x0+x,kponto.getT(), 'isBetween:',p1.getT(),p2.getT()
					for estado in self.bs[n]:								
						out_banda.append([x0+x, float(estado[0]),float(estado[1])])


		#montando a linha kk-gama
		p1=Pkk
		p2=Pgama
		#print '#####################  Caminho kk-gama' 
		for k in range(6):	
			p1=rot*p1
			p2=rot*p2
			#print '####p1,p2=',p1.getT(),p2.getT()
			for n in range(len(self.kPrim)):
				kponto=np.matrix( (self.kPrim[n][0],self.kPrim[n][1],self.kPrim[n][2]) ).transpose()
				if (isBetween(kponto,p1,p2)):

					x=d3*(dist(m,p1,kponto)/dist(m,p1,p2))
					#print x0+x,kponto.getT(), 'isBetween:',p1.getT(),p2.getT()
					for estado in self.bs[n]:								
						out_banda.append([x0+x, float(estado[0]),float(estado[1])])
		out_banda.sort()
		return (out_banda)

	# eFermi = x.xxxx eV
	def readEFermi(self,fOutcar):
		fileIn=open(fOutcar,'r')
		outcar=fileIn.read()
		ef=float(outcar.split('E-fermi :')[1].split('XC(G=0):')[0])#l1621
		fileIn.close()
		return  ef 	





	'''
	Set a new reference for the eigenvalues
	'''
	def setReference (self, newRef):
		self.reference = newRef


'''
Auxiliary functions
'''

def colinear(p,p1,p2):
	tol_colinear=0.00001
	matrix=np.matrix(( (p.item(0) ,p.item(1) ,p.item(2) ) , (p1.item(0) ,p1.item(1) ,p1.item(2)), (p2.item(0),p2.item(1),p2.item(2)) ))
	bool1=abs(np.linalg.det(matrix))< tol_colinear
	return (bool1) 

def isBetween(p,p1,p2):
	boolOut=False
	if colinear(p,p1,p2):
		weight=(p.item(0)-p2.item(0))/(p1.item(0)-p2.item(0))
		boolOut= (weight>0) and (weight<1)
	return (boolOut)
	
def distance(basis, p1, p2):
	d = np.linalg.norm (np.dot(np.array(p1)-np.array(p2), np.array(basis)))
	return d

def dist(m,v1,v2):
	#caso 2D	
	v1[2]=0
	v2[2]=0
	diff=np.linalg.inv(m)*(v1-v2)
	return math.sqrt((diff.getT()*diff).item())


def equal(x1,x2):
	tol=0.00001
	return (abs(x1[0]-x2[0])<tol/10 and abs(x1[1]-x2[1])<tol/10 and abs(x1[2]-x2[2])<tol/10)

