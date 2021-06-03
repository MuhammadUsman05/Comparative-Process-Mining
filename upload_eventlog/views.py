from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.conf import settings
import os
from os import listdir
from os.path import isfile, join
from django.http import HttpResponse
from mimetypes import guess_type
from wsgiref.util import FileWrapper
import json
import pandas as pd
from pm4py.objects.log.importer import xes
from pm4py.objects.log.importer.xes import importer as xes_importer_factory
from pm4py.objects.log.util import dataframe_utils
from pm4py.objects.conversion.log import converter as log_converter
from pm4py.objects.conversion.log.variants import to_data_frame as log_to_data_frame
import heapq
import pm4py
from pm4py.algo.filtering.dfg import dfg_filtering

# Create your views here.

def upload_page(request):
    log_attributes = {}
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    n_event_logs_path = os.path.join(settings.MEDIA_ROOT, "none_event_logs")

    if request.method == 'POST':
        if request.is_ajax():  # currently is not being used (get commented in html file)
            filename = request.POST["log_name"]
            print('filename = ', filename)
            file_dir = os.path.join(event_logs_path, filename)
            eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

            log = xes_importer_factory.apply(file_dir)
            no_traces = len(log)
            no_events = sum([len(trace) for trace in log])
            log_attributes['no_traces'] = no_traces
            log_attributes['no_events'] = no_events
            print(log_attributes)
            json_respone = {'log_attributes': log_attributes, 'eventlog_list': eventlogs}
            return HttpResponse(json.dumps(json_respone), content_type='application/json')
            # return render(request, 'upload.html', {'log_attributes': log_attributes, 'eventlog_list':eventlogs})
        else:
            if "uploadButton" in request.POST:
                if "event_log" not in request.FILES:
                    return HttpResponseRedirect(request.path_info)

                log = request.FILES["event_log"]
                fs = FileSystemStorage(event_logs_path)
                filename = fs.save(log.name, log)
                uploaded_file_url = fs.url(filename)

                eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]
                # eventlogs.append(filename)

                file_dir = os.path.join(event_logs_path, filename)

                # xes_log = xes_importer_factory.apply(file_dir)
                # no_traces = len(xes_log)
                # no_events = sum([len(trace) for trace in xes_log])
                # log_attributes['no_traces'] = no_traces
                # log_attributes['no_events'] = no_events

                return render(request, 'upload.html', {'eventlog_list': eventlogs})

            elif "deleteButton" in request.POST:  # for event logs
                if "log_list" not in request.POST:
                    return HttpResponseRedirect(request.path_info)

                filename = request.POST["log_list"]
                if settings.EVENT_LOG_NAME == filename:
                    settings.EVENT_LOG_NAME = ":notset:"

                eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]
                n_eventlogs = [f for f in listdir(n_event_logs_path) if isfile(join(n_event_logs_path, f))]

                eventlogs.remove(filename)
                file_dir = os.path.join(event_logs_path, filename)
                os.remove(file_dir)
                return render(request, 'upload.html', {'eventlog_list': eventlogs, 'n_eventlog_list': n_eventlogs})


            elif "n_deleteButton" in request.POST:  # for none event logs
                if "n_log_list" not in request.POST:
                    return HttpResponseRedirect(request.path_info)

                filename = request.POST["n_log_list"]

                n_eventlogs = [f for f in listdir(n_event_logs_path) if isfile(join(n_event_logs_path, f))]
                eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

                n_eventlogs.remove(filename)
                file_dir = os.path.join(n_event_logs_path, filename)
                os.remove(file_dir)
                return render(request, 'upload.html', {'eventlog_list': eventlogs, 'n_eventlog_list': n_eventlogs})

            elif "setButton" in request.POST:
                if "log_list" not in request.POST:
                    return HttpResponseRedirect(request.path_info)

                filename = request.POST["log_list"]
                settings.EVENT_LOG_NAME = filename

                file_dir = os.path.join(event_logs_path, filename)

                log = convert_eventfile_to_log(file_dir)

                # Apply Filters on log
                # filters = {
                #     'concept:name': ['Test Repair']
                # }
                # log = filter_log(log, filters, True)

                no_traces = len(log)
                no_events = sum([len(trace) for trace in log])
                log_attributes['no_traces'] = no_traces
                log_attributes['no_events'] = no_events

                dfg = log_to_dfg(log, 1)

                g6, temp_file = dfg_to_g6(dfg)
                dfg_g6_json = json.dumps(g6)

                log_attributes['dfg'] = dfg_g6_json

                # Get all the column names and respective values
                log_attributes['ColumnNamesValues'] = convert_eventlog_to_json(log)

                eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

                return render(request, 'upload.html',
                              {'eventlog_list': eventlogs, 'log_name': filename, 'log_attributes': log_attributes})

            elif "downloadButton" in request.POST:  # for event logs
                if "log_list" not in request.POST:
                    return HttpResponseRedirect(request.path_info)

                filename = request.POST["log_list"]
                file_dir = os.path.join(event_logs_path, filename)

                try:
                    wrapper = FileWrapper(open(file_dir, 'rb'))
                    response = HttpResponse(wrapper, content_type='application/force-download')
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_dir)
                    return response
                except Exception as e:
                    return None

            elif "n_downloadButton" in request.POST:  # for none event logs
                if "n_log_list" not in request.POST:
                    return HttpResponseRedirect(request.path_info)

                filename = request.POST["n_log_list"]
                file_dir = os.path.join(n_event_logs_path, filename)

                try:
                    wrapper = FileWrapper(open(file_dir, 'rb'))
                    response = HttpResponse(wrapper, content_type='application/force-download')
                    response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_dir)
                    return response
                except Exception as e:
                    return None

    else:

        # file_dir = os.path.join(settings.MEDIA_ROOT, "Privacy_P6uRPEd.xes")
        # xes_log = xes_importer_factory.apply(file_dir)
        # no_traces = len(xes_log)
        # no_events = sum([len(trace) for trace in xes_log])
        # log_attributes['no_traces'] = no_traces
        # log_attributes['no_events'] = no_events
        eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]
        n_eventlogs = [f for f in listdir(n_event_logs_path) if isfile(join(n_event_logs_path, f))]

        return render(request, 'upload.html', {'eventlog_list': eventlogs, 'n_eventlog_list': n_eventlogs})

        # return render(request, 'upload.html')


