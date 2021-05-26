import json
import traceback
from pm4py.algo.discovery.dfg import algorithm as dfg_factory
from pm4py.objects.conversion.log import converter as conversion_factory
from pm4py.objects.log.exporter.xes import exporter as xes_exporter
#from pm4py.objects.log.importer.csv import importer as csv_importer
from pm4py.objects.log.importer.xes import importer as xes_import_factory
from pm4py.visualization.dfg import visualizer as dfg_vis_factory
from pm4py.algo.filtering.log.attributes import attributes_filter
from pm4py.util import constants
import os


""" def import_csv(file):
    '''
    import csv and it adds classifiers
    input file path
    output log object
    '''
    try:
        event_stream = csv_importer.import_event_stream(file)
        log = conversion_factory.apply(event_stream)
        log = add_classifier(log)

    # handling the exceptions occuring during the import and converting
    except Exception as e:
        print("Error occur, please check the csv file", e)
        return None
    return log """


def add_classifier(log):
    '''
    check the column names and add them as classifier of log object
    input log object from pm4py
    output log with clasisfier attributes
    '''
    activity = None
    timestamp = None

    # check if the columns includes the keyword for activity / timestamps
    for k in log[0][0].keys():
        if activity is None:
            if ('concept:name' == k) or ('activity' in k.lower()):
                activity = k
        if timestamp is None:
            if 'timestamp' in k.lower() or ('time:timestamp' in k.lower()):
                timestamp = k

	# there is no candidates
    if (activity is None) or (timestamp is None):
        print("activity and/or timestamp cannot be found in the given log")
        return None

    # adding clasisifer attributes to log objects
    log.classifiers['activity classifier'] = activity
    log.classifiers['timestamp'] = timestamp
    print("successful in adding classifier")
    return log


def import_log_XES(path_to_xes_file):
    '''
    Description: to import xes file using pm4py library function
    Used: get the file path and call import method of library
    Input: path_to_xes_file
    Output: return imported log file
    '''
    try:
        log = xes_import_factory.apply(path_to_xes_file)
        log = add_classifier(log)


    except Exception as e:
        print(
            '''error occured during the loading the xes file. '''
            '''Please check if the file is valid XES\n\n''', e)
        exit(0)
        return

    return log


def clean_lifecycle_events(log):
    '''recives a log and checks if it contains multiple
    lifecycle events per activity. Returns a log that
    only contains the starting events. If the log has no
    lifecycle events it is returned without any changes'''

    try:
        if 'lifecycle:transition' in log[0][0].keys():
            if len(set([e['lifecycle:transition'] for e in log[0]])) > 1:
                log = attributes_filter.apply_events(log, ["start"],
                                                  parameters={constants.PARAMETER_CONSTANT_ATTRIBUTE_KEY:
                                                              "lifecycle:transition",
                                                              "positive": True})
    except Exception as e:
        print('An exception occured during cleaning of lifecycle events')
        print(e)

    return log


def import_pattern_json(path):
    '''
    Returns the pattern.json specified in the path argument
    '''
    patterns = None
    try:
        json_data = open(path, "r").read()
        patterns = json.loads(json_data)
        if not is_valid_user_input(patterns):
            print('There apears to be an error in the provided user patterns. Patterns will not be abstracted')
    except Exception as e:
        print('User Patterns could not be loaded. Patterns will not be abstracted')
        print(traceback.format_exc())
        return

    return patterns


def check_valid_json(file):
    '''
    Description: get data from json file and check its validity
    Used: to check whether user input userpattern required json format
    Input: json file path
    Output: return True if valid json format, otherwise return false
    '''
    try:
        json_data = open(path, "r").read()
        patterns = json.loads(json_data)
        if not is_valid_user_input(patterns):
            msg = "%s is not the XES/CSV file" % file
            raise argparse.ArgumentTypeError(msg)
        else:
            return file
    except Exception as e:
        print(
            '''error occured during the loading the xes file. '''
            '''Please check if the file is valid XES\n\n''', e)
        exit(0)
        return False


def is_valid_user_input(patterns):
    '''given the input of a pattern.json file it returns
    a trruth value of weather or not it is a valid patter input'''
    if type(patterns) != list:
        return False

    ids = []
    names = []
    for element in patterns:

        if type(element) != dict:
            return False

        if 'ID' not in element.keys():
            return False
        if type(element['ID']) != int:
            return False
        ids.append(element['ID'])

        if 'Name' not in element.keys():
            return False
        if type(element['Name']) != str:
            return False
        names.append(element['Name'])

        if 'Pattern' not in element.keys():
            return False
        if type(element['Pattern']) != list:
            return False
        for event in element['Pattern']:
            if type(event) != str:
                return False

    if len(set(ids)) != len(ids):
        return False
    if len(set(names)) != len(names):
        return False

    return True


def export_log(log, filename):
    '''
    Description: to export xes file using pm4py library function
    Used: get the log and call export method of library to
          export under provided file name
    Input: log file, file name
    Output: N/A
    '''
    xes_exporter.export_log(log, filename)


def export_process_model(dfgModel, log, filename):
    '''
    Description: to export graphical process model in .svg format
    using pm4py library function
    Used: generate and export process model under provided file name
    Input: dfgModel, log file, file name
    Output: N/A
    '''

    # dfg = dfg_factory.apply(log, variant="performance")
    parameters = {"format": "svg"}
    gviz = dfg_vis_factory.apply(
                                dfgModel, log=log,
                                variant="frequency",
                                parameters=parameters
                                )
    dfg_vis_factory.save(gviz, filename)


def generate_process_model(log):
    '''
    Description: to generate graphical process model in
                .svg format using pm4py library function
    Used: generate process model under provided log
    Input: log file
    Output: Display process model
    '''

    dfg = dfg_factory.apply(log)
    '''To decorate DFG with the frequency of activities'''
    gviz = dfg_vis_factory.apply(dfg, log=log, variant="frequency")
    dfg_vis_factory.view(gviz)
    return dfg
