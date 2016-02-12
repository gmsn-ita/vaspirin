#!/usr/bin/env python

class DatFiles (object):
	'''
	Generate .dat files for XMGrace
	The files are generated in the current directory
	'''
	
	'''
	Set default reference for the eigenvalues
	
	def __init__ (self):
	'''
	
	'''
	Creates the eigenv.dat file
	Format:
	1st column) normalized k-point (from 0 to 1, derived from the path length)
	2nd column) eigenvalue
	'''
	def datEigenvals (self, bandStructure):
		with open ("eigenv.dat",'w') as outputFile:
			for band in range(bandStructure.nBands):
				for kpoint in range(len(bandStructure.xAxis)):
					outputFile.write ("%.6f % 3.6f\n" % (bandStructure.xAxis[kpoint], bandStructure.eigenvals[kpoint][band] - bandStructure.reference))
				outputFile.write ("\n")
	
	'''
	Creates the orbital.dat file
	Format:
	1st column) normalized k-point (from 0 to 1, derived from the path length)
	2nd column) eigenvalue
	
	The following columns contain the relative contribution of each orbital, canonically:
	3rd column) contribution of the s orbitals
	4th column) contribution of the px + py orbitals
	5th column) contribution of the pz orbitals
	6th column) contribution of the d orbitals
	
	Depending on the functions, the contributions of other orbitals, e.g. dz2, may be explicited in other columns
	'''
	def datCharacter (self, bandStructure, bandCharacter):
		with open ("orbital.dat",'w') as outputFile:
			for band in range(bandStructure.nBands):
				for kpoint in range(len(bandStructure.xAxis)):
					outputFile.write ("%.6f % 3.6f" % (bandStructure.xAxis[kpoint], bandStructure.eigenvals[kpoint][band] - bandStructure.reference))
					for contrib in bandCharacter.orbitalContributions[kpoint][band]:
						outputFile.write(" %1.4f" % contrib)
					outputFile.write ("\n")
				outputFile.write ("\n")
	
	'''
	Creates the projected.dat file
	Format:
	1st column) normalized k-point (from 0 to 1, derived from the path length)
	2nd column) eigenvalue
	
	The following columns contain the relative contribution of each material:
	3rd column) contribution of the 1st material
	4th column) contribution of the 2nd material
	... and so on
	'''
	def datProjected (self, bandStructure, bandCharacter):
		with open ("projected.dat",'w') as outputFile:
			for band in range(bandStructure.nBands):
				for kpoint in range(len(bandStructure.xAxis)):
					outputFile.write ("%.6f % 3.6f" % (bandStructure.xAxis[kpoint], bandStructure.eigenvals[kpoint][band] - bandStructure.reference))
					
					for contrib in bandCharacter.materialContributions[kpoint][band]:
						outputFile.write(" %1.4f" % contrib)
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
	
	def setYaxis (self, yMax, yMin):
		self.yMax = yMax
		self.yMin = yMin
	
	'''
	xTicks[index] = ["label string", normalized index from 0 to 1]
	'''
	def setXticks (self, ticksList):
		self.xTicks = ticksList
	
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
		
	def printAxis (self, outputFile):
		outputFile.write ("world %.3f, %.3f, %.3f, %.3f" % (self.xMin, self.yMin, self.xMax, self.yMax))
		
		outputFile.write ("yaxis  tick on \n")
		outputFile.write ("yaxis  tick major 2 \n")
		outputFile.write ("yaxis  tick minor ticks 3 \n")
		
		outputFile.write ("xaxis  tick on \n")
		
		# Writing the symmetry points ticks
		for tickIndex in range (len(self.xTicks)):
			if (self.xTicks[self.xTicks][0] == 'G'):
				self.xTicks[self.xTicks][0] = "\\xG\\0"
		
			outputFile.write ("xaxis  tick major %d, %d\n" % (tickIndex, self.xTicks[self.xTicks][1]))
			outputFile.write ("xaxis  ticklabel %d, \"%s\"\n" % (tickIndex, self.xTicks[self.xTicks][0]))

	
	def printTraces (self, outputFile, bands):
		for eachBand in range(bands.nBands):
			outputFile.write ("s%d line linestyle 1\n" % eachBand)
			outputFile.write ("s%d line linewidth 1.5\n" % eachBand)
			outputFile.write ("s%d line color %d\n" % (eachBand, GraceConstants.colors.get('black')))
			outputFile.write ("s%d comment \"Band %d\"\n" % (eachBand,eachBand))
	
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
			
			self.printFontSection (self, outputFile)
			self.printAxis (self, outputFile)
			self.printTraces (self, outputFile, bands)
			#self.printExportPS (self, outputFile)
		
		
		
		
