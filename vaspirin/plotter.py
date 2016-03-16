#!/usr/bin/env python
import os, shutil

class DatFiles (object):
	'''
	Generate .dat files for XMGrace
	The files are generated in the current directory
	'''
	
	def __init__ (self, markerSize):
		self.markerSize = markerSize
		self.flagINTERPOLATE = 0
		self.pointsInterpolate = 0
	
	def setInterpolateOptions (self, flag, numberPoints):
		self.flagInterpolate = flag
		self.pointsInterpolate = numberPoints
	
	
	'''
	Creates the eigenv.dat file
	Format:
	1st column) normalized k-point (from 0 to 1, derived from the path length)
	2nd column) eigenvalue
	'''
	def datEigenvals (self, bandStructure):
		with open ("eigenv.dat",'w') as outputFile:
			for band in range(bandStructure.nBands):
				for kpoint in range(1, len(bandStructure.xAxis)):
					if self.flagInterpolate:
						for interpol_kpt in range (self.pointsInterpolate+1):
							t = (interpol_kpt)/(self.pointsInterpolate+1)
							outputFile.write ("%.6f % 3.6f\n" % (((1-t)*bandStructure.xAxis[kpoint-1] + t*bandStructure.xAxis[kpoint]), ((1-t)*bandStructure.eigenvals[kpoint-1][band] + t*bandStructure.eigenvals[kpoint][band]) - bandStructure.reference))
					else:
						outputFile.write ("%.6f % 3.6f\n" % (bandStructure.xAxis[kpoint-1], bandStructure.eigenvals[kpoint-1][band] - bandStructure.reference))
				
				outputFile.write ("%.6f % 3.6f\n" % (bandStructure.xAxis[len(bandStructure.xAxis)-1], bandStructure.eigenvals[len(bandStructure.xAxis)-1][band] - bandStructure.reference))
				
				outputFile.write ("\n")
	
	'''
	Creates the bands_character folder
	Each file contains the eigenvalues and contributions projected for each band
	Format:
	1st column) normalized k-point (from 0 to 1, derived from the path length)
	2nd column) eigenvalue
	
	The following columns contain the relative contribution of each orbital, canonically:
	3rd column) contribution of the s orbitals
	4th column) contribution of the px + py orbitals
	5th column) contribution of the pz orbitals
	6th column) contribution of the d orbitals
	
	Depending on the functions, the contributions of other orbitals, e.g. dz2, may be explicited in other columns
	However, this requires modifications on the code not yet implemented
	
	The markerSize variable scales the size of the marker plotted
	'''
	def datCharacter (self, bandStructure, bandCharacter):

		try:
			os.mkdir ('bands_character')
		except:
			shutil.rmtree ('bands_character')
			os.mkdir ('bands_character')
			
		for band in range(bandStructure.nBands):
			with open ("bands_character/band%02d.dat" % int(band+1),'w') as outputFile:
				for kpoint in range(1, len(bandStructure.xAxis)):
					if self.flagInterpolate:
						for interpol_kpt in range (self.pointsInterpolate+1):
							t = (interpol_kpt)/(self.pointsInterpolate+1)
							
							outputFile.write ("%.6f % 3.6f" % ((1-t)*bandStructure.xAxis[kpoint-1] + t*bandStructure.xAxis[kpoint], (1-t)*bandStructure.eigenvals[kpoint-1][band] + t*bandStructure.eigenvals[kpoint][band] - bandStructure.reference))
							
							for i in range(len(bandCharacter.orbitalContributions[kpoint][band])):
								outputFile.write(" %1.4f" % ((1-t)*float(bandCharacter.orbitalContributions[kpoint-1][band][i])*float(self.markerSize) + t*float(bandCharacter.orbitalContributions[kpoint][band][i])*float(self.markerSize)))
							outputFile.write ("\n")

					else:			
						outputFile.write ("%.6f % 3.6f" % (bandStructure.xAxis[kpoint-1], bandStructure.eigenvals[kpoint-1][band] - bandStructure.reference))
						for contrib in bandCharacter.orbitalContributions[kpoint-1][band]:
							outputFile.write(" %1.4f" % (float(contrib)*float(self.markerSize)))	
						outputFile.write ("\n")
				
				# Print last k-point
				outputFile.write ("%.6f % 3.6f" % (bandStructure.xAxis[len(bandStructure.xAxis)-1], bandStructure.eigenvals[len(bandStructure.xAxis)-1][band] - bandStructure.reference))
				for contrib in bandCharacter.orbitalContributions[len(bandStructure.xAxis)-1][band]:
					outputFile.write(" %1.4f" % (float(contrib)*float(self.markerSize)))
				outputFile.write ("\n")
									
				outputFile.write ("\n")
		
	'''
	Creates the bands_projected folder
	Each file in the folder contains the eigenvalues and contributions projected for each band
	Format:
	1st column) normalized k-point (from 0 to 1, derived from the path length)
	2nd column) eigenvalue
	
	The following columns contain the relative contribution of each material:
	3rd column) contribution of the 1st material
	4th column) contribution of the 2nd material
	... and so on
	
	The markerSize variable scales the size of the marker plotted
	'''
	def datProjected (self, bandStructure, bandCharacter):
		if self.markerSize <= 0:
			self.markerSize = 0.5
			
		try:
			os.mkdir ('bands_projected')
		except:
			shutil.rmtree ('bands_projected')
			os.mkdir ('bands_projected')
			
		for band in range(bandStructure.nBands):
			with open ("bands_projected/band%02d.dat" % int(band+1),'w') as outputFile:
				for kpoint in range(1, len(bandStructure.xAxis)):
					if self.flagInterpolate:
						for interpol_kpt in range (self.pointsInterpolate+1):
							t = (interpol_kpt)/(self.pointsInterpolate+1)
							
							outputFile.write ("%.6f % 3.6f" % ((1-t)*bandStructure.xAxis[kpoint-1] + t*bandStructure.xAxis[kpoint], (1-t)*bandStructure.eigenvals[kpoint-1][band] + t*bandStructure.eigenvals[kpoint][band] - bandStructure.reference))
					
							for i in range(len(bandCharacter.materialContributions[kpoint-1][band])):
								outputFile.write(" %1.4f" % ((1-t)*float(bandCharacter.materialContributions[kpoint-1][band][i])*float(self.markerSize) + t*float(bandCharacter.materialContributions[kpoint][band][i])*float(self.markerSize)))
							outputFile.write ("\n")
								
					else:
						outputFile.write ("%.6f % 3.6f" % (bandStructure.xAxis[kpoint-1], bandStructure.eigenvals[kpoint-1][band] - bandStructure.reference))
						for contrib in bandCharacter.materialContributions[kpoint][band]:
							outputFile.write(" %1.4f" % (float(contrib)*float(self.markerSize)))
						outputFile.write ("\n")
				
				# Print last k-point
				outputFile.write ("%.6f % 3.6f" % (bandStructure.xAxis[len(bandStructure.xAxis)-1], bandStructure.eigenvals[len(bandStructure.xAxis)-1][band] - bandStructure.reference))
				for contrib in bandCharacter.materialContributions[len(bandStructure.xAxis)-1][band]:
					outputFile.write(" %1.4f" % (float(contrib)*float(self.markerSize)))
				outputFile.write ("\n")
						
				outputFile.write ("\n")
				
				
