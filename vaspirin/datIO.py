#!/usr/bin/env python
import os, shutil
import numpy as np
from scipy.interpolate import interp1d

class DatFiles (object):
	"""
	Generate .dat files for XMGrace
	The files are generated in the current directory
	"""
	
	def __init__ (self, marker = 0.5):
		"""
		Initializes the datIO interface.
		"""
		
		self.markerSize = float(marker)
		"""
		The size of the symbols
		"""
		
		self.flagINTERPOLATE = False
		"""
		Whether to interpolate or not the values within .dat files
		"""
		
		self.pointsInterpolate = 0
		self.interpolationType = 'cubic'
		"""
		Options for interpolating band structures
		"""
	
	def setInterpolateOptions (self, numberPoints, interpType='cubic'):
		"""
		Method for setting if the datIO interface should or not interpolate
		a certain number of points between the calculated k-points
		"""
		self.pointsInterpolate = numberPoints
		if numberPoints != 0:
			self.flagInterpolate = True
			self.interpolationType = interpType
		else:
			self.flagInterpolate = False
			self.interpolationType = 'linear'
	
	
	def datEigenvals (self, bandStructure, datName='eigenv.dat'):
		"""
		Creates the eigenv.dat file
		Format:
		1st column) normalized k-point (from 0 to 1, derived from the path length)
		2nd column) eigenvalue
		
		Bands are written in sequence and are put together in a same .dat file.
		Different bands are separated by a \n\n
		"""
		
		with open (datName,'w') as outputFile:
			for band in range(bandStructure.nBands):
				
				## The eigenvalues are organized as in bandStructure.eigenvals[k-point][band]
				eigenvals = [kpt[band] for kpt in bandStructure.eigenvals]
				
				## Uses the information we already have to interpolate
				spl = interp1d (bandStructure.xAxis, eigenvals, kind=self.interpolationType)
				
				## Starts writing the .dat file
				## The range starts in 1 to allow linear interpolations within the k-points axis
				for kpoint in range(1, len(bandStructure.xAxis)):
					
					## Checks whether interpolation shall be used
					if self.flagInterpolate:
						
						for interpol_kpt in range (self.pointsInterpolate+1):
							## Interpolates linearly the k-point axis
							t = (interpol_kpt)/(self.pointsInterpolate+1)
							k = ((1-t)*bandStructure.xAxis[kpoint-1] + t*bandStructure.xAxis[kpoint])
							
							## Interpolates the eigenvalues
							E_k = spl(k) - bandStructure.reference
							
							## Writes to the .dat file the interpolated eigenvalues
							outputFile.write ("%.6f % 3.6f\n" % (k, E_k))
					else:
						## Writes to the .dat file only the calculated eigenvalues
						outputFile.write ("%.6f % 3.6f\n" % (bandStructure.xAxis[kpoint-1], bandStructure.eigenvals[kpoint-1][band] - bandStructure.reference))
				
				## Writes the last k-point of the band, which is let behind in the iteration
				outputFile.write ("%.6f % 3.6f\n" % (bandStructure.xAxis[len(bandStructure.xAxis)-1], bandStructure.eigenvals[len(bandStructure.xAxis)-1][band] - bandStructure.reference))
				
				## Ends the band with an additional \n
				outputFile.write ("\n")
	
	def datCharacter (self, bandStructure, bandCharacter):
		"""
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
		"""

		## Creates the bands_character folder, if it does not exists
		try:
			os.mkdir ('bands_character')
		except FileExistsError:
			shutil.rmtree ('bands_character')
			os.mkdir ('bands_character')
		
		## Starts writing the band files
		## Each band receives a .dat file for itself
		for band in range(bandStructure.nBands):
			with open ("bands_character/band%02d.dat" % int(band+1),'w') as outputFile:
				
				## The range starts in 1 to allow linear interpolations within the k-points axis:
				for kpoint in range(1, len(bandStructure.xAxis)):
					
					## Checks whether interpolation shall be used
					if self.flagInterpolate:

						## The eigenvalues are organized as in bandStructure.eigenvals[k-point][band]
						eigenvals = [kpt[band] for kpt in bandStructure.eigenvals]
						
						## Uses the information we already have to interpolate
						spl = interp1d (bandStructure.xAxis, eigenvals, kind=self.interpolationType)
						
						for interpol_kpt in range (self.pointsInterpolate+1):
							## Interpolates linearly the k-point axis
							t = (interpol_kpt)/(self.pointsInterpolate+1)
							k = (1-t)*bandStructure.xAxis[kpoint-1] + t*bandStructure.xAxis[kpoint]
							
							## Interpolates the eigenvalues
							E_k = spl(k) - bandStructure.reference 
							
							## Writes to the .dat file the interpolated eigenvalues
							outputFile.write ("%.6f % 3.6f" % (k, E_k))
							
							## Writes to the .dat file the interpolated contributions
							for i in range(len(bandCharacter.orbitalContributions[kpoint][band])):
								## Interpolates linearly the orbital contributions to be plotted
								contrib = (1-t)*float(bandCharacter.orbitalContributions[kpoint-1][band][i]) + t*float(bandCharacter.orbitalContributions[kpoint][band][i])
								
								contrib *= self.markerSize
								
								## Writes to the .dat file the interpolated contributions
								outputFile.write(" %1.4f" % contrib)
							
							## Finishes writing the current k-point to file
							outputFile.write ("\n")

					else:			
						## Simply writes the eigenvalues to the .dat file
						outputFile.write ("%.6f % 3.6f" % (bandStructure.xAxis[kpoint-1], bandStructure.eigenvals[kpoint-1][band] - bandStructure.reference))
						
						## As well as the contributions
						for contrib in bandCharacter.orbitalContributions[kpoint-1][band]:
							outputFile.write(" %1.4f" % (float(contrib)*self.markerSize))	
						
						## Finishes writing the current k-point to file
						outputFile.write ("\n")
				
				## Print the last k-point
				outputFile.write ("%.6f % 3.6f" % (bandStructure.xAxis[len(bandStructure.xAxis)-1], bandStructure.eigenvals[len(bandStructure.xAxis)-1][band] - bandStructure.reference))
				for contrib in bandCharacter.orbitalContributions[len(bandStructure.xAxis)-1][band]:
					outputFile.write(" %1.4f" % (float(contrib)*self.markerSize))
				outputFile.write ("\n")
				
				## Finishes printing the band					
				outputFile.write ("\n")
		
	
	def datProjected (self, bandStructure, bandCharacter):
		"""
		Creates the bands_projected folder
		Each file in the folder contains the eigenvalues and contributions projected for each band
		
		File formatting:
		1st column) normalized k-point (from 0 to 1, derived from the path length)
		2nd column) eigenvalue
		
		The following columns contain the relative contribution of each material:
		3rd column) contribution of the 1st material
		4th column) contribution of the 2nd material
		... and so on
		"""
		
		## Creates the bands_projected folder, if it does not exists
		try:
			os.mkdir ('bands_projected')
		except FileExistsError:
			shutil.rmtree ('bands_projected')
			os.mkdir ('bands_projected')
		
		## Starts writing the band files
		## Each band receives a .dat file for itself
		for band in range(bandStructure.nBands):
			
			with open ("bands_projected/band%02d.dat" % int(band+1),'w') as outputFile:
				
				## The range starts in 1 to allow linear interpolations within the k-points axis:
				for kpoint in range(1, len(bandStructure.xAxis)):
					
					## Checks whether interpolation shall be used
					if self.flagInterpolate:
						
						## The eigenvalues are organized as in bandStructure.eigenvals[k-point][band]
						eigenvals = [kpt[band] for kpt in bandStructure.eigenvals]
						
						## Uses the information we already have to interpolate
						spl = interp1d (bandStructure.xAxis, eigenvals, kind=self.interpolationType)
						
						
						for interpol_kpt in range (self.pointsInterpolate+1):
							## Interpolates linearly the k-point axis
							t = (interpol_kpt)/(self.pointsInterpolate+1)
							k = (1-t)*bandStructure.xAxis[kpoint-1] + t*bandStructure.xAxis[kpoint]
							
							## Interpolates the eigenvalues
							E_k = spl(k) - bandStructure.reference 
							
							## Writes to the .dat file the interpolated eigenvalues
							outputFile.write ("%.6f % 3.6f" % (k, E_k))
					
							## Writes to the .dat file the interpolated contributions
							for i in range(len(bandCharacter.materialContributions[kpoint-1][band])):
								## Interpolates linearly the orbital contributions to be plotted
								contrib = (1-t)*float(bandCharacter.materialContributions[kpoint-1][band][i]) + t*float(bandCharacter.materialContributions[kpoint][band][i])
							
								contrib *= self.markerSize
								
								## Writes to the .dat file the interpolated contributions
								outputFile.write(" %1.4f" % contrib)
								
							## Finishes writing the current k-point to file
							outputFile.write ("\n")
								
					else:
						## Simply writes the eigenvalues to the .dat file
						outputFile.write ("%.6f % 3.6f" % (bandStructure.xAxis[kpoint-1], bandStructure.eigenvals[kpoint-1][band] - bandStructure.reference))
						
						## As well as the contributions
						for contrib in bandCharacter.materialContributions[kpoint][band]:
							outputFile.write(" %1.4f" % (float(contrib)*self.markerSize))
						
						## Finishes writing the current k-point to file
						outputFile.write ("\n")
				
				# Print last k-point
				outputFile.write ("%.6f % 3.6f" % (bandStructure.xAxis[len(bandStructure.xAxis)-1], bandStructure.eigenvals[len(bandStructure.xAxis)-1][band] - bandStructure.reference))
				for contrib in bandCharacter.materialContributions[len(bandStructure.xAxis)-1][band]:
					outputFile.write(" %1.4f" % (float(contrib)*self.markerSize))
				outputFile.write ("\n")
				
				## Finishes printing the band		
				outputFile.write ("\n")
	
	def datDOS (self, DOS, datName='dos.dat'):
		"""
		Creates the dos.dat file
		
		File formatting:
		1st column) eigenvalue (with respect to a reference)
		2nd column) density of states
		"""
		with open (datName,'w') as outputFile:
			## Print Total DOS
			for i in range(len(DOS.energies)):
				outputFile.write ("% .3f %3.5f\n" % (DOS.energies[i] - DOS.reference, DOS.states[i]))
	
	def datDOSproj (self, DOS, datName='dosProj.dat'):
		"""
		Creates the dosProj.dat file
		
		File formatting:
		1st column) eigenvalue
		2nd column) density of states
		
		DOS from different materials are separated by \n\n
		Total DOS is also included in this file
		"""
		with open (datName,'w') as outputFile:
			## Print Total DOS
			for i in range(len(DOS.energies)):
				outputFile.write ("% .3f %3.5f\n" % (DOS.energies[i] - DOS.reference, DOS.states[i]))
			outputFile.write ("\n")
			
			## Print projected DOS onto materials
			for material in DOS.materialDOS:
				for i in range(material.nEDOS):
					outputFile.write ("% .3f %3.5f\n" % (material.totalDOS[i][0] - DOS.reference, material.totalDOS[i][1]))
				outputFile.write ("\n")
	
	def datDOSorbital (self, DOS, datName='dosOrbital.dat'):
		"""
		Creates the dosProj.dat file
		
		File formatting:
		1st column) eigenvalue
		2nd column) density of states
		
		DOS from different orbitals are separated by \n\n
		Total DOS is also included in this file
		"""
		with open (datName,'w') as outputFile:
			## Print Total DOS
			for i in range(len(DOS.energies)):
				outputFile.write ("% .3f %3.5f\n" % (DOS.energies[i] - DOS.reference, DOS.states[i]))
			outputFile.write ("\n")
			
			orbitalDOS = DOS.orbitalDOS
			
			## Print projected DOS onto orbitals
			for i in range(orbitalDOS.nEDOS):
				## Energy
				outputFile.write ("% .3f" % (orbitalDOS.dos[i][0] - DOS.reference))
				## s orbitals
				outputFile.write (" %3.5f\n" % (orbitalDOS.dos[i][1]))
			outputFile.write ("\n")

			for i in range(orbitalDOS.nEDOS):
				## Energy
				outputFile.write ("% .3f" % (orbitalDOS.dos[i][0] - DOS.reference))
				## px + py orbitals
				outputFile.write (" %3.5f\n" % (orbitalDOS.dos[i][2] + orbitalDOS.dos[i][4]))
			outputFile.write ("\n")

			for i in range(orbitalDOS.nEDOS):
				## Energy
				outputFile.write ("% .3f" % (orbitalDOS.dos[i][0] - DOS.reference))
				## pz orbitals
				outputFile.write (" %3.5f\n" % (orbitalDOS.dos[i][3]))
			outputFile.write ("\n")

			for i in range(orbitalDOS.nEDOS):
				## Energy
				outputFile.write ("% .3f" % (orbitalDOS.dos[i][0] - DOS.reference))
				## d orbitals
				outputFile.write (" %3.5f\n" % (sum(orbitalDOS.dos[i][5:10])))
				
			outputFile.write ("\n")
				
