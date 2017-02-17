import re,sys

class PROJECTION (object):
	'''
	Deals with PROJECTION files, which are a custom user-generated file to process projection
	onto orbitals and atomic sites. The PROJECTION file should have the following format:

	The file PROJECTION (default name) should have the following format:
	 
	Material1Name ionsBelongingToMat1
	Material2Name ionsBelongingToMat2
	Material3Name ionsBelongingToMat3
	...

	For example, the file could be written as:
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

	def __init__ (self, fProjection = 'PROJECTION'):
		
		self.fProjection = fProjection
		'''
		The file to be opened. Default: PROJECTION
		'''

		self.ionsVsMaterials = []
		'''
		The list ionsVsMaterials contains `nIons` labels, which are integer numbers
		'''
		
		self.dictMaterials = {}
		'''
		The dictionary dictMaterials relates the label of the material with its index
		'''
		
		self.projectedColors = {}
		'''
		Dictionary containing the standard information for projected onto atomic sites.
		By default, it is set as empty and should be entered by the user. If not, the sequential colors will be used
		'''
		
		self.nAtoms = self.read_nAtoms ()
		'''
		Number of atoms found specified in the PROJECTION file
		'''
		
		self.importProjectionList()
		'''
		Import properties related to atoms within PROJECTION files 
		'''
	
		
	def read_nAtoms (self):
		'''
		Read the number of atoms specified in the PROJECTION file
		'''
		
		## Opens the PROJECTION file
		try:
			with open(self.fProjection,'r') as fileIn:
				ionsData = fileIn.read()
				
		except FileNotFoundError:
			print ('Projection file not found. Please specify a valid filename.')
			sys.exit()
			
		## matString has all data regarding the materials
		matString = ionsData.split('\n')
		matString = [i for i in matString if i]  # removes repeated \n
		
		## index is a variable that labels the materials with an integer number
		index = 0
		
		## Each line is a material, so, we loop over each material
		for eachMaterial in matString:
			## Interpreting the sintax of the PROJECTION file, i.e. decoding the punctuation signs
			belongingIons = re.split(' +', eachMaterial.strip())[1].split(',')
			
			for eachIon in belongingIons:
				## Two dots (x..y) represent something like 'from ion x to y'
				if eachIon.find('..') == -1:
					index += 1
				else:
					ionsInterval = eachIon.split('..')
					index += int(ionsInterval[1]) - int(ionsInterval[0]) + 1
			
		return index
		
	
	def importProjectionList (self):
		'''
		The list ionsVsMaterials should indicate the material to which the ion belong, e.g.:
		i) for two materials based on six atoms: [HfS2, HfS2, HfS2, ZrS2, ZrS2, ZrS2]
		ii) for three materials based on nine atoms with an odd order: [Mat1, Mat1, Mat3, Mat2, Mat2, Mat2, Mat3, Mat3, Mat1]
		''' 
		
		## Opens the PROJECTION file
		try:
			with open(self.fProjection,'r') as fileIn:
				ionsData = fileIn.read()
				
		except FileNotFoundError:
			print ('Projection file not found. Please specify a valid filename.')
			sys.exit()
			
		
		## matString has all data regarding the materials
		matString = ionsData.split('\n')
		matString = [i for i in matString if i]  # removes repeated \n
		
		## index is a variable that labels the materials with an integer number
		index = 0
		
		## The list ionsVsMaterials contains `nAtoms` labels, which are integer numbers
		self.ionsVsMaterials = [None]*self.nAtoms
		
		## The dictionary dictMaterials relates the label of the material with its index
		self.dictMaterials = {}
		
		## The dictionary projectedColors relates the color of the projected lines, for each material, with its index
		self.projectedColors = {}
		
		## Each line is a material, so, we loop over each material
		for eachMaterial in matString:
			## The first information should be the material
			matLabel = re.split(' +', eachMaterial.strip())[0]
			
			self.dictMaterials.update ({matLabel : index})
			## The third column should be the color of the material
			try:
				self.projectedColors.update ({index : re.split(' +', eachMaterial.strip())[2]})
			except IndexError:
				print ("Color not specified within PROJECTION file! Using defaults...")
				pass # do nothing
				
			index += 1
			
			## Interpreting the sintax of the PROJECTION file, i.e. decoding the punctuation signs
			belongingIons = re.split(' +', eachMaterial.strip())[1].split(',')
			
			for eachIon in belongingIons:
				## Two dots (x..y) represent something like 'from ion x to y'
				if eachIon.find('..') == -1:
					try:
						self.ionsVsMaterials[int(eachIon) - 1] = matLabel
					except:
						print ("Formatting error within PROJECTION file! Exiting...")
						sys.exit(1)
						
				else:
					ionsInterval = eachIon.split('..')
					nIonsInterval = int(ionsInterval[1]) - int(ionsInterval[0]) + 1
					
					try:
						for i in range (int(ionsInterval[0]), int(ionsInterval[1]) + 1):
							self.ionsVsMaterials[i - 1] = matLabel
					except:
						print ("Formatting error within PROJECTION file! Exiting...")
						sys.exit(1)	
		
		return
		
