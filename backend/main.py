import pm4py
import pandas as pd

import os
from pm4py.objects.log.importer.xes import importer as xes_importer
path = os.path.join("..", "eventlogs", "running-example.xes")
log = xes_importer.apply(path)

from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
dfg = dfg_discovery.apply(log)

print(dir(dfg))
print(type(dfg))

from pm4py.visualization.dfg import visualizer as dfg_visualization
gviz = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.FREQUENCY)
dfg_visualization.view(gviz)

