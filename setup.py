# -*- coding: utf-8 -*-

from setuptools import setup
 
    
setup (
	name='vaspirin',
	packages=['vaspirin'],
	version='2.0',
	
	description='Painless VASP post-processing tool',
	
	author='Daniel S. Koda, Ivan Guilhon',
	author_email='danielskoda@gmail.com, ivanguilhonn@gmail.com ',
	url='http://www.gmsn.ita.br/',
	download_url = 'https://github.com/gmsn-ita/vaspirin',
	
	scripts = [
	'scripts/band_offsets.py',
	'scripts/colored_bands.py',
	'scripts/dos.py',
	'scripts/gen_kpoints.py',
	'scripts/move_atoms.py',
	'scripts/plot_bands.py',
	'scripts/plot_compared_bands.py',
	'scripts/rotate_molecule.py',
	'scripts/split_procar.py',
	'scripts/strain_cell.py',	
	],
	
	requires = [
	'matplotlib',
	'numpy',
	'scipy',
	'pylab',
	'itertools',
	],
	
	include_package_data=True,
	)
