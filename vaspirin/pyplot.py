#!/usr/bin/env python
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
import numpy as np
import scipy
import pylab as pl
from itertools import cycle


def plotBS(bsData,figureName):
	bsData.setReference(bsData.eFermi)
	for k1 in range(bsData.nBands):
		band=[]
		for k2 in range(len(bsData.xAxis)):
			band.append(bsData.eigenvals[k2][k1]-bsData.reference)
		pl.plot(bsData.xAxis,band,'k')

	#Setting plot
	pl.xlim(min(bsData.xAxis), max(bsData.xAxis))
	pl.ylim(-6, 6)
	pl.xlabel(r'High Symmetry Path',fontsize=16)
	pl.ylabel(r'E - E$_F$ (eV)',fontsize=16)
	pl.tick_params(axis='x',      labelbottom='off')
	pl.plot([min(bsData.xAxis), max(bsData.xAxis)],[0,0],'k--')
	pl.savefig(figureName)
	return 0

def plotDOS(dosData,figureName):
	dosData.setReference(dosData.eFermi)
	xaxis=[]
	for e in dosData.energies:
		xaxis.append(e-dosData.reference) 
	pl.plot(xaxis,dosData.states,'k')	
	#Setting plot
	pl.xlim(min(dosData.energies), max(dosData.energies))
	plt.ylim(0, 1.2*max(dosData.states))
	pl.xlabel(r'E - E$_F$ (eV)',fontsize=16)
	pl.ylabel('Density of states (a.u.)',fontsize=16)
	pl.plot([0,0],[min(dosData.states), 1.2*max(dosData.states)],'k--')
	pl.savefig(figureName)
	return 0


def plotBSDOS(bsData,dosData,figureName):
	plt.figure(1)
	#PLOT 121 = BS
	plt.subplot(121)
	#Setting plot 1
	plt.tick_params(axis='x',      labelbottom='off')
	plt.xlim(min(bsData.xAxis), max(bsData.xAxis))
	plt.ylim(min(dosData.energies), max(dosData.energies))
	plt.xlabel(r'High Symmetry Path',fontsize=16)
	plt.ylabel(r'E - E$_F$ (eV)',fontsize=16)
	plt.plot([min(bsData.xAxis), max(bsData.xAxis)],[0,0],'k--')



	bsData.setReference(bsData.eFermi)
	for k1 in range(bsData.nBands):
		band=[]
		for k2 in range(len(bsData.xAxis)):
			band.append(bsData.eigenvals[k2][k1]-bsData.reference)
		pl.plot(bsData.xAxis,band,'k')


	#PLOT 122 = DOS
	plt.subplot(122)
	dosData.setReference(dosData.eFermi)
	EnergyAxis=[]
	for e in dosData.energies:
		EnergyAxis.append(e-dosData.reference) 

	#Setting plot 2
	plt.ylim(min(dosData.energies), max(dosData.energies))
	plt.xlim(0, 1.2*max(dosData.states))
	plt.xlabel('Density of states (a.u.)',fontsize=16)
	plt.tick_params(axis='y',      labelleft='off')
	plt.plot([min(dosData.states), 1.2*max(dosData.states)],[0,0],'k--')
	pl.plot(dosData.states,EnergyAxis,'k')

	#OUTPUT
	plt.savefig(figureName)
	return 0



def plotBSCHAR(bsData,procarData,figureName):


	return 0

