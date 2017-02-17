import os,sys,shutil
from . import projection

class PROCAR_splitter (object):
	'''
	Deals with big PROCAR files: splits the file directly onto .dat files, thus bypassing the .dat generator. This is useful for very large files (~ GB files), since it does not requires the standard open-and-close approach to reading the files, but reads it only once and one line per time.
	'''

	def __init__ (self, fProcar, projection, bs, marker=0.5, nKPTignore=0):
		
		self.fProcar = fProcar
		"""
		PROCAR file to be split
		"""
		
		self.prj = projection
		"""
		PROJECTION information
		"""
		
		self.nKPTignore = nKPTignore
		"""
		Number of k-points to be ignored
		"""
		
		self.nKpoints,self.nBands,self.nIons = self.readHeader ()
		"""
		Number of k-points, bands and ions used in the calculation
		"""
		
		self.axis = bs.xAxis
		"""
		x-axis associated with the band structure in this same calculation
		"""
		
		self.ref = bs.reference
		"""
		Reference for the 0 eV level
		"""
		
		self.markerSize = float(marker)
		"""
		The size of the symbols
		"""
		
	
	def readHeader (self):
		'''
		Reads the number of k-points, bands and ions in the simulation from
		the header of the PROCAR file. Uses only the first two lines.
		'''
		try:
			with open(self.fProcar,'r') as f:
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
			
			
			
	def splitPROCAR (self):
		'''
		Splits the PROCAR file as made by the plotter.
		'''
		
		try:
			os.mkdir ('bands_projected')
		except FileExistsError:
			shutil.rmtree ('bands_projected')
			os.mkdir ('bands_projected')
			
		try:
			with open(self.fProcar,'r') as f:
				## Discard the first three lines
				for i in range(3):
					f.readline()
				
				## Discard the first nKPT points to be ignored
				for kpt in range (self.nKPTignore):
					f.readline() # Throw away the k-point line
					f.readline() # and a blank line
					
					for band in range (self.nBands):
						f.readline() ## Throw away the band line,
						f.readline() ## a blank line,
						f.readline() ## and the table header
						
						for ion in range(self.nIons):
							f.readline() # Throw away each atom's contribution
						
						f.readline() # Total contributions line
						f.readline() # and a blank line
					
					f.readline() # Throw away a blank line
						
						
				## Starts to read the files and k-points
				for kpt in range (self.nKpoints - self.nKPTignore):
					f.readline() # Throw away the k-point line
					f.readline() # and a blank line
					
					## Read the information
					for band in range (self.nBands):
						## Read the eigenvalue
						eigenval = float(f.readline().split('energy')[1].split()[0])
						
						f.readline() ## Throw away a blank line
						f.readline() ## and the table header
						
						contributions = []
						
						## Read total contributions from all atoms
						for ion in range(self.nIons):
							contributions.append( float(f.readline().split()[-1]) )
						
						## Read total contributions
						totContributions = float(f.readline().split()[-1])
						
						f.readline() # Throw away a blank line
						
						## Normalize
						contributions = [x/totContributions for x in contributions]
						
						## Sum contributions
						projectedContributions = self.sumContributions(contributions)
						
						## Print in .dat file
						with open ("bands_projected/band%02d.dat" % int(band+1),'a') as outputFile:
							outputFile.write ("%.6f % 3.6f" % (self.axis[kpt], eigenval - self.ref))
							
							for i in range(len(projectedContributions)):
								outputFile.write(" %1.4f" % (projectedContributions[i]*self.markerSize))
							outputFile.write ("\n")
					
					f.readline() # Throw away a blank line
		
		except FileNotFoundError:
			print ("PROCAR file not found! Exiting...\n")
			sys.exit (1)
	
	
	def splitOrbitals (self):
		'''
		Splits the PROCAR file projected onto atomic orbitals, as made by the plotter.
		'''
		
		try:
			os.mkdir ('bands_character')
		except FileExistsError:
			shutil.rmtree ('bands_character')
			os.mkdir ('bands_character')
			
		try:
			with open(self.fProcar,'r') as f:
				## Discard the first three lines
				for i in range(3):
					f.readline()
				
				## Discard the first nKPT points to be ignored
				for kpt in range (self.nKPTignore):
					f.readline() # Throw away the k-point line
					f.readline() # and a blank line
					
					for band in range (self.nBands):
						f.readline() ## Throw away the band line,
						f.readline() ## a blank line,
						f.readline() ## and the table header
						
						for ion in range(self.nIons):
							f.readline() # Throw away each atom's contribution
						
						f.readline() # Total contributions line
						f.readline() # and a blank line
					
					f.readline() # Throw away a blank line
						
						
				## Starts to read the files and k-points
				for kpt in range (self.nKpoints - self.nKPTignore):
					f.readline() # Throw away the k-point line
					f.readline() # and a blank line
					
					## Read the information
					for band in range (self.nBands):
						## Read the eigenvalue
						eigenval = float(f.readline().split('energy')[1].split()[0])
						
						f.readline() ## Throw away a blank line
						f.readline() ## and the table header
						
						## Simply read lines containing contributions from all atoms
						for ion in range(self.nIons):
							f.readline()
						
						## Read total contributions
						lineTotContributions = f.readline().split()
						totCont = float(lineTotContributions[-1])
						
						contributions = []
						
						## And the orbital-projected contributions
						if totCont > 0:
							sCont = float(lineTotContributions[1])/totCont
							pyCont = float(lineTotContributions[2])/totCont
							pzCont = float(lineTotContributions[3])/totCont
							pxCont = float(lineTotContributions[4])/totCont
							dxyCont = float(lineTotContributions[5])/totCont
							dyzCont = float(lineTotContributions[6])/totCont
							dz2Cont = float(lineTotContributions[7])/totCont
							dxzCont = float(lineTotContributions[8])/totCont
							dx2Cont = float(lineTotContributions[9])/totCont
							contributions = [sCont, pyCont + pxCont, pzCont, dxyCont + dyzCont + dz2Cont + dxzCont + dx2Cont]
						else:
							contributions = [0,0,0,0]
						
						f.readline() # Throw away a blank line
						
						## Print in .dat file
						with open ("bands_character/band%02d.dat" % int(band+1),'a') as outputFile:
							outputFile.write ("%.6f % 3.6f" % (self.axis[kpt], eigenval - self.ref))
							
							for i in range(len(contributions)):
								outputFile.write(" %1.4f" % (contributions[i]*self.markerSize))
							outputFile.write ("\n")
					
					f.readline() # Throw away a blank line
		
		except FileNotFoundError:
			print ("PROCAR file not found! Exiting...\n")
			sys.exit (1)
			

	def sumContributions (self, c):
		'''
		Sum the contributions from the ions into N materials based on the list ionsVsMaterials.
		'''
		
		projectedContributions = [0]*len(self.prj.dictMaterials)
		
		for eachIon in range(self.nIons):		
			ionLabel = self.prj.dictMaterials.get(self.prj.ionsVsMaterials[eachIon])
			
			## projectedContribution [material in index form]
			projectedContributions[ionLabel] += c[eachIon]
			
		return projectedContributions
		

