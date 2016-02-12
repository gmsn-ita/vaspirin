#!/usr/bin/env python

import bandcharacter, bandstructure, plotter

b = bandstructure.BandStructure ('OUTCAR')
p = bandcharacter.PROCAR ('PROCAR')
p.createIonVsMaterials("Mo=1 ; S = 2..3")

dat = plotter.DatFiles ()
plt = plotter.Grace ()
