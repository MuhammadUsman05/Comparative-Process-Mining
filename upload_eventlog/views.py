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
from pm4py.objects.log.importer.xes import importer as xes_importer_factory


# Create your views here.

def upload_page(request):
    log_attributes = {}
    event_logs_path = os.path.join(settings.MEDIA_ROOT,"event_logs")
    n_event_logs_path = os.path.join(settings.MEDIA_ROOT,"none_event_logs")

    if request.method == 'POST':
        if request.is_ajax():  # currently is not being used (get commented in html file)
            filename = request.POST["log_name"]
            print('filename = ', filename)
            file_dir = os.path.join(event_logs_path, filename)
            eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

            xes_log = xes_importer_factory.apply(file_dir)
            no_traces = len(xes_log)
            no_events = sum([len(trace) for trace in xes_log])
            log_attributes['no_traces'] = no_traces
            log_attributes['no_events'] = no_events
            print(log_attributes)
            json_respone = {'log_attributes': log_attributes, 'eventlog_list':eventlogs}
            return HttpResponse(json.dumps(json_respone),content_type='application/json')
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

                return render(request, 'upload.html', {'eventlog_list':eventlogs})

            elif "deleteButton" in request.POST: #for event logs
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
                return render(request, 'upload.html',{'eventlog_list': eventlogs, 'n_eventlog_list': n_eventlogs})


            elif "n_deleteButton" in request.POST: #for none event logs
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

                xes_log = xes_importer_factory.apply(file_dir)
                no_traces = len(xes_log)
                no_events = sum([len(trace) for trace in xes_log])
                log_attributes['no_traces'] = no_traces
                log_attributes['no_events'] = no_events

                # Discover DFG
                from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
                dfg = dfg_discovery.apply(xes_log)
                g6, temp_file = dfg_to_g6(dfg)

                jsondata = {
                    'nodes': [
                        {
                            'id': 'node_0',
                            'name': 'Send Fine',
                            'conf': [
                                {
                                    'label': 'medain',
                                    'value': '10'
                                },
                                {
                                    'label': 'mean',
                                    'value': '10'
                                },
                                {
                                    'label': 'mode',
                                    'value': '10'
                                }
                            ]
                        },
                        {
                            'id': 'node_1',
                            'name': 'Add penalty',
                            'conf': [
                                {
                                    'label': 'medain',
                                    'value': '10'
                                },
                                {
                                    'label': 'mean',
                                    'value': '10'
                                },
                                {
                                    'label': 'mode',
                                    'value': '10'
                                }
                            ]
                        },
                        {
                            'id': 'node_2',
                            'name': 'Insert Date Appeal to Prefecture',
                            'conf': [
                                {
                                    'label': 'medain',
                                    'value': '10'
                                },
                                {
                                    'label': 'mean',
                                    'value': '10'
                                },
                                {
                                    'label': 'mode',
                                    'value': '10'
                                }
                            ]
                        },
                        {
                            'id': 'node_3',
                            'name': 'Payment',
                            'conf': [
                                {
                                    'label': 'medain',
                                    'value': '10'
                                },
                                {
                                    'label': 'mean',
                                    'value': '10'
                                },
                                {
                                    'label': 'mode',
                                    'value': '10'
                                }
                            ]
                        },
                        {
                            'id': 'node_4',
                            'name': 'Insert Fine Notification',
                            'conf': [
                                {
                                    'label': 'medain',
                                    'value': '10'
                                },
                                {
                                    'label': 'mean',
                                    'value': '10'
                                },
                                {
                                    'label': 'mode',
                                    'value': '10'
                                }
                            ]
                        },
                        {
                            'id': 'node_5',
                            'name': 'Create Fine',
                            'conf': [
                                {
                                    'label': 'medain',
                                    'value': '10'
                                },
                                {
                                    'label': 'mean',
                                    'value': '10'
                                },
                                {
                                    'label': 'mode',
                                    'value': '10'
                                }
                            ]
                        },
                        {
                            'id': 'node_6',
                            'name': 'Send Appeal to Prefecture',
                            'conf': [
                                {
                                    'label': 'medain',
                                    'value': '10'
                                },
                                {
                                    'label': 'mean',
                                    'value': '10'
                                },
                                {
                                    'label': 'mode',
                                    'value': '10'
                                }
                            ]
                        },
                        {
                            'id': 'node_7',
                            'name': 'Send for Credit Collection',
                            'conf': [
                                {
                                    'label': 'medain',
                                    'value': '10'
                                },
                                {
                                    'label': 'mean',
                                    'value': '10'
                                },
                                {
                                    'label': 'mode',
                                    'value': '10'
                                }
                            ]
                        }
                    ],
                    'edges': [
                        {
                            'source': 'node_5',
                            'target': 'node_0',
                            'label': 39,
                            'style': {
                                'lineWidth': 8,
                                'endArrow': True
                            },
                            'labelCfg': {
                                'style': {
                                    'fontSize': 39,
                                    'fontWeight': 'bold'
                                }
                            }
                        },
                        {
                            'source': 'node_0',
                            'target': 'node_4',
                            'label': 32,
                            'style': {
                                'lineWidth': 6,
                                'endArrow': True
                            }
                        },
                        {
                            'source': 'node_4',
                            'target': 'node_1',
                            'label': 31,
                            'style': {
                                'lineWidth': 6,
                                'endArrow': True
                            }
                        },
                        {
                            'source': 'node_1',
                            'target': 'node_7',
                            'label': 22,
                            'style': {
                                'lineWidth': 4,
                                'endArrow': True
                            }
                        },
                        {
                            'source': 'node_1',
                            'target': 'node_3',
                            'label': 9,
                            'style': {
                                'lineWidth': 2,
                                'endArrow': True
                            }
                        },
                        {
                            'source': 'node_4',
                            'target': 'node_2',
                            'label': 1,
                            'style': {
                                'lineWidth': 2,
                                'endArrow': True
                            }
                        },
                        {
                            'source': 'node_2',
                            'target': 'node_1',
                            'label': 1,
                            'style': {
                                'lineWidth': 2,
                                'endArrow': True
                            }
                        },
                        {
                            'source': 'node_1',
                            'target': 'node_6',
                            'label': 1,
                            'style': {
                                'lineWidth': 2,
                                'endArrow': True
                            }
                        },
                        {
                            'source': 'node_5',
                            'target': 'node_3',
                            'label': 12,
                            'style': {
                                'lineWidth': 2,
                                'endArrow': True
                            }
                        },
                        {
                            'source': 'node_3',
                            'target': 'node_3',
                            'label': 2,
                            'style': {
                                'lineWidth': 2,
                                'endArrow': True
                            }
                        }
                    ]
                }

                json_data = json.dumps(jsondata)
                log_attributes['dfg'] = json_data
                log_attributes['g6'] = g6


                eventlogs = [f for f in listdir(event_logs_path) if isfile(join(event_logs_path, f))]

                return render(request, 'upload.html',{'eventlog_list': eventlogs, 'log_name':filename, 'log_attributes':log_attributes})

            elif "downloadButton" in request.POST: # for event logs
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

            elif "n_downloadButton" in request.POST: #for none event logs
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

        return render(request, 'upload.html', {'eventlog_list':eventlogs, 'n_eventlog_list': n_eventlogs})

        #return render(request, 'upload.html')

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