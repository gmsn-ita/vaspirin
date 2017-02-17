
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
	
	symbols = {
	"none" : 0,
	"circle" : 1,
	"square" : 2,
	"diamond" : 3,
	"triangle-up" : 4,
	"triangle-left" : 5,
	"triangle-down" : 6,
	"triangle-right" : 7,
	"plus" : 8,
	"x" : 9,
	"star" : 10,
	"char" : 11
	}
	
	line_style = {
	"none" : 0,
	"solid" : 1,
	"dotted" : 2,
	"dashed" : 3,
	"long-dashed" : 4,
	"dash-dot" : 5,
	"long-dash-dot" : 6,
	"dash-dot-dot" : 7,
	"dash-dash-dot" : 8
	}
	
	dosView = [0.150000, 0.550000, 1.150000, 0.850000]
	bandsView = [0.150000, 0.150000, 1.150000, 0.850000]
	
class Grace (object):
	"""
	Generate files with extension .bfile
	Each one of these files is a XMGrace batch for the chosen option
	"""
	
	def __init__ (self):
		"""
		Set the initial conditions for the XMGrace configuration
		"""
		self.setDefaultParameters() 

	def setDefaultParameters(self):
		"""
		Default parameters for the plots
		"""
		
		self.yMax = 3
		"""
		The maximum value to be represented on the y axis
		"""
		
		self.yMin = -3
		"""
		The minimum value to be represented on the y axis
		"""
		
		self.xMax = 1
		"""
		The maximum value to be represented on the x axis
		"""
		
		self.xMin = 0
		"""
		The minimum value to be represented on the x axis
		"""
		
		self.xTicks = []
		"""
		The ticks to be represented in the x axis
		"""
		
		self.title = ""
		"""
		The plot title
		"""
		
		self.subtitle = ""
		"""
		The plot subtitle
		"""
		
		self.font = "optima"
		"""
		The plot default font
		"""
		
		self.exportPS = False
		"""
		Option to export directly to postscript or not
		"""
		
		self.psFilename = 'bands'
		"""
		Postscript filename
		"""
		
		self.orbitalColors = {
		0 : GraceConstants.colors.get('red'), ## s orbital (0): red
		1 : GraceConstants.colors.get('green'), ## px+py orbitals (1): green
		2 : GraceConstants.colors.get('blue'), ## pz orbitals (2): blue
		3 : GraceConstants.colors.get('magenta') ## d orbitals (3): magenta
		}
		"""
		Dictionary containing the standard information for projected orbitals
		"""
		
		self.projectedColors = {}
		"""
		Dictionary containing the standard information for projected onto atomic sites.
		By default, it is set as empty and should be entered by the user. If not, the sequential colors will be used
		"""
		
		self.boolSymbolFill = False
		"""
		Boolean variable to set whether the symbols are or not filled
		"""
		
		self.view = GraceConstants.bandsView
		"""
		Standard view for the XMGrace plot
		"""
	
	def setYaxis (self, yMin, yMax):
		"""
		Default y axis parameters for the plots
		"""
		self.yMax = yMax
		self.yMin = yMin
	
	def setXaxis (self, xMin, xMax):
		"""
		Default x axis parameters for the plots
		"""
		self.xMax = xMax
		self.xMin = xMin
	
	
	def setXticks (self, ticksList):
		"""
		xTicks[index] = ["label string", normalized index from 0 to 1]
		"""
		self.xTicks = ticksList
	
	def readXticks (self, fKpoints):
		"""
		Read k-points ticks labels in the KPOINTS header
		
		KPOINTS header format: KPT_1 index_1, KPT_2 index_2 ...
		Example G 1, M 20, K 40, G 60
		"""

		ticks = []
		try:
			with open (fKpoints, 'r') as fileIn:
				firstLine = fileIn.readline()
				symKpt = firstLine.strip('\n').split(',')
				for eachKpt in symKpt:
					l = eachKpt.split(' ')
					l = [i for i in l if i] # strips whitespace
					ticks.append ([l[0], l[1]])
					
		except FileNotFoundError:
			print ("KPOINTS file not found! Exiting...\n")
			sys.exit (1)
		
		self.setXticks (ticks)
		
	def setTitle (self, titleString):
		"""
		Set plot title
		"""
		self.title = titleString
		
	def setSubtitle (self, subtitleString):
		"""
		Set plot subtitle
		"""
		self.subtitle = subtitleString
		
	def setProjectedColors (self, projectedColors):
		"""
		Set colors from PROJECTION files
		"""
		self.projectedColors = projectedColors
	
	def setSymbolFill (self, boolSymbolFill):
		"""
		Set whether or not the symbol fill is set
		"""
		self.boolSymbolFill = boolSymbolFill
	
	def setView (self, view):
		"""
		Set whether or not the symbol fill is set
		"""
		self.view = view

	def printView (self, outputFile):
		"""
		Print the plotting area (view) for XMGrace
		"""
		outputFile.write ("view %.6f, %.6f, %.6f, %.6f\n" % (self.view[0], self.view[1], self.view[2], self.view[3]))
		
		
	def printFontSection (self, outputFile):
		"""
		Font section
		"""		
		outputFile.write ("map font %d to \"Optima\", \"Optima\" \n" % GraceConstants.fonts.get('optima'))
		outputFile.write ("title font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("subtitle font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("legend font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("xaxis label font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("xaxis ticklabel font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("yaxis label font %d \n" % GraceConstants.fonts.get(self.font))
		outputFile.write ("yaxis ticklabel font %d \n" % GraceConstants.fonts.get(self.font))
		
	def printAxis (self, outputFile, bands):
		"""
		Defines the axis for the plot
		"""
		## Defining XY axis
		outputFile.write ("world %.3f, %.3f, %.3f, %.3f \n" % (self.xMin, self.yMin, self.xMax, self.yMax))
		
		## Y ticks settings
		outputFile.write ("yaxis  tick on \n")
		outputFile.write ("yaxis  tick major 1 \n")
		outputFile.write ("yaxis  tick minor ticks 3 \n")
		outputFile.write ("yaxis  tick major size 1.000000\n")
		outputFile.write ("yaxis  ticklabel char size 1.500000\n")
		
		## Enable symmetry points in the X axis
		outputFile.write ("xaxis  tick on \n")
		outputFile.write ("xaxis  tick spec type both \n")
		outputFile.write ("xaxis  tick spec %d \n" % len(self.xTicks))
		outputFile.write ("xaxis  ticklabel char size 1.500000\n")
		
		## Symmetry points have vertical dashed lines
		outputFile.write ("xaxis  tick major linestyle 4 \n")
		outputFile.write ("xaxis  tick major grid on \n")
		

		## Writing the symmetry points ticks
		for tickIndex in range (len(self.xTicks)):
			if (self.xTicks[tickIndex][0] == 'G'):
				self.xTicks[tickIndex][0] = "\\xG\\0"
			
			try:
				outputFile.write ("xaxis  tick major %d, %.6f\n" % (tickIndex, bands.xAxis[int(self.xTicks[tickIndex][1])]))
				outputFile.write ("xaxis  ticklabel %d, \"%s\"\n" % (tickIndex, self.xTicks[tickIndex][0]))
			except IndexError:
				print ('Symmetry point ' + self.xTicks[tickIndex][0] + ' specified as k-point ' + self.xTicks[tickIndex][1] + ' is out of range. Please specify valid k-points.')

	def printDOSAxis (self, outputFile):
		"""
		Defines the axis for the plot
		"""
		## Defining XY axis
		outputFile.write ("world %.3f, %.3f, %.3f, %.3f \n" % (self.xMin, self.yMin, self.xMax, self.yMax))
		
		## Y ticks settings
		outputFile.write ("yaxis  tick on \n")
		outputFile.write ("yaxis  tick major 10 \n")
		outputFile.write ("yaxis  tick minor ticks 1 \n")
		outputFile.write ("yaxis  tick major size 1.000000\n")
		outputFile.write ("yaxis  ticklabel char size 1.500000\n")
		
		## Enable symmetry points in the X axis
		outputFile.write ("xaxis  tick on \n")
		outputFile.write ("xaxis  tick major 1 \n")
		outputFile.write ("xaxis  tick minor ticks 1 \n")
		outputFile.write ("xaxis  tick major size 1.000000\n")
		outputFile.write ("xaxis  ticklabel char size 1.500000\n")
		
		
	def printTraces (self, outputFile, bands, traceColor='black', firstBand=0):
		"""
		Configure the sets of data (bands)
		
		The firstBand variable defines the first band to be plotted, which is
		useful in case of concatenating band structures or to simply reduce the
		use of memory when rendering figures.
		"""
		for eachBand in range(firstBand, bands.nBands + firstBand):
			outputFile.write ("s%d line linestyle %d\n" % (eachBand, GraceConstants.line_style.get("solid")))
			outputFile.write ("s%d line linewidth 1.5\n" % eachBand)
			outputFile.write ("s%d line color %d\n" % (eachBand, GraceConstants.colors.get(traceColor)))
			outputFile.write ("s%d comment \"Band %d\"\n" % (eachBand,eachBand))
	
	
	def printTracesCharacter (self, outputFile, bands):
		"""
		Configure the bands with character
		"""
		
		## We have nBands .dat files containing the information needed
		for i in range (1, bands.nBands + 1):
			outputFile.write ("read block \"bands_character/band%02i.dat\"\n" % (i))
			
			## In this case, 4 is the number of projected orbitals:
			## s, px+py, +z, d
			## In the future, this might be changed to include personalized orbital projection
			nOrbitals = 4
			 
			for j in range (nOrbitals):
				
				## Number of the trace in the XMGrace description
				traceNumber = nOrbitals*(i-1) + j
				
				## Select the column regarding the orbital contribution
				outputFile.write ("block xysize \"1:2:%d\"\n" % (j+3))
				
				## Select the symbol circle to the band
				outputFile.write ("s%d symbol %d\n" % (traceNumber,GraceConstants.symbols.get("circle")))
				
				## Select symbol size for the trace
				outputFile.write ("s%d symbol size 1\n" % (traceNumber))
				
				## Fill of the marker: solid or none
				if self.boolSymbolFill:
					outputFile.write ("s%d symbol fill pattern 1\n" % (traceNumber))
				else:
					outputFile.write ("s%d symbol fill pattern 0\n" % (traceNumber))
					
				## The color is defined according to the orbital represented
				## The dictionary self.orbitalColors can be personalized
				outputFile.write ("s%d symbol color %d\n" % (traceNumber, self.orbitalColors.get(j)))
				outputFile.write ("s%d symbol fill color %d\n" % (traceNumber, self.orbitalColors.get(j)))
					
				## The linewidth is defined, as well as the skip symbol attribute
				outputFile.write ("s%d symbol linewidth 1\n" % traceNumber)
				outputFile.write ("s%d symbol skip 0\n" % traceNumber)
				
				## Writes only one trace putting the bands together for each band
				## If this is not set, the line is written four times, which is unnecessary
				## and memory-consuming.
				if (j == 0):
					outputFile.write ("s%d line type 1\n" % traceNumber)
				else:
					outputFile.write ("s%d line type 0\n" % traceNumber)	
					
				## Configurations for the trace line
				outputFile.write ("s%d line linestyle %d\n" % (traceNumber,GraceConstants.line_style.get("solid")))
				outputFile.write ("s%d line linewidth 1\n" % traceNumber)
				
				## The trace line in the case of the projected bands is light gray
				outputFile.write ("s%d line color %d\n" % (traceNumber,GraceConstants.colors.get('gray')))
				
				outputFile.write ("s%d comment \"Band %d\"\n" % (traceNumber,i))
				outputFile.write ("s%d legend  \"\"\n" % traceNumber)
		
	
	def printTracesProjected (self, outputFile, bands, projectedBands):
		"""
		Configure the bands projected onto the materials
		"""
		
		## Discover how many materials we have to project onto
		nMaterials = len(projectedBands.prj.dictMaterials)
			
		for i in range (1, bands.nBands + 1):
			## We have nBands .dat files containing the information needed
			outputFile.write ("read block \"bands_projected/band%02i.dat\"\n" % (i))
			
			## In this case, nMaterials is the number of projected sites:
			for j in range (nMaterials):
				## Number of the trace in the XMGrace description
				
				traceNumber = nMaterials*(i-1) + j
				
				## Read the columns which represent the projection 
				outputFile.write ("block xysize \"1:2:%d\"\n" % (j+3))
				
				## All projected symbols are set as a circle (symbol 1)
				## This might be personalized later
				outputFile.write ("s%d symbol %d\n" % (traceNumber,GraceConstants.symbols.get("circle")))
				
				## Size of the marker
				outputFile.write ("s%d symbol size 1\n" % (traceNumber))
				
				## Fill of the marker: solid or none
				if self.boolSymbolFill:
					outputFile.write ("s%d symbol fill pattern 1\n" % (traceNumber))
				else:
					outputFile.write ("s%d symbol fill pattern 0\n" % (traceNumber))
				
				
				## Color for the symbol
				## The projectedColors dictionary may be customized according to the
				## projection file input. If it is not customized, simply use the sequential colors
				## to represent the data
				if len(self.projectedColors) == nMaterials:
					matColor = self.projectedColors.get(j)
					outputFile.write ("s%d symbol color %d\n" % (traceNumber, GraceConstants.colors.get(matColor.lower())))
					outputFile.write ("s%d symbol fill color %d\n" % (traceNumber, GraceConstants.colors.get(matColor.lower())))
				else:
					## Customize so that the first color is red
					outputFile.write ("s%d symbol color %d\n" % (traceNumber, j+2))
					outputFile.write ("s%d symbol fill color %d\n" % (traceNumber, j+2))
				
				## Linewidth and skip configurations
				outputFile.write ("s%d symbol linewidth 1\n" % (traceNumber))
				outputFile.write ("s%d symbol skip 0\n" % (traceNumber))
				
				## Writes the trace only once per band
				## If this option does not exist, `nMaterials` lines are traced
				if (j == 0):
					outputFile.write ("s%d line type 1\n" % (traceNumber))
				else:
					outputFile.write ("s%d line type 0\n" % (traceNumber))
				
				
					
				## A few more configurations about the line plotted	
				outputFile.write ("s%d line linestyle %d\n" % (traceNumber,GraceConstants.line_style.get("solid")))
				outputFile.write ("s%d line linewidth 1\n" % (traceNumber))
				outputFile.write ("s%d line color %d\n" % (traceNumber, GraceConstants.colors.get('gray')))
				outputFile.write ("s%d comment \"Band %d\"\n" % (traceNumber,i))
				outputFile.write ("s%d legend  \"\"\n" % (traceNumber))

	def printDOS (self, outputFile, dos, traceColor='black'):
		"""
		Plot the total density of states
		"""
		outputFile.write ("s0 line linestyle %d\n" % (GraceConstants.line_style.get("solid")))
		outputFile.write ("s0 line linewidth 1.0\n")
		outputFile.write ("s0 line color %d\n" % (GraceConstants.colors.get(traceColor)))
		#~ outputFile.write ("s0 legend \"Total DOS\"\n")
		outputFile.write ("s0 baseline type 0\n")
		
		outputFile.write ("s0 fill rule 0\n")
		outputFile.write ("s0 fill color %d\n" % (GraceConstants.colors.get(traceColor)))
		outputFile.write ("s0 fill pattern 1\n")
		
		if self.boolSymbolFill:
			outputFile.write ("s0 fill type 2\n")
		else:
			outputFile.write ("s0 fill type 0\n")

	
	def printDOSCharacter (self, outputFile, dos):
		"""
		Configure the density of states projected onto atomic orbitals
		"""
		
		self.printDOS (outputFile, dos, traceColor='gray')
		
		## In this case, 4 is the number of projected orbitals:
		## s, px+py, +z, d
		## In the future, this might be changed to include personalized orbital projection
		nOrbitals = 4
		 
		for j in range (1, nOrbitals+1):
			
			outputFile.write ("s%d line linestyle %d\n" % (j, GraceConstants.line_style.get("solid")))
			outputFile.write ("s%d line linewidth 1.0\n" % j)
			outputFile.write ("s%d line color %d\n" % (j, self.orbitalColors.get(j-1)))
			#~ outputFile.write ("s%d legend \"Total DOS\"\n" % j)
			outputFile.write ("s%d baseline type 0\n" % j)
			
			outputFile.write ("s%d fill rule 0\n" % j)
			outputFile.write ("s%d fill color %d\n" % (j, self.orbitalColors.get(j-1)))
			outputFile.write ("s%d fill pattern 1\n" % j)
			
			if self.boolSymbolFill:
				outputFile.write ("s%d fill type 2\n" % j)
			else:
				outputFile.write ("s%d fill type 0\n" % j)
					
	
	def printDOSProjected (self, outputFile, dos):
		"""
		Configure the bands projected onto the materials
		"""
		
		self.printDOS (outputFile, dos, traceColor='gray')
		
		## Discover how many materials we have to project onto
		nMaterials = len(dos.prj.dictMaterials)
		
		for j in range (1, nMaterials+1):
			
			outputFile.write ("s%d line linestyle %d\n" % (j, GraceConstants.line_style.get("solid")))
			outputFile.write ("s%d line linewidth 1.0\n" % j)
			#~ outputFile.write ("s%d legend \"Total DOS\"\n" % j)
			outputFile.write ("s%d baseline type 0\n" % j)
			
			outputFile.write ("s%d fill rule 0\n" % j)
			
			outputFile.write ("s%d fill pattern 1\n" % j)
			
			## Color for the symbol
			## The projectedColors dictionary may be customized according to the
			## projection file input. If it is not customized, simply use the sequential colors
			## to represent the data
			if len(self.projectedColors) == nMaterials:
				matColor = self.projectedColors.get(j-1)
				outputFile.write ("s%d fill color %d\n" % (j, GraceConstants.colors.get(matColor.lower())))
				outputFile.write ("s%d line color %d\n" % (j, GraceConstants.colors.get(matColor.lower())))
			else:
				## Customize so that the first color is red
				outputFile.write ("s%d fill color %d\n" % (j, j+1))
				outputFile.write ("s%d line color %d\n" % (j, j+1))
			
			if self.boolSymbolFill:
				outputFile.write ("s%d fill type 2\n" % j)
			else:
				outputFile.write ("s%d fill type 0\n" % j)

	
	def printLabel (self, outputFile):
		"""
		Configure labels
		"""
		outputFile.write ("yaxis  label \"Energy (eV)\"\n")
		outputFile.write ("yaxis  label char size 2.000000\n")
		outputFile.write ("xaxis  label char size 2.000000\n")
	
	def printDOSLabel (self, outputFile):
		"""
		Configure labels
		"""
		outputFile.write ("yaxis  label \"DOS (a.u.)\"\n")
		outputFile.write ("yaxis  label char size 2.000000\n")
		outputFile.write ("xaxis  label \"Energy (eV)\"\n")
		outputFile.write ("xaxis  label char size 2.000000\n")
		
	def printExportPS (self, outputFile, psName):
		"""
		Exporting PS files from XMGrace
		"""
		outputFile.write ("PRINT TO \"%s.ps\"\n" % psName)
		outputFile.write ("HARDCOPY DEVICE \"PS\"\n")
		outputFile.write ("PRINT\n")

	
	def printLine (self, outputFile, tick, traceColor='black', firstBand=0):
		"""
		Configure the sets of data (bands)
		
		The firstBand variable defines the first band to be plotted, which is
		useful in case of concatenating band structures or to simply reduce the
		use of memory when rendering figures.
		"""
		for eachBand in range(firstBand, bands.nBands + firstBand):
			outputFile.write ("s%d line linestyle %d\n" % (eachBand, GraceConstants.line_style.get("solid")))
			outputFile.write ("s%d line linewidth 1.5\n" % eachBand)
			outputFile.write ("s%d line color %d\n" % (eachBand, GraceConstants.colors.get(traceColor)))
			outputFile.write ("s%d comment \"Band %d\"\n" % (eachBand,eachBand))
