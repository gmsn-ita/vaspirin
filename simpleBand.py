import bandstructure
import numpy as np
import math
import pylab as pl

label=['G','W','X','L','M','K']
coordenates=[[0.0,0.0,0.0],[0.5 ,0.75, 0.25],[0.5 ,0.5, 0 ],[0.5 ,0.5 ,0.5],[0.5,0.0,0.0],[-0.3333,0.3333,0]]

class simpleBand(bandstructure.BandStructure):
	def __init__(self,fOutcar):
		self.path = self.readPath(fOutcar)
		self.nBands = self.readNbands(fOutcar)
		self.recLattice = self.readRecLattice(fOutcar)
		self.eigenvals = self.readEigenvals(fOutcar)
		self.eFermi = self.readEFermi(fOutcar)
		self.nElec = self.readNElec(fOutcar)
		self.eValence = self.readEValence()
		self.xAxis = self.createXaxis()
		self.reference = self.eValence
		self.way=self.readWay() #LIST OF SPECIAL K-POINTS (LABELS ONLY)
		self.symPath=self.readSymPath() #COORDENATES OF SPECIAL K-POINTS
		self.norm=self.calcNorm() #normalization factor in x axis
		self.locLabel=self.calcLoc() #location of the labels
		self.redPath = self.makeRedPath() # LIST OF [XAXIS,[KX,KY,KZ]]
		self.redBS= self.makeRedBS() #LIST OF [EIGENVALUES]
		self.redXAxis=self.readRedXAxis() #x coordenates


	def readWay(self):
		fin=open('WAY','r')
		way=fin.read()
		fin.close()
		output=[]
		for char in way:
			if char.isalpha():
				output.append(char.upper())
		print 'WAY=',output
		return output		

	def readSymPath(self):
		output=[]
		for char in self.way:
			index=label.index(char)
			newPoint=np.matrix( (coordenates[index][0],coordenates[index][1],coordenates[index][2]) ).transpose()
			output.append(newPoint)
		print 'symPath=',output,' Nkpt=', len(output)
		return output

	def calcNorm(self):
		baseaux=self.recLattice
		m = np.matrix( ((baseaux[0][0],baseaux[0][1],baseaux[0][2]), (baseaux[1][0],baseaux[1][1],baseaux[1][2]),(baseaux[2][0],baseaux[2][1],baseaux[2][2])) ).transpose()
		invm=np.linalg.inv(m)

		norm=0
		for k in range(len(self.symPath)-1):
			p1=self.symPath[k]
			p2=self.symPath[k+1]
			norm=norm+dist(invm,p1,p2)
		return norm

	def calcLoc(self):
		baseaux=self.recLattice
		m = np.matrix( ((baseaux[0][0],baseaux[0][1],baseaux[0][2]), (baseaux[1][0],baseaux[1][1],baseaux[1][2]),(baseaux[2][0],baseaux[2][1],baseaux[2][2])) ).transpose()
		invm=np.linalg.inv(m)
		loc=[]		
		x0=0.0
		loc.append(x0)
		for k in range(len(self.symPath)-1):
			p1=self.symPath[k]
			p2=self.symPath[k+1]
			x0=x0+ dist(invm,p1,p2)/self.norm
			loc.append(x0)
		return loc
		

	def makeRedPath(self):		
		baseaux=self.recLattice
		m = np.matrix( ((baseaux[0][0],baseaux[0][1],baseaux[0][2]), (baseaux[1][0],baseaux[1][1],baseaux[1][2]),(baseaux[2][0],baseaux[2][1],baseaux[2][2])) ).transpose()
		invm=np.linalg.inv(m)

		path=[]
		for k in range(len(self.symPath)-1):
			x0=self.locLabel[k]
			p1=self.symPath[k]
			p2=self.symPath[k+1]
			for kpt in self.path:
				kpoint=np.matrix( (kpt[0],kpt[1],kpt[2]) ).transpose()	
				if (colinear(m,kpoint,p1,p2)):
					x=dist(invm,p1,kpoint)/self.norm
					path.append([x0+x,kpt])
		path.sort()
		return path

	def makeRedBS(self):
		redBS=[]
		for kpt in self.redPath:
			index=self.path.index(kpt[1])
			redBS.append(self.eigenvals[index])
		return redBS

	def readRedXAxis(self):
		xaxis=[]
		for kpt in self.redPath:
			xaxis.append(kpt[0])
		return xaxis

	def printSBS(self):
		fout=open('SBS.out','w')
		for k1 in range(len(self.redXAxis)):
			fout.write(str(self.redXAxis[k1])+' ')
			for k2 in range(len(self.redBS[0])):
				fout.write(str(self.redBS[k1][k2])+' ')
			fout.write('\n')	
		fout.close()		



#PLOT FUNCTION 
def plotSimpleBand(bsData,figureName):
	bsData.setReference(bsData.eValence)
	for k1 in range(bsData.nBands):
		band=[]
		for k2 in range(len(bsData.redXAxis)):
			band.append(bsData.redBS[k2][k1]-bsData.reference)
		pl.plot(bsData.redXAxis,band,'k')

	#Setting plot
	pl.xlim(min(bsData.xAxis), max(bsData.xAxis))
	pl.ylim(-9, 9)

	pl.ylabel(r'E (eV)',fontsize=16)

	#pl.plot([min(bsData.xAxis), max(bsData.xAxis)],[0,0],'k--')

	#LABELLING X AXIS 
	pl.xticks(bsData.locLabel,bsData.way,fontsize=16)
	

	pl.savefig(figureName)
	return 0


'''
Auxiliary functions
'''
def colinear(m,p,p1,p2):
	tol_colinear=0.00001
#	matriz=np.matrix(( (p.item(0) ,p.item(1) ,p.item(2)), (p1.item(0) ,p1.item(1) ,p1.item(2)), (p2.item(0),p2.item(1),p2.item(2)) ))
	matriz=np.matrix(( (p.item(0) ,p.item(1) ,1), (p1.item(0) ,p1.item(1) ,1), (p2.item(0),p2.item(1),1) ))
	alfa=1

	bool1=abs(np.linalg.det(matriz))< tol_colinear

	if bool1 and min([dist(m,p,p1),dist(m,p,p2)])>0.000001:
		alfa=np.inner( (p-p1).getT() , (p2-p1).getT())/np.inner( (p2-p1).getT() , (p2-p1).getT())
		#print 'col:',p.getT(),p1.getT(),p2.getT(),'alfas:',alfa

	return (abs(np.linalg.det(matriz))< tol_colinear and alfa >-0.001 and alfa<1) 

def dist(m,v1,v2):
	#caso 2D	
	v1[2]=0
	v2[2]=0
	diff=np.linalg.inv(m)*(v1-v2)
	return math.sqrt((diff.getT()*diff).item())

def equal(x1,x2):
	tol=0.00001
	return (abs(x1[0]-x2[0])<tol and abs(x1[1]-x2[1])<tol and abs(x1[2]-x2[2])<tol)

