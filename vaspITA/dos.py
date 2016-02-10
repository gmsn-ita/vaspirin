#!/usr/bin/env python

class DOS (object):
	def __init__(self,fDoscar):
		self.NEDOS=self.readNEDOS(fDoscar)
		self.eFermi=self.readEFermi(fDoscar)
		self.energies=self.readEnergies(fDoscar)
		self.states=self.readStates(fDoscar)
		self.projDOS=self.readProjDOS(fDoscar)	
			

	def readNEDOS(fDoscar):
		fileIn=open(fDoscar,'r')
		nedos=int(fileIn.read().split('\n')[5].split()[2])
		fileIn.close()		
		return nedos

	def readEFermi(fDoscar):
		fileIn=open(fDoscar,'r')
		ef=int(fileIn.read().split('\n')[5].split()[3])
		fileIn.close()		
		return ef

	def readEnergies(fDoscar):
		fileIn=open(fDoscar,'r')
		doscar=fileIn.read()
		energies=[]
		
		lines=doscar.split('\n')
		for k in range(6,5+self.NEDOS):
			energies.append( float(lines[k].split()[0]) )
		fileIn.close()

		return energies


	def readStates(fDoscar):
		fileIn=open(fDoscar,'r')
		doscar=fileIn.read()
		states=[]
		
		lines=doscar.split('\n')
		for k in range(6,5+self.NEDOS):
			states.append( float(lines[k].split()[1]) )
		fileIn.close()
		return states


	def readProjDOS(fDoscar):
		return 0


