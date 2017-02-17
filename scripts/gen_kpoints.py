#!/usr/bin/python
# coding: utf-8

import re
import numpy as np
import sys
import math
import argparse

class SymmetryDatabase (object):
	"""
	Class with specifications of symmetry points from various lattices.
	Information taken from: W. Setyawan, S. Curtarolo / Computational Materials Science 49 (2010) 299–312
	The terminology is also taken from this article
	"""
	
	cub = {
		'G' : np.array([0, 0, 0], dtype=np.float),
		'M' : np.array([1/2, 1/2, 0], dtype=np.float),
		'R' : np.array([1/2, 1/2, 1/2], dtype=np.float),
		'X' : np.array([0, 1/2, 0], dtype=np.float),
		}
	'''
	Cubic lattice
	'''
	
	fcc = {
		'G' : np.array([0, 0, 0], dtype=np.float),
		'K' : np.array([3/8, 3/8, 3/4], dtype=np.float),
		'L' : np.array([1/2, 1/2, 1/2], dtype=np.float),
		'U' : np.array([5/8, 1/4, 5/8], dtype=np.float),
		'W' : np.array([1/2, 1/4, 3/4], dtype=np.float),
		'X' : np.array([1/2, 0, 1/2], dtype=np.float),
		}
	'''
	Face-centered lattice
	'''

	bcc = {
		'G' : np.array([0, 0, 0], dtype=np.float),
		'P' : np.array([1/4, 1/4, 1/4], dtype=np.float),
		'H' : np.array([1/2, -1/2, 1/2], dtype=np.float),
		'N' : np.array([0, 0, 1/2], dtype=np.float),
		}
	'''
	Body-centered lattice
	'''
	
	tet = {
		'G' : np.array([0, 0, 0], dtype=np.float),
		'M' : np.array([1/2, 1/2, 0], dtype=np.float),
		'A' : np.array([1/2, 1/2, 1/2], dtype=np.float),
		'Z' : np.array([0, 0, 1/2], dtype=np.float),
		'X' : np.array([0, 1/2, 0], dtype=np.float),
		'R' : np.array([0, 1/2, 1/2], dtype=np.float),
		}
	'''
	Tetragonal lattice
	'''
	
	ort = {
		'G' : np.array([0, 0, 0], dtype=np.float),
		'R' : np.array([1/2, 1/2, 1/2], dtype=np.float),
		'S' : np.array([1/2, 1/2, 0], dtype=np.float),
		'T' : np.array([0, 1/2, 1/2], dtype=np.float),
		'U' : np.array([1/2, 0, 1/2], dtype=np.float),
		'X' : np.array([1/2, 0, 0], dtype=np.float),
		'Y' : np.array([0, 1/2, 0], dtype=np.float),
		'Z' : np.array([0, 0, 1/2], dtype=np.float),
		}
	'''
	Orthorhombic lattice
	'''

	hex120deg = {
		'G' : np.array([0, 0, 0], dtype=np.float),
		'A' : np.array([0, 0, 1/2], dtype=np.float),
		'H' : np.array([1/3, 1/3, 1/2], dtype=np.float),
		'K' : np.array([1/3, 1/3, 0], dtype=np.float),
		'M' : np.array([1/2, 0, 0], dtype=np.float),
		'L' : np.array([1/2, 0, 1/2], dtype=np.float),
		}
	'''
	Hexagonal lattice (120 deg between direct lattice vectors)
	'''
	
	hex60deg = {
		'G' : np.array([0, 0, 0], dtype=np.float),
		'A' : np.array([0, 0, 1/2], dtype=np.float),
		'H' : np.array([2/3, 1/3, 1/2], dtype=np.float),
		'K' : np.array([2/3, 1/3, 0], dtype=np.float),
		'M' : np.array([1/2, 0, 0], dtype=np.float),
		'L' : np.array([1/2, 0, 1/2], dtype=np.float),
		}
	'''
	Hexagonal lattice (120 deg between direct lattice vectors)
	'''
	
	lattices = {
		'cub' : cub,
		'fcc' : fcc,
		'bcc': bcc,
		'hex120deg' : hex120deg,
		'hex60deg' : hex60deg,
		'ort' : ort,
		'tet' : tet,
	}
	'''
	A dictionary of all lattices implemented
	'''
	
	
def parseArgs():
	"""
	Parse arguments from the command line. Uses the `argparse` package to
	establish all positional and optional arguments.
	"""
	parser = argparse.ArgumentParser(description='Generate KPOINTS files with personalized options.',
									epilog= "Written by Daniel S. Koda (feb. 2017).",
									prog="gen_kpoints.py")

	parser.add_argument('kpt_path', nargs='+', help="Path of symmetry points")
	
	parser.add_argument('-o', '--output', default='KPOINTS_gen', help="output name for the generated files. Default: KPOINTS_gen")
	
	parser.add_argument('-n', '--number', type=int, default=10, help="number of k-points between symmetry points (default: 10)")
	
	parser.add_argument('-p', '--proportional', action='store_true', help="create a path with a number of k-points between symmetry points proportional to the path length (requires an OUTCAR file)")
	
	parser.add_argument('-i', '--ibzkpt', action='store_true',
					help="import a IBZKPT file to put before the document. Useful for preparing HSE06 calculations")
	
	parser.add_argument('-l', '--lattice', choices=list(SymmetryDatabase.lattices.keys()), default='hex60deg', help="lattice type (default: hex60deg)")
	
	parser.add_argument('-w', '--weight', type=float, default=1.0, help="weight of the k-points created (Default: 1)")
	
	parser.add_argument('-q', '--quiet', action='store_true', help="do not display text on the output window (default: False)")
	
	return parser.parse_args()