def log_to_dfg(log, percentage_most_freq_edges):
    # Discover DFG
    from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
    # dfg = dfg_discovery.apply(log)
    dfg, sa, ea = pm4py.discover_directly_follows_graph(log)
    activities_count = pm4py.get_attribute_values(log, "concept:name")

    # Filter Frequent Paths
    dfg, sa, ea, activities_count = dfg_filtering.filter_dfg_on_paths_percentage(dfg, sa, ea, activities_count, percentage_most_freq_edges)
    return dfg


def dfg_to_g6(dfg):
    unique_nodes = []

    for i in dfg:
        unique_nodes.extend(i)
    unique_nodes = list(set(unique_nodes))

    unique_nodes_dict = {}

    for index, node in enumerate(unique_nodes):
        unique_nodes_dict[node] = "node_" + str(index)

    nodes = [{'id': unique_nodes_dict[i], 'name': i, 'conf': [
        {
            'label': 'Name',
            'value': i
        }
    ]} for i in unique_nodes_dict]
    freqList = [int(dfg[i]) for i in dfg]
    maxVal = max(freqList) if len(freqList) != 0 else 0
    minVal = min(freqList) if len(freqList) != 0 else 0

    edges = [{'source': unique_nodes_dict[i[0]], 'target': unique_nodes_dict[i[1]], 'label': dfg[i],
              "style": {"lineWidth": ((int(dfg[i]) - minVal) / (maxVal - minVal) * (20 - 2) + 2), "endArrow": True}} for
             i in
             dfg]
    data = {
        "nodes": nodes,
        "edges": edges,
    }

    # Apply freq filtering on edges

    temp_path = os.path.join(settings.MEDIA_ROOT, "temp")
    temp_file = os.path.join(temp_path, 'data.json')
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data, temp_file


def filter_log(log, filterItemList, isKeepOnlyThese=True):
    from pm4py.algo.filtering.log.attributes import attributes_filter
    filtered_log_events = log;

    for key in filterItemList:
        list_of_values = filterItemList[key]
        if (type(list_of_values[0]).__name__ == 'int'):
            filtered_log_events = attributes_filter.apply_numeric_events(filtered_log_events, min(list_of_values),
                                                                         max(list_of_values), parameters={
                    attributes_filter.Parameters.ATTRIBUTE_KEY: key,
                    attributes_filter.Parameters.POSITIVE: isKeepOnlyThese})
        else:
            filtered_log_events = attributes_filter.apply(filtered_log_events, list_of_values,
                                                          parameters={attributes_filter.Parameters.ATTRIBUTE_KEY: key,
                                                                      attributes_filter.Parameters.POSITIVE: isKeepOnlyThese})

    return filtered_log_events


def convert_eventfile_to_log(file_path):
    file_name, file_extension = os.path.splitext(file_path)

    if file_extension == '.csv':

        log = pd.read_csv(file_path, sep=',')
        log = dataframe_utils.convert_timestamp_columns_in_df(log)
        # log = log.sort_values('<timestamp_column>')
        log = log_converter.apply(log)

    else:

        log = xes_importer_factory.apply(file_path)

    # df = log_to_data_frame.apply(log)
    convert_eventlog_to_json(log)
    return log


def convert_eventlog_to_json(log):
    df = log_to_data_frame.apply(log)

    firstIteration = True
    jsonstr = "{ "
    for col in df:

        if not firstIteration:
            jsonstr += ", "
        else:
            firstIteration = False

        jsonstr += "\"" + col + "\"" + ": "

        uniqueSortedData = pd.Series(df[col].unique()).sort_values(ascending=True)
        uniqueSortedData = uniqueSortedData.reset_index(drop=True)
        jsonstr += uniqueSortedData.to_json(orient="columns", date_format='iso')

    jsonstr += " }"

    return jsonstr
