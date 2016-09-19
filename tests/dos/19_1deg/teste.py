#!/usr/bin/env python

import plotter, dos

d = dos.DOS("DOSCAR")
p = plotter.DatFiles(0.5)

d.createIonVsMaterials('PROJECTION')

p.datDOSproj(d)
p.datDOS(d)