def printRunDescription (args):
	'''
	Print description of the options chosen and the crystals input.
	'''
	
	leftJustSpace = 20
	print ("output file:".ljust(leftJustSpace) + "%s" % args.output)
	print ("Bravais lattice:".ljust(leftJustSpace) + "%s" % args.lattice)
	print ("path:".ljust(leftJustSpace) + ' '.join(args.kpt_path))	
	print ("number of k-points:".ljust(leftJustSpace) + "%d" % args.number)
	print ("k-points weight:".ljust(leftJustSpace) + "%2.1f" % args.weight)
	print ("proportional?".ljust(leftJustSpace) + ("yes (requires OUTCAR)" if args.proportional else "no"))
	print ("include IBZKPT?".ljust(leftJustSpace) + ("yes" if args.ibzkpt else "no"))

def genKPT (args):
	'''
	Generates KPOINTS file based on the requested properties
	'''
	
	## Importing properties
	path = args.kpt_path
	nKpt = args.number

	## Creates the path
	xPath = np.array([])
	yPath = np.array([])
	zPath = np.array([])
	symIndex = [0]

	pathDict = SymmetryDatabase.lattices.get(args.lattice)

	## If the option to merge with a IBZKPT file is set, then import this file fist
	if args.ibzkpt:
		with open ("IBZKPT", 'r') as ibzkpt_file:
			ibzkpt_file.readline() # Throws away the comment line
			n_ibzkpt = int (ibzkpt_file.readline().strip())
			ibzkpt_file.readline() # Throws away the "Reciprocal lattice" line
			
			## Read all k-points and throw away blank space
			ibzkpt_kpoints = ""
			for i in range (n_ibzkpt):
				ibzkpt_kpoints += ibzkpt_file.readline()
			
			
	## Read the reciprocal vectors from OUTCAR to create a proportional path
	if args.proportional:
		info = []
		with open("OUTCAR", 'r') as input_file:
			found_vectors = 0;
			i=0;
			for line in input_file:
				if found_vectors:
					info.append (re.split(' +', line.rstrip('\n')))
					i += 1;
				if "reciprocal lattice vectors" in line:
					found_vectors = 1;
				if i == 3:
					break;
		
		## Reciprocal lattice vectors
		vec = [[float(info[i][-3]), float(info[i][-2]), float(info[i][-1])] for i in range (3)]
		## Reciprocal lattice vectors norm
		recVec = np.array([np.linalg.norm(vec[i]) for i in range (3)])
		
		## Creates a step proportional to the minimum distance between two points
		minDistance = min([np.linalg.norm(pathDict.get(path[i-1]) * recVec - pathDict.get(path[i]) * recVec) for i in range(1,len(path))])
		kStep = minDistance/nKpt
				
				
	for i in range (1,len(path)):
		## Avoid calculations with two sequential points
		if (len(xPath) > 0):
			xPath = np.delete (xPath, -1)
			yPath = np.delete (yPath, -1)
			zPath = np.delete (zPath, -1)
		
		## Decides how many points will be created between symmetry points
		if args.proportional:
			nPoints = math.ceil(np.linalg.norm(pathDict.get(path[i-1]) * recVec - pathDict.get(path[i]) * recVec)/kStep)
		else:
			nPoints = nKpt
		
		symIndex = symIndex + [symIndex[-1] + nPoints - 1]
		
		## Appends the new path
		xPath = np.concatenate([xPath, np.linspace (pathDict.get(path[i-1])[0], pathDict.get(path[i])[0], nPoints)])
		yPath = np.concatenate([yPath, np.linspace (pathDict.get(path[i-1])[1], pathDict.get(path[i])[1], nPoints)])
		zPath = np.concatenate([zPath, np.linspace (pathDict.get(path[i-1])[2], pathDict.get(path[i])[2], nPoints)])

	## Write path to file
	with open (args.output, 'w') as output_file:
		
		## Plot the comment, which is useful for plotting with XMGrace
		for i in range(len(path)):
			output_file.write ("%s %d" % (path[i],symIndex[i]))
			
			if i != len(path) - 1:
				output_file.write (', ')
				
		output_file.write ('\n')
		
		## Plot the number of k-points in the file
		if args.ibzkpt:
			output_file.write ('%d\n' % (len(xPath) + n_ibzkpt))
		else:
			output_file.write ('%d\n' % len(xPath))
			
		output_file.write ('Reciprocal lattice\n')
		
		## Plot the k-points in the file
		if args.ibzkpt:
			output_file.write (ibzkpt_kpoints)
			
		for i in range (len(xPath)):
			output_file.write ("%.15f    %.15f    %.15f    %.4f\n" % (xPath[i], yPath[i], zPath[i], args.weight))

def main():
	'''
	Generate k-points path for creating band structures
	'''
	
	args = parseArgs()
	
	if not args.quiet:
		print ("****************************")
		print (" vaspirin v2.0: gen_kpoints ")
		print ("****************************")
		
		printRunDescription (args)
	
	## Plots the artistic band offsets
	genKPT (args)
	
if __name__ == "__main__":
	main ()