class GraceConstants (object):
	colors = {
	"white" : 0,
	"black" : 1,
	"red" : 2,
	"green" : 3,
	"blue" : 4,
	"yellow" : 5,
	"brown" : 6,
	"gray" : 7,
	"violet" : 8,
	"cyan" : 9,
	"magenta" : 10,
	"orange" : 11,
	"indigo" : 12,
	"maroon" : 13,
	"turquoise" : 14,
	"green4" : 15
	}
	
	fonts = {
	"times-roman" : 0,
	"times-italic" : 1,
	"times-bold" : 2,
	"times-bold-italic" : 3,
	"helvetica" : 4,
	"helvetica-oblique" : 5,
	"helvetica-bold" : 6,
	"helvetica-bold-oblique" : 7,
	"courier" : 8,
	"courier-oblique" : 9,
	"courier-bold" : 10,
	"courier-bold-oblique" : 11,
	"symbol" : 12,
	"dingbats" : 13,
	"optima" : 14
	}

class Grace (object):
	'''
	Generate files with extension .bfile
	Each one of these files is a XMGrace batch for the chosen option
	'''
	
	'''
	Default parameters for the plots
	'''
	def __init__ (self):
		self.setDefaultParameters() 

	def setDefaultParameters(self):
		self.yMax = 3
		self.yMin = -3
		self.xMax = 1
		self.xMin = 0
		self.xTicks = []
		self.title = ""
		self.subtitle = ""
		self.font = "optima"
	
	def setYaxis (self, yMin, yMax):
		self.yMax = yMax
		self.yMin = yMin
	
	'''
	xTicks[index] = ["label string", normalized index from 0 to 1]
	'''
	def setXticks (self, ticksList):
		self.xTicks = ticksList
	
	'''
	KPOINTS header: KPT_1 index_1, KPT_2 index_2 ...
	Example G 1, M 20, K 40, G 60
	'''
	def readXticks (self, fKpoints):
		ticks = []
		with open (fKpoints, 'r') as fileIn:
			firstLine = fileIn.readline()
			symKpt = firstLine.strip('\n').split(',')
			for eachKpt in symKpt:
				l = eachKpt.split(' ')
				l = [i for i in l if i] # strips whitespace
				ticks.append ([l[0], l[1]])
		
		self.setXticks (ticks)
		
	def setTitle (self, titleString):
		self.title = titleString
		
	def setSubtitle (self, subtitleString):
		self.subtitle = subtitleString

	def printFontSection (self, outputFile):
		'''
		Font section
		'''		
		outputFile.write ("map font %d to \"Optima\", \"Optima\" \n" % GraceConstants.fonts.get("optima"))
		outputFile.write ("title font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("subtitle font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("legend font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("xaxis label font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("xaxis ticklabel font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("yaxis label font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("yaxis ticklabel font %d \n" % GraceConstants.fonts.get(self.font))
		
	def printAxis (self, outputFile, bands):
		# Defining XY axis
		outputFile.write ("world %.3f, %.3f, %.3f, %.3f \n" % (self.xMin, self.yMin, self.xMax, self.yMax))
		
		# Y ticks settings
		outputFile.write ("yaxis  tick on \n")
		outputFile.write ("yaxis  tick major 1 \n")
		outputFile.write ("yaxis  tick minor ticks 3 \n")
		outputFile.write ("yaxis  tick major size 1.000000\n")
		outputFile.write ("yaxis  ticklabel char size 1.500000\n")
		
		# Enable symmetry points in the X axis
		outputFile.write ("xaxis  tick on \n")
		outputFile.write ("xaxis  tick spec type both \n")
		outputFile.write ("xaxis  tick spec %d \n" % len(self.xTicks))
		outputFile.write ("xaxis  ticklabel char size 1.500000\n")
		
		# Symmetry points have vertical dashed lines
		outputFile.write ("xaxis  tick major linestyle 4 \n")
		outputFile.write ("xaxis  tick major grid on \n")
		

		# Writing the symmetry points ticks
		for tickIndex in range (len(self.xTicks)):
			if (self.xTicks[tickIndex][0] == 'G'):
				self.xTicks[tickIndex][0] = "\\xG\\0"
			
			try:
				outputFile.write ("xaxis  tick major %d, %.6f\n" % (tickIndex, bands.xAxis[int(self.xTicks[tickIndex][1])]))
				outputFile.write ("xaxis  ticklabel %d, \"%s\"\n" % (tickIndex, self.xTicks[tickIndex][0]))
			except IndexError:
				print ('Symmetry point ' + self.xTicks[tickIndex][0] + ' specified as k-point ' + self.xTicks[tickIndex][1] + ' is out of range. Please specify valid k-points.')

	# Configure the sets of data (bands)
	def printTraces (self, outputFile, bands):
		for eachBand in range(bands.nBands):
			outputFile.write ("s%d line linestyle 1\n" % eachBand)
			outputFile.write ("s%d line linewidth 1.5\n" % eachBand)
			outputFile.write ("s%d line color %d\n" % (eachBand, GraceConstants.colors.get('black')))
			outputFile.write ("s%d comment \"Band %d\"\n" % (eachBand,eachBand))
	
	# Configure the bands with character
	def printTracesCharacter (self, outputFile, bands):
			
		for i in range (1, bands.nBands + 1):
			outputFile.write ("read block \"bands_character/band%02i.dat\"\n" % (i))
			for j in range (4):
				outputFile.write ("block xysize \"1:2:%d\"\n" % (j+3))
				outputFile.write ("s%d symbol 1\n" % (4*(i-1) + j))
				outputFile.write ("s%d symbol size 1\n" % (4*(i-1) + j))
				outputFile.write ("s%d symbol color %d\n" % (4*(i-1) + j, j+2))
				outputFile.write ("s%d symbol linewidth 1\n" % (4*(i-1) + j))
				outputFile.write ("s%d symbol skip 0\n" % (4*(i-1) + j))
				if (j == 0):
					outputFile.write ("s%d line type 1\n" % (4*(i-1) + j))
				else:
					outputFile.write ("s%d line type 0\n" % (4*(i-1) + j))			
				outputFile.write ("s%d line linestyle 1\n" % (4*(i-1) + j))
				outputFile.write ("s%d line linewidth 1\n" % (4*(i-1) + j))
				outputFile.write ("s%d line color 7\n" % (4*(i-1) + j))
				outputFile.write ("s%d comment \"Band %d\"\n" % (4*(i-1) + j,i))
				outputFile.write ("s%d legend  \"\"\n" % (4*(i-1) + j))
		
	
	# Configure the bands projected onto the materials
	def printTracesProjected (self, outputFile, bands, projectedBands):
		
		nMaterials = len(projectedBands.dictMaterials)
			
		for i in range (1, bands.nBands + 1):
			outputFile.write ("read block \"bands_projected/band%02i.dat\"\n" % (i))

			for j in range (nMaterials):
				outputFile.write ("block xysize \"1:2:%d\"\n" % (j+3))
				if (j == 0):
					outputFile.write ("s%d symbol 1\n" % (nMaterials*(i-1) + j))
				else:
					outputFile.write ("s%d symbol 6\n" % (nMaterials*(i-1) + j))
				
				outputFile.write ("s%d symbol size 1\n" % (nMaterials*(i-1) + j))
				outputFile.write ("s%d symbol color %d\n" % (nMaterials*(i-1) + j, j+nMaterials))
				outputFile.write ("s%d symbol linewidth 1\n" % (nMaterials*(i-1) + j))
				outputFile.write ("s%d symbol skip 0\n" % (nMaterials*(i-1) + j))
				if (j == 0):
					outputFile.write ("s%d line type 1\n" % (nMaterials*(i-1) + j))
				else:
					outputFile.write ("s%d line type 0\n" % (nMaterials*(i-1) + j))			
				outputFile.write ("s%d line linestyle 1\n" % (nMaterials*(i-1) + j))
				outputFile.write ("s%d line linewidth 1\n" % (nMaterials*(i-1) + j))
				outputFile.write ("s%d line color 7\n" % (nMaterials*(i-1) + j))
				outputFile.write ("s%d comment \"Band %d\"\n" % (nMaterials*(i-1) + j,i))
				outputFile.write ("s%d legend  \"\"\n" % (nMaterials*(i-1) + j))
	
	
	# Configure labels
	def printLabel (self, outputFile):
		outputFile.write ("yaxis  label \"Energy (eV)\"\n")
		outputFile.write ("yaxis  label char size 2.000000\n")
		outputFile.write ("xaxis  label char size 2.000000\n")
		outputFile.write ("yaxis  label font 14\n")
		
	# Exporting PS files from XMGrace
	def printExportPS (self, outputFile, psName):
		outputFile.write ("PRINT TO \"%s.ps\"\n" % psName)
		outputFile.write ("HARDCOPY DEVICE \"PS\"\n")
		outputFile.write ("PRINT\n")
		
		

	'''
	Prints a .bfile for a common band structure
	This method contains all needed settings
	'''
	def printBandStructure (self, bands):
		with open ('bands.bfile', 'w') as outputFile:				
			'''
			Read the file
			'''
			outputFile.write ("READ NXY \"eigenv.dat\" \n")
			
			self.printFontSection (outputFile)
			self.printAxis (outputFile, bands)
			self.printTraces (outputFile, bands)
			self.printLabel (outputFile)
			
			#self.printExportPS (outputFile, 'bands')
	
	'''
	Prints a .bfile for a band structure with character
	This method contains all needed settings
	The variable markerSize specifies the size of the marker while printing the bands
	'''
	def printBandCharacter (self, bands):
		with open ('bandsCharacter.bfile', 'w') as outputFile:				
			'''
			Read the file
			'''
			
			self.printFontSection (outputFile)
			self.printTracesCharacter (outputFile, bands)
			self.printAxis (outputFile, bands)
			self.printLabel (outputFile)
			
			#self.printExportPS (outputFile, 'bandsOrbitals')
	
	'''
	Prints a .bfile for a band structure projected onto the specified materials (file PROJECTION)
	This method contains all needed settings
	'''
	def printBandProjected (self, bands, projectedBands):
		with open ('bandsProjected.bfile', 'w') as outputFile:				
			'''
			Read the file
			'''
			
			self.printFontSection (outputFile)
			self.printTracesProjected (outputFile, bands, projectedBands)
			self.printAxis (outputFile, bands)			
			self.printLabel (outputFile)
			
			#self.printExportPS (outputFile, 'bandsProjected')
