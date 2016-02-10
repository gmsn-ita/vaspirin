#!/usr/bin/env python

class Grace (object):
	'''
	Deals with plotting and generating XMGrace files
	A set of parameters should be supplied to write the file
	'''

	def __init__ (self):
		self.yMax = 3
		self.yMin = -3
		self.xMax = 1
		self.xMin = 0
		self.xTicks = []
	
	def datEigenvals (self, bandStructure):
		with open ("eigenv.dat",'w') as outputFile:
			for band in range(bandStructure.nBands):
				for kpoint in range(len(bandStructure.xAxis)):
					outputFile.write ("%.6f % 3.6f\n" % (bandStructure.xAxis[kpoint], bandStructure.eigenvals[kpoint][band]))
				outputFile.write ("\n")
