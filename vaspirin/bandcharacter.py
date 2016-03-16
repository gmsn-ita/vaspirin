import sys

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

	def __init__ (self, fProcar, nKPTignore):
		self.nKPTignore = nKPTignore
		self.nBands = self.readNbands (fProcar)
		self.nKpoints = self.readNkpoints (fProcar)
		self.nIons = self.readNions (fProcar)
		self.orbitalContributions = self.readOrbitalContribution (fProcar)
		self.ionContributions = self.readIonContribution (fProcar)
		self.ionsVsMaterials = []
		self.materialContributions = []
		self.dictMaterials = {}
	
	# Returns the number of bands used in the simulation	
	def readNbands (self,fProcar):
		fileIn=open(fProcar,'r')
        
		nBands = int(fileIn.read().split('\n')[1].split(':')[2].split()[0])
        
		fileIn.close()        
		return nBands
	
	# Returns the number of k-points used in the simulation
	def readNkpoints (self,fProcar):
		fileIn=open(fProcar,'r')
        
		Nkpoints = int(fileIn.read().split('\n')[1].split(':')[1].split()[0])
        
		fileIn.close()        
		return Nkpoints
	
	# Returns the number of ions used in the simulation	
	def readNions (self,fProcar):
		fileIn=open(fProcar,'r')
        
		nIons = int(fileIn.read().split('\n')[1].split(':')[3].split()[0])
        
		fileIn.close()        
		return nIons
	
	# Creates a matrix containing the contribution of each orbital
	def readOrbitalContribution (self,fProcar):
		fileIn=open(fProcar,'r')
		procar = fileIn.read()
        
        # contributions[kpoint][band] returns the list [s,px+py,pz,d]
		contributions = []
		
		kptBlock = procar.split('k-point')
		
		for k in range (2 + self.nKPTignore,len(kptBlock)):
			contributions.append([])
			bands = kptBlock[k].split('band')
			for j in range (1,self.nBands+1):
				contributions[k-self.nKPTignore-2].append([])
				lines = bands[j].split('\n')
				
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
		
		fileIn.close()        
		
		return contributions
		

	def readIonContribution (self,fProcar):
		fileIn=open(fProcar,'r')
		procar = fileIn.read()
		
		# contributions[k-point][band][ion]
		contributions = []
		
		kptBlock = procar.split('k-point')
		
		for k in range (2 + self.nKPTignore,len(kptBlock)):
			contributions.append([])
			bands = kptBlock[k].split('band')
			for j in range (1,self.nBands+1):
				contributions[k-self.nKPTignore-2].append([])
				lines = bands[j].split('\n')
				
				totCont = float(lines[3+self.nIons].split()[10])
				
				if totCont > 0:
					ionContributionThisBand = []
					for i in range(self.nIons):
						ionContributionThisBand.append(float(lines[3+i].split()[10])/totCont)

					contributions[k-self.nKPTignore-2][j-1].extend(ionContributionThisBand)
				else:
					contributions[k-self.nKPTignore-2][j-1].extend([0]*self.nIons)
		
		fileIn.close()        
		
		return contributions
	
	# sum the contributions from the ions into N materials based on the list ionsVsMaterials
	def sumContributions (self):

		projectedContributions = []
		for kpt in range(self.nKpoints - self.nKPTignore):
			projectedContributions.append ([])
			
			for band in range (self.nBands):
				projectedContributions[kpt].append ([])
				projectedContributions[kpt][band].extend ([0]*len(self.dictMaterials))
				
				for ionIndex in range(self.nIons):		
								
					# projectedContribution [k-point][band][material in index form]
					projectedContributions[kpt][band][self.dictMaterials.get(self.ionsVsMaterials[ionIndex])] = projectedContributions[kpt][band][self.dictMaterials.get(self.ionsVsMaterials[ionIndex])] + self.ionContributions[kpt][band][ionIndex]
		
		self.materialContributions = projectedContributions
		return
				
		
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
	def createIonVsMaterials (self, fileProjection):
		fileIn=open(fileProjection,'r')
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
			
		if len(self.ionsVsMaterials) != self.nIons:
			print ("Error in the argument of the projection on ions: not all ions are specified!")
			sys.exit(1)
		
		self.sumContributions()
		
		return
