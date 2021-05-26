import shutil

from django.shortcuts import render
from django.conf import settings
import os
from os import path
from datetime import datetime
from django.http import HttpResponseRedirect, HttpResponse
from wsgiref.util import FileWrapper
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.objects.log.importer.xes import importer
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from pm4py.algo.discovery.dfg import algorithm as dfg_factory
import json
import re
import log_filtering.abstraction_support_functions as asf
import log_filtering.utils as utils
import log_filtering.transformation as trans




# Create your views here.

def filter(request):
    event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
    event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
    log = importer.apply(event_log)

    dfg = dfg_factory.apply(log)
    this_data,temp_file = dfg_to_g6(dfg)
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp")

    if request.method == 'POST':
        if "uploadButton" in request.POST:
            print("in request")
        event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")

        if settings.EVENT_LOG_NAME == ':notset:':
            return HttpResponseRedirect(request.path_info)

        return render(request,'filter.html', {'log_name': settings.EVENT_LOG_NAME, 'data': this_data})

    else:
        if "groupButton" in request.GET:
            print("in request")
            groupname = request.GET["new_name"]
            pattern = request.GET["values"]

            temp_file = os.path.join(temp_path, 'data.json')
            eventlist = [x for x in pattern.split(',') if x]
            abs_sequence = {}

            pattern = []
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for index in eventlist:
                    # id = int(index)
                    id = int(index.split("_")[1])
                    print("id = ", id)
                    print("event = ", data['nodes'][id]['label'])
                    pattern.append(data['nodes'][id]['label'])

                # print([])
                # for nodes in data['nodes']:
                #     print("id = ", nodes['id'])
                #     print("label = ", nodes['label'])
            print(pattern)


            pattern_list = [{'ID': 0, 'Name': groupname, 'Pattern': pattern}]
            print(pattern_list)
            log = utils.import_log_XES(event_log)
            concatenated_traces, concatenated_timestamps = asf.read_log(log)

            abstracted_traces, abstracted_timestamps = \
                asf.perform_abstractions(
                                [0], pattern_list,
                                concatenated_traces,
                                concatenated_timestamps
                                )
            print("absracted pattern = ", abstracted_traces)

            log_content = trans.generate_transformed_log_XES(
                                                event_log,
                                                abstracted_traces,
                                                abstracted_timestamps,
                                                event_log[:-4] + "_header.XES"
                                                )

            print("log_content = ", log_content)

            # very ugly code to deal with meta data loss of pm4py filters
            user_abstracted = utils.import_log_XES(event_log[:-4] +
                                                   "_header.XES")

            print("user_abstracted = ", user_abstracted)
            dfg = dfg_discovery.apply(user_abstracted)
            dfg = dfg_factory.apply(log)
            this_data, temp_file = dfg_to_g6(dfg)

            return render(request,'filter.html', {'log_name': settings.EVENT_LOG_NAME, 'data':this_data})


        else:
            event_logs_path = os.path.join(settings.MEDIA_ROOT, "event_logs")
            temp_path = os.path.join(settings.MEDIA_ROOT, "temp")

            if settings.EVENT_LOG_NAME == ':notset:':
                return HttpResponseRedirect(request.path_info)

            event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)

            event_log = os.path.join(event_logs_path, settings.EVENT_LOG_NAME)
            exportPrivacyAwareLog = True
            log = importer.apply(event_log)
            dfg = dfg_factory.apply(log)
            print(dfg)
            this_data,temp_file = dfg_to_g6(dfg)

            re.escape(temp_file)
            network = {}

            return render(request,'filter.html', {'log_name': settings.EVENT_LOG_NAME, 'json_file': temp_file, 'data':json.dumps(this_data)})

def dfg_to_g6(dfg):
    unique_nodes = []

    for i in dfg:
        unique_nodes.extend(i)
    unique_nodes = list(set(unique_nodes))

    unique_nodes_dict = {}

    for index, node in enumerate(unique_nodes):
        unique_nodes_dict[node] = "node_" + str(index)

    nodes = [{'id': unique_nodes_dict[i], 'label': i} for i in unique_nodes_dict]
    edges = [{'from': unique_nodes_dict[i[0]], 'to': unique_nodes_dict[i[1]], "data": {"freq": dfg[i]}} for i in
             dfg]
    data = {
        "nodes": nodes,
        "edges": edges,
    }
    temp_path = os.path.join(settings.MEDIA_ROOT, "temp")
    temp_file = os.path.join(temp_path, 'data.json')
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    return data, temp_file