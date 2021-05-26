import pm4py
import pandas as pd
import os


def filter_log(log, filterItemList, isKeepOnlyThese = True):
    from pm4py.algo.filtering.log.attributes import attributes_filter
    for key in filterItemList:
        list_of_values = filterItemList[key]
        if (type(list_of_values[0]).__name__ == 'int'):
            filtered_log_events = attributes_filter.apply_numeric_events(log, min(list_of_values), max(list_of_values), parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: key})
        else:
            filtered_log_events = attributes_filter.apply(log, list_of_values, parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: key, attributes_filter.Parameters.POSITIVE: isKeepOnlyThese})
    return filtered_log_events


from pm4py.objects.log.importer.xes import importer as xes_importer
path = os.path.join("..", "eventlogs", "running-example.xes")
log = xes_importer.apply(path)

filters = {}
filters.setdefault('org:resource', []).append('Pete')
filters.setdefault('org:resource', []).append('Ellen')
filters.setdefault('Costs', []).append("100")

filtered_log = filter_log(log, filters, True)

from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
dfg = dfg_discovery.apply(log)

print(dir(dfg))
print(type(dfg))

from pm4py.visualization.dfg import visualizer as dfg_visualization
gviz = dfg_visualization.apply(dfg, log=log, variant=dfg_visualization.Variants.FREQUENCY)
dfg_visualization.view(gviz)


