#/usr/bin/env python
# coding: utf-8

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import argparse
import sys
import re

class PyplotConst (object):
	"""
	Constants for style-plotting with matplotlib.pyplot
	"""
	
	lineStyles = ['-', '--', '-.', ':', 'None', ' ', '']
	labelFont = {'fontname' : 'Linux Biolinum',
				 #~ 'weight' : 'bold',
				 'size'   : 14	}
	params = {'mathtext.default': 'regular' } 
	

class Offsets (object):
	"""
	Defines the band offset of a single compound specified within the ALIGNMENTS file
	"""
	
	def __init__ (self, label, vbm, cbm):
		
		self.label = label
		"""
		Defines a label for the compound
		"""
		
		self.vbm = float(vbm)
		"""
		Defines the valence band maximum (ionization energy)
		"""
		
		self.cbm = float(cbm)
		"""
		Defines the conduction band minimum (electron affinity)
		"""
		
		self.vacum = 0
		"""
		Defines the vacuum level for this material
		"""
		
		self.color = 'black'
		"""
		Specifies the color for this band discontinuities
		"""
		
	def setVacuum (self, vac):
		"""
		Sets the vacuum potential for this material
		"""
		
		self.vacuum = float (vac)
	
	def setColor (self, color):
		"""
		Sets a color for this material representation
		"""
		
		self.color = color		


def importAlignmentsList (fAlignments):
		'''
		The file ALIGNMENTS contains information on how to describe band offsets between the interfaces. Its format must be several lines organized as something like:
		
		Label   VBM    CBM   color

		Lines with --- and ... are band offsets dividers, representing dashed and dotted lines.
		
		For example:
		MoS$_2$ -5.795 -4.016 red
		--- red
		MoS$_2$ -5.819 -4.075 black
		SnS$_2$ -6.662 -5.120 black
		--- blue
		SnS$_2$ -6.586 -5.063 blue
		''' 
		
		## Opens the ALIGNMENTS file
		try:
			with open(fAlignments,'r') as f:
				inputFile = f.read().strip()
				lines = [x for x in inputFile.split('\n') if x] # removes repeated \n ''
				
		except FileNotFoundError:
			print ('Alignments file not found. Please specify a valid filename.')
			sys.exit()
		
		offsetsList = []
		
		## Each line is a band offset or a ligature
		for eachLine in lines:
			## The first information should be the material
			offsetLabel = re.split(' +', eachLine.strip())[0]
			
			if offsetLabel in PyplotConst.lineStyles:
				## line format: LINE_STYLE COLOR
				try:
					color = re.split(' +', eachLine.strip())[1]
				except IndexError:
					print ('Invalid file formatting. Please correct it and try again.')
					sys.exit(1)
				
				## Creates an object which is only a ligature	
				newOffset = Offsets (offsetLabel, 0, 0)
			else:
				## line format: LABEL VBM CBM COLOR
				try:
					vbm = re.split(' +', eachLine.strip())[1]
					cbm = re.split(' +', eachLine.strip())[2]
					color = re.split(' +', eachLine.strip())[3]
				except IndexError:
					print ('Invalid file formatting. Please correct it and try again.')
					sys.exit(1)

				## Creates an object which is a band offset
				newOffset = Offsets (offsetLabel, vbm, cbm)

			newOffset.setColor(color)
			offsetsList.append(newOffset)				
				
		return offsetsList

