# -*- coding: utf-8 -*-

from setuptools import setup
 
    
setup (
	name='vaspirin',
	packages=['vaspirin'],
	
	requires = [
	'matplotlib',
	'numpy',
	'scipy',
	'pylab',
	'itertools',
	],
	entry_points = {
        "console_scripts": ['vaspirin = vaspirin.vaspirin:main']
        },
	version='1.1',
	description='Painless VASP post-processing tool',
	author='Daniel S. Koda, Ivan Guilhon',
	author_email='danielskoda@gmail.com, ivanguilhonn@gmail.com ',
	url='http://www.gmsn.ita.br/',
	)
