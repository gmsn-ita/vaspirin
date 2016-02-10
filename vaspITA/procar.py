class PROCAR (object):
	'''
	Deals with PROCAR-related information.
	
	Available operations:
	 -> Seek number of bands
	 -> Seek number of k-points
	 -> Seek number of ions
	 -> Seek contributions of each orbital for each band and k-point
	 -> Seek contributions of each ion for each band and k-point
	'''

	def __init__ (self, fProcar):
		self.Nbands = self.readNbands (fProcar)
		self.Nkpoints = self.readNkpoints (fProcar)
		self.Nions = self.readNions (fProcar)
		self.orbitalContributions = self.readOrbitalContribution (fProcar)
		self.ionContributions = self.readIonContribution (fProcar)
	
	# Returns the number of bands used in the simulation	
	def readNbands (self,fProcar):
		fileIn=open(fProcar,'r')
        
		Nbands = int(fileIn.read().split('\n')[1].split(':')[2].split()[0])
        
		fileIn.close()        
		return Nbands
	
	# Returns the number of k-points used in the simulation
	def readNkpoints (self,fProcar):
		fileIn=open(fProcar,'r')
        
		Nkpoints = int(fileIn.read().split('\n')[1].split(':')[1].split()[0])
        
		fileIn.close()        
		return Nkpoints
	
	# Returns the number of ions used in the simulation	
	def readNions (self,fProcar):
		fileIn=open(fProcar,'r')
        
		Nions = int(fileIn.read().split('\n')[1].split(':')[3].split()[0])
        
		fileIn.close()        
		return Nions
	
	# Creates a matrix containing the contribution of each orbita
	def readOrbitalContribution (self,fProcar):
		fileIn=open(fProcar,'r')
		procar = fileIn.read()
        
        # contributions[kpoint][band] returns the list [s,px+py,pz,d]
		contributions = []
		
		kptBlock = procar.split('k-point')
		
		for k in range (2,len(kptBlock)):
			contributions.append([])
			bands = kptBlock[k].split('band')
			for j in range (1,self.Nbands+1):
				contributions[k-2].append([])
				lines = bands[j].split('\n')
				
				totCont = float(lines[3+self.Nions].split()[10])
				
				if totCont > 0:
					sCont = float(lines[3+self.Nions].split()[1])/totCont
					pyCont = float(lines[3+self.Nions].split()[2])/totCont
					pzCont = float(lines[3+self.Nions].split()[3])/totCont
					pxCont = float(lines[3+self.Nions].split()[4])/totCont
					dxyCont = float(lines[3+self.Nions].split()[5])/totCont
					dyzCont = float(lines[3+self.Nions].split()[6])/totCont
					dz2Cont = float(lines[3+self.Nions].split()[7])/totCont
					dxzCont = float(lines[3+self.Nions].split()[8])/totCont
					dx2Cont = float(lines[3+self.Nions].split()[9])/totCont
					contributions[k-2][j-1].append([sCont, pyCont + pxCont, pzCont, dxyCont + dyzCont + dz2Cont + dxzCont + dx2Cont])
				else:
					contributions[k-2][j-1].append([0,0,0,0])
		
		fileIn.close()        
		
		return contributions
		

	def readIonContribution (self,fProcar):
		fileIn=open(fProcar,'r')
		procar = fileIn.read()
		
		# contributions[kpoint][band][ion]
		contributions = []
		
		kptBlock = procar.split('k-point')
		
		for k in range (2,len(kptBlock)):
			contributions.append([])
			bands = kptBlock[k].split('band')
			for j in range (1,self.Nbands+1):
				contributions[k-2].append([])
				lines = bands[j].split('\n')
				
				totCont = float(lines[3+self.Nions].split()[10])
				
				if totCont > 0:
					ionContributionThisBand = []
					for i in range(self.Nions):
						ionContributionThisBand.append(float(lines[3+i].split()[10])/totCont)

					contributions[k-2][j-1].append(ionContributionThisBand)
				else:
					contributions[k-2][j-1].append([0]*self.Nions)
		
		fileIn.close()        
		
		return contributions
			
		

def main():
		# my code here
		teste = PROCAR('PROCAR')
		print(teste.ionContributions)

if __name__ == "__main__":
		main()