def printOffsetsList (offsetsList, args):
		'''
		A list of band offsets is received and printed using matplotlib.pyplot.
		Lines joining different band offsets should not be at the end or beginning of the lists
		'''
		
		last_x = 0
		
		offset_x_length = 1
		offset_linewidth = 3
		ligature_x_length = 0.4
		ligature_linewidth = 1.5
		axes_margin = 0.25
		
		## Then, the offsets are plotted
		for i in range (len(offsetsList)):
			## Plot ligature
			if offsetsList[i].label in PyplotConst.lineStyles:
				
				## Reads the offsets from the last and the next one
				vbm_last = offsetsList[i-1].vbm
				cbm_last = offsetsList[i-1].cbm
				vbm_next = offsetsList[i+1].vbm
				cbm_next = offsetsList[i+1].cbm
				
				labelInterface = offsetsList[i-1].label + '/' + offsetsList[i+1].label
				
				if offsetsList[i].label == '-':
					## Plot line joining adjacent VBM
					plt.plot ([last_x, last_x], [vbm_last, vbm_next],
							  linestyle = offsetsList[i].label,
							  color = offsetsList[i].color,
							  linewidth = offset_linewidth)
					
					## Plot line joining adjacent CBM
					plt.plot ([last_x, last_x], [cbm_last, cbm_next],
							  linestyle = offsetsList[i].label,
							  color = offsetsList[i].color,
							  linewidth = offset_linewidth)
					
					## Label interface
					## label becomes aligned in the center if there is only one interface (two materials)
					if args.number == 2:
						plt.annotate (labelInterface, (last_x, (max(vbm_last, vbm_next)+ min(cbm_last, cbm_next))/2),
									  horizontalalignment='center', verticalalignment='center', **PyplotConst.labelFont)
					
					last_x = last_x
							  
				else:
					## Plot line joining VBM with stylish lines
					plt.plot ([last_x, last_x + ligature_x_length], [vbm_last, vbm_next],
							  linestyle = offsetsList[i].label,
							  color = offsetsList[i].color,
							  linewidth = ligature_linewidth)
					
					## Plot line joining CBM with stylish lines
					plt.plot ([last_x, last_x + ligature_x_length], [cbm_last, cbm_next],
							  linestyle = offsetsList[i].label,
							  color = offsetsList[i].color,
							  linewidth = ligature_linewidth)
					
					last_x = last_x + ligature_x_length
			
			## Or plot offset
			else:		 
				
				vbm = offsetsList[i].vbm
				cbm = offsetsList[i].cbm
				
				## Plot VBM
				plt.plot ([last_x, last_x + offset_x_length], [vbm, vbm],
						  linestyle = '-',
						  color = offsetsList[i].color,
						  linewidth = offset_linewidth)
				
				plt.annotate (("% .2f" % offsetsList[i].vbm), (last_x + offset_x_length/2, vbm - 0.03), horizontalalignment='center', verticalalignment='top', **PyplotConst.labelFont)
				
				## Plot CBM
				plt.plot ([last_x, last_x + offset_x_length], [cbm, cbm],
						  linestyle = '-',
						  color = offsetsList[i].color,
						  linewidth = offset_linewidth)
				
				plt.annotate (("% .2f" % offsetsList[i].cbm), (last_x + offset_x_length/2, cbm + 0.02), horizontalalignment='center', verticalalignment='bottom', **PyplotConst.labelFont)
				
				plt.annotate (offsetsList[i].label, (last_x + offset_x_length/2, (vbm+cbm)/2),
									  horizontalalignment='center', verticalalignment='center', **PyplotConst.labelFont)
				
				last_x = last_x + offset_x_length
		
		## A set of pyplot configurations is passed
		plt.margins (axes_margin)
		plt.rcParams.update(PyplotConst.params)
		
		## Turn on the axis if requested
		if args.axis:
			plt.axis('on')
		else:
			plt.axis('off')
		
		plt.savefig (args.output)
					
		## Finally, the plot is shown
		if args.show:
			plt.show()


def parseArgs():
	"""
	Parse arguments from the command line. Uses the `argparse` package to
	establish all positional and optional arguments.
	"""
	parser = argparse.ArgumentParser(description='Easy script to create band alignments',
									epilog= "Written by Daniel S. Koda (feb. 2017).",
									prog="band_offsets.py")

	parser.add_argument('input_file', default='ALIGNMENTS', help="ALIGNMENTS input file")
	
	parser.add_argument('-o', '--output', default='offsets.png', help="output name for the generated files with its format. Default: offsets.png")
	
	parser.add_argument('-v', '--vacuum', type=float, default=0.0, help="vacuum dipole step (Default: 0.0)")
	
	parser.add_argument('-q', '--quiet', action='store_true', help="do not display text on the output window (default: False)")
	
	parser.add_argument('-x', '--axis', action='store_true', help="turn on the axis for the plot (default: False)")
	
	parser.add_argument('-s', '--show', action='store_true', help="show the band alignments before saving to file (default: False)")
	
	parser.add_argument('-n', '--number', type=int, default=2, help="number of materials composing the interface (Default: 2)")
	
	return parser.parse_args()

def printRunDescription (args):
	'''
	Print description of the options chosen and the crystals input.
	'''
	
	leftJustSpace = 20
	print ("input file:".ljust(leftJustSpace) + "%s" % args.input_file)
	print ("output file:".ljust(leftJustSpace) + "%s" % args.output)
	print ("vacuum step:".ljust(leftJustSpace) + "% .2f" % args.vacuum)
                     

	

def main():
	'''
	Rotates a molecule in a POSCAR file by angleDegrees
	The refAtom is taken as reference to the rotation
	'''
	
	args = parseArgs()
	
	if not args.quiet:
		print ("*****************************")
		print (" vaspirin v2.0: band_offsets ")
		print ("*****************************")
		
		printRunDescription (args)
	
	## Open the input file and creates an offsets list
	offsetsList = importAlignmentsList (args.input_file)
	
	## Plots the artistic band offsets
	printOffsetsList (offsetsList, args)
	
if __name__ == "__main__":
	main ()

