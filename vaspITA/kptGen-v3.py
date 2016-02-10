#!/usr/bin/python
# coding: utf-8

## Version created for Python 2
## Automatically create line mode kpoints
## Usage: python kptGen.py NumberKpoints Path

# Daniel S. Koda
# Sep 2015
import re
import numpy as np
import sys
import math

def genKPT(args):
	# Verify number of arguments
	if len(args) < 4:
		print ("Not enough arguments! Please specify:")
		print ("Minimum number of Kpoints and path")


	# kpoints generation specifications for the hexagonal cell
	nKpt = float(args[1])
	path = [args[i] for i in range (2, len(args))]

	# for debugging...
	#nKpt = 10
	#path = ['G', 'K', 'M', 'G']

	G = np.array([0.000, 0.000, 0.000])
	K = np.array([0.667, 0.333, 0.000])
	M = np.array([0.500, 0.000, 0.000])
	H = np.array([0.667, 0.333, 0.500])
	A = np.array([0.000, 0.000, 0.500])
	L = np.array([0.500, 0.000, 0.500])
	Y = np.array([0.000, 0.500, 0.000])
	X = np.array([0.500, 0.000, 0.000])
	S = np.array([0.500, 0.500, 0.000])

	lookup = {"G" : G, "K" : K, "M" : M, "H" : H, "A" : A, "L" : L, "X" : X, "Y" : Y, "S" : S}


	# Creates the path
	xPath = np.array([])
	yPath = np.array([])
	zPath = np.array([])
	symIndex = [0]

	for i in range (1,len(path)):
		# Eliminates redundancy with linspaces
		if (len(xPath) > 0):
			xPath = np.delete (xPath, -1)
			yPath = np.delete (yPath, -1)
			zPath = np.delete (zPath, -1)
		
		# Appends the new path
		xPath = np.concatenate([xPath, np.linspace (lookup.get(path[i-1])[0], lookup.get(path[i])[0], nKpt)])
		yPath = np.concatenate([yPath, np.linspace (lookup.get(path[i-1])[1], lookup.get(path[i])[1], nKpt)])
		zPath = np.concatenate([zPath, np.linspace (lookup.get(path[i-1])[2], lookup.get(path[i])[2], nKpt)])

	# Write path to file
	with open ("KPOINTS_gen", 'w') as output_file:
		output_file.write ('Points = ')
		for i in range(len(path)):
			output_file.write ("%s " % path[i])

		output_file.write (', Index = ')
		for i in range(len(symIndex)):
			output_file.write ("%d " % symIndex[i])

		output_file.write (', Hexagonal\n')
		output_file.write ('%d\n' % len(xPath))
		output_file.write ('Reciprocal lattice\n')

		kptWeight = 1.0

		for i in range (len(xPath)):
			output_file.write ("%.15f    %.15f    %.15f    %.4f\n" % (xPath[i], yPath[i], zPath[i], kptWeight))

