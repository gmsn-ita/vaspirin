#!/usr/bin/env python

import bandcharacter, bandstructure, plotter

b = bandstructure.BandStructure ('OUTCAR')
p = bandcharacter.PROCAR ('PROCAR')
p.createIonVsMaterials('PROJECTION')

dat = plotter.DatFiles ()
dat.datCharacter(b, p, 0.5)

plt = plotter.Grace ()
plt.readXticks('KPOINTS')
plt.printBandCharacter (b)

plt.printBandProjected(b, p)


plt.xTicks
