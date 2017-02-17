#!/usr/bin/env python

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import argparse
import sys

def make_cmap(colors, position=None, bit=False):
    '''
    make_cmap takes a list of tuples which contain RGB values. The RGB
    values may either be in 8-bit [0 to 255] (in which bit must be set to
    True when called) or arithmetic [0 to 1] (default). make_cmap returns
    a cmap with equally spaced colors.
    Arrange your tuples so that the first color is the lowest value for the
    colorbar and the last is the highest.
    position contains values from 0 to 1 to dictate the location of each color.
    
    Reference: https://github.com/iuryt/OceanLab/blob/master/deprecated/old/seaplot.py
    '''
    
    bit_rgb = np.linspace(0,1,256)
    if position == None:
        position = np.linspace(0,1,len(colors))
    else:
        if len(position) != len(colors):
            sys.exit("position length must be the same as colors")
        elif position[0] != 0 or position[-1] != 1:
            sys.exit("position must start with 0 and end with 1")
    if bit:
        for i in range(len(colors)):
            colors[i] = (bit_rgb[colors[i][0]],
                         bit_rgb[colors[i][1]],
                         bit_rgb[colors[i][2]])
    cdict = {'red':[], 'green':[], 'blue':[]}
    for pos, color in zip(position, colors):
        cdict['red'].append((pos, color[0], color[0]))
        cdict['green'].append((pos, color[1], color[1]))
        cdict['blue'].append((pos, color[2], color[2]))

    cmap = matplotlib.colors.LinearSegmentedColormap('my_colormap',cdict,256)
    return cmap

	
def parseArgs():
	"""
	Parse arguments from the command line. Uses the `argparse` package to
	establish all positional and optional arguments.
	"""
	parser = argparse.ArgumentParser(description='Create colored bands from projection data.',
									epilog= "Written by Daniel S. Koda (jan. 2017).",
									prog="colored_bands.py")

	parser.add_argument('-i', '--input_folder', default='bands_projected', help="projection data folder with .dat files. Default: bands_projected/")
	
	parser.add_argument('-o', '--output', default='colorBands.eps', help="output name for the generated bands, including the figure type. Default: colorBands.eps")
	
	parser.add_argument('-b', '--bands', type=int, nargs=2, default=[1, 1], help="range of bands to be plotted (default: 1 to 1)", metavar=('BAND_MIN', 'BAND_MAX'))
	
	parser.add_argument('-y', '--yaxis', type=float, nargs=2, default=[-3, 3],
					help="set the y-axis range for the band structure" +
					" (default: -3 to 3).",
					metavar=('Y_MIN', 'Y_MAX'))	

	parser.add_argument('-x', '--xaxis', type=float, nargs=2, default=[0, 1],
					help="set the x-axis range for the band structure" +
					" (default: 0 to 1).",
					metavar=('X_MIN', 'X_MAX'))
					
	parser.add_argument('-z', '--size', type=float, nargs=2, default=[4, 3],
					help="set the figure size for the band structure" +
					" (default: 4 inches by 3 inches).",
					metavar=('WIDTH', 'HEIGHT'))	
	
	parser.add_argument('-l', '--legend', action='store_true',
						help="display the color bar (legend) in the plot" +
						" (default: False).")
	
	parser.add_argument('-s', '--show', action='store_true',
						help="show the plot after doing everything" +
						" (default: False).")

	parser.add_argument('-q', '--quiet', action='store_true', help="do not display text on the output window (default: False)")
	
	return parser.parse_args()


def printRunDescription (args):
	'''
	Print description of the options chosen and the crystals input.
	'''
	
	leftJustSpace = 20
	print ("input folder:".ljust(leftJustSpace) + "%s" % args.input_folder)
	print ("output file:".ljust(leftJustSpace) + "%s" % args.output)
	print ("bands to plot:".ljust(leftJustSpace) + "from band %d to %d" % (args.bands[0], args.bands[1]))
	print ("xaxis limits:".ljust(leftJustSpace) + "from % 2.1f to % 2.1f" % (args.xaxis[0], args.xaxis[1]))
	print ("yaxis limits:".ljust(leftJustSpace) + "from % 2.1f to % 2.1f" % (args.yaxis[0], args.yaxis[1]))
	print ("include legend?".ljust(leftJustSpace) + ("yes" if args.legend else "no"))
	print ("show plot?".ljust(leftJustSpace) + ("yes" if args.show else "no"))


def main():
	'''
	Creates a colored band structure based on projected data
	'''
	
	args = parseArgs()
	
	if not args.quiet:
		print ("****************************")
		print (" vaspirin v2.0: color_bands ")
		print ("****************************")
		
		printRunDescription (args)
	
	## Dictionary of colors to help things make sense
	colorsDict = {
	'red' : (255,0,0),
	'orange' : (255,128,0), 
	'yellow' : (255,255,0),
	'yellowish green' : (128,255,0),
	'green' : (0,255,0),
	'greenish cyan' : (0,255,128),
	'cyan' : (0,255,255),
	'light blue' : (0,128,255),
	'blue' : (0,0,255),
	'indigo' : (128,0,255),
	'fuchsia' : (255,0,255),
	'pink' : (255,0,128),
	'gray' : (128,128,128),
	'black' : (0,0,0),
	'white' : (255,255,255),
	}
	
	## Defining the color map for this plot
	colors = [colorsDict.get('red'),
			  colorsDict.get('orange'),
			  colorsDict.get('yellow'),
			  colorsDict.get('yellowish green'),
			  colorsDict.get('green'),
			  colorsDict.get('greenish cyan'),
			  colorsDict.get('cyan'),
			  colorsDict.get('light blue'),
			  colorsDict.get('blue')
			  ]
	
	## Call the function make_cmap which returns your colormap
	my_cmap = make_cmap(colors, bit=True)

	## Check what size is the marker
	with open (args.input_folder + "/band01.dat", 'r') as f:
		## Read the first line
		l = f.readline().split()
		
		## Convert the first line to float numbers
		l = [float(i) for i in l]
		
		## We find the marker size simply by summing the two contributions
		markerSize = l[2] + l[3]
	
	
	## Norm for colors based on projected data
	norm = matplotlib.colors.Normalize(vmin = 0, vmax = markerSize)

	## Creates a figure for the 
	fig = plt.figure (figsize=(args.size[0],args.size[1]))

	## Plot the specified bands
	for i in range (args.bands[0], args.bands[1]):
		try:
			k,E,p1,p2 = np.loadtxt (args.input_folder + ("/band%02d.dat" % i), unpack = True)
		except FileNotFoundError:
			print ("Band out of range! Check if you have correctly inserted the bands you want to draw.")
			sys.exit(1)
		
		plt.scatter(k, E, c=p2, norm=norm, cmap = my_cmap, linewidth='0')

	
	## Set the axis limits
	axes = plt.gca()
	axes.set_xlim([args.xaxis[0],args.xaxis[1]])
	axes.set_ylim([args.yaxis[0],args.yaxis[1]])
	axes.set_xticklabels([])
	axes.xaxis.set_ticks_position('none')

	## Include the legend if ordered to do so
	if args.legend:
		cbar = plt.colorbar()
		cbar.ax.set_yticklabels([])

	## Print the figure
	fig.savefig (args.output)
	
	## Show the figure if ordered to do so
	if args.show:
		plt.show()
	
		
if __name__ == "__main__":
	main ()
