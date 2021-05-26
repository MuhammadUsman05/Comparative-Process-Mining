import argparse
import csv
import getopt
import os
import sys

from pm4py.objects.log.importer.xes import importer as xes_import_factory

import log_filtering.utils as utils
from log_filtering.abstraction_support_functions import *


def generate_transformed_log_XES(
                            original_file, abstracted_patterns,
                            abstracted_timestamps, transformed_file
                            ):
    """
    Desc.   generate transformed log with abstraction of traces in xes format
    Used    gather and format log contents and return final content with
            artificial case ids for filter it further
    Input   original log file to copy top content, abstracted patterns,
    abstracted timestamps, filename used to transform it
    Output  content of transformed log file
    """
    transformed_log_content = ""
    file1 = open(transformed_file, "w")
    try:

        islogComplete = False
        trace_contains_events = False

        # We do not have case ids in our scnerios, so it must autoincremented here (Non-issues).
        case_id = 1

        # remove last element '|' from both lists
        del abstracted_timestamps[-1]
        del abstracted_patterns[-1]

        if (original_file.endswith('.csv') or original_file.endswith('.CSV')) or (original_file.endswith('.xes') or original_file.endswith('.XES')):
            # referring from test.xes
            """<log xes.version='1.0' xes.features='nested-attributes' openxes.version='1.0RC7'>"""
            transformed_log_content = str(
                    '''<?xml version="1.0" encoding="UTF-8" ?>\n'''
                    '''<log xes.version="1.0" xmlns="http://code.deckfour.org/xes" xes.creator="Fluxicon Nitro">\n'''
                    '''\t<extension name="Concept" prefix="concept" uri="http://www.xes-standard.org/concept.xesext"/>\n'''
                    '''\t<extension name="Time" prefix="time" uri="http://www.xes-standard.org/time.xesext"/>\n'''
                    '''\t<extension name="Lifecycle" prefix="lifecycle" uri="http://www.xes-standard.org/lifecycle.xesext"/>\n'''
                    '''\t<global scope="trace">\n'''
                    '''\t\t<string key="concept:name" value=""/>\n'''
                    '''\t</global>\n'''
                    '''\t<classifier name="Event Name" keys="concept:name"/>\n'''
                    '''\t<classifier name="(Event Name AND Lifecycle transition)" keys="concept:name lifecycle:transition"/>\n'''
                    '''\t<string key="concept:name" value="XES Event Log"/>\n''')

        # for first trace only
        transformed_log_content = \
            transformed_log_content + '''\t<trace>\n'''
        if (len(abstracted_patterns) != 0):
            transformed_log_content = \
                transformed_log_content + '''\t\t<string key="concept:name" ''' \
                '''value="{case_id}"/>\n'''.format(case_id=case_id)
            case_id = case_id + 1

        for index, activity in enumerate(abstracted_patterns):
            if (
                '|' not in abstracted_patterns[index] or
                abstracted_patterns[index] != '|'
            ):
                # To check if there are two timestamps: start and end time
                if type(abstracted_timestamps[index]) == list:

                    transformed_log_content = transformed_log_content + \
                        str(
                            '''\t\t<event>\n'''
                            '''\t\t\t<string key="concept:name" '''
                            '''value="{abs_patt}"/>\n'''
                            '''\t\t\t<string key="lifecycle:transition" '''
                            '''value="start"/>\n'''
                            '''\t\t\t<date key="time:timestamp" '''
                            '''value="{abs_tmp_start}"/>\n'''
                            '''\t\t</event>\n'''
                            '''\t\t<event>\n'''
                            '''\t\t\t<string key="concept:name" '''
                            '''value="{abs_patt}"/>\n'''
                            '''\t\t\t<string key="lifecycle:transition" '''
                            '''value="complete"/>\n'''
                            '''\t\t\t<date key="time:timestamp" '''
                            '''value="{abs_tmp_complete}"/>\n'''
                            '''\t\t</event>\n'''
                            .format(
                                    abs_patt=abstracted_patterns[index],
                                    abs_tmp_start=abstracted_timestamps[index][0],
                                    abs_tmp_complete=abstracted_timestamps[index][1]
                                    ))
                else:
                    transformed_log_content = transformed_log_content + \
                        str(
                            '''\t\t<event>\n'''
                            '''\t\t\t<string key="concept:name" '''
                            '''value="{abs_patt}"/>\n'''
                            '''\t\t\t<string key="lifecycle:transition" '''
                            '''value="start"/>\n'''
                            '''\t\t\t<date key="time:timestamp" '''
                            '''value="{abs_tmp_start}"/>\n'''
                            '''\t\t</event>\n'''
                            '''\t\t<event>\n'''
                            '''\t\t\t<string key="concept:name" '''
                            '''value="{abs_patt}"/>\n'''
                            '''\t\t\t<string key="lifecycle:transition" '''
                            '''value="complete"/>\n'''
                            '''\t\t\t<date key="time:timestamp" '''
                            '''value="{abs_tmp_complete}"/>\n'''
                            '''\t\t</event>\n'''
                            .format(
                                    abs_patt=abstracted_patterns[index],
                                    abs_tmp_start=abstracted_timestamps[index],
                                    abs_tmp_complete=abstracted_timestamps[index]
                                    ))

            else:
                transformed_log_content = \
                    transformed_log_content + '''\t</trace>\n''' \
                    '''\t<trace>\n''' \
                    '''\t\t<string key="concept:name" ''' \
                    '''value="{case_id}"/>\n'''.format(case_id=case_id)   # to get value next to |
                case_id = case_id + 1

        # for last trace only
        transformed_log_content = \
            transformed_log_content + '''\t</trace>\n'''

        transformed_log_content = \
            transformed_log_content + '''</log>\n'''
        islogComplete = True
        file1.write(transformed_log_content)

    except Exception as e:
        print("Exception!!!... -> " + str(e))

    # Release used resources
    file1.close()
    return transformed_log_content


def generate_transformed_log_CSV(
                            original_file, abstracted_patterns,
                            abstracted_timestamps, transformed_file
                            ):
    """
    Desc.   generate transformed log with abstraction of traces in csv format
    Used    gather and format log contents and return final content
    Input   original log file to copy top headers, abstracted patterns,
    abstracted timestamps, filename used to transform it
    Output  content of transformed log file
    """
    try:
        transformed_log_content = [[]]
        case_number = 1

        # remove last element '|' from both lists
        del abstracted_timestamps[-1]
        del abstracted_patterns[-1]

        transformed_log_content = [["case:concept:name", "Start Timestamp", "Complete Timestamp", "Activity"]]

        with open(transformed_file, 'w', newline='') as file2:
            writer = csv.writer(file2)
            writer.writerow(["case:concept:name", "Start Timestamp",
                            "Complete Timestamp", "Activity"])

            for index, activity in enumerate(abstracted_patterns):
                if (
                        '|' not in abstracted_patterns[index] or
                        abstracted_patterns[index] != '|'):

                    # To check if there are two timestamps: start and end time
                    if type(abstracted_timestamps[index]) == list:
                        writer.writerow([case_number, abstracted_timestamps[index][0], abstracted_timestamps[index][1], activity])
                        transformed_log_content = \
                            transformed_log_content + [[str(case_number), str(abstracted_timestamps[index][0]), str(abstracted_timestamps[index][1]), activity]]
                    else:
                        # if no abstraction is possible then start and end timestamps of activity are same
                        writer.writerow([case_number, abstracted_timestamps[index], abstracted_timestamps[index], activity])
                        transformed_log_content = \
                            transformed_log_content + [[str(case_number), str(abstracted_timestamps[index]), str(abstracted_timestamps[index]), activity]]
                else:
                    case_number = case_number + 1

        return transformed_log_content

    except Exception as e:
        print("Exception!!!... -> " + str(e))

    # Release used resources
    file1.close()


def perform_transformation(event_log,
                           export_log,
                           export_model,
                           patterns):
    """
    Desc.   Perform all transformation steps and generate transformed log and model
    Used    call from main.py, provided by command line args
    Input:
        --event_log (designated path along with filename),
        --downloadLog (to export log)
        --downModel (to export process model)
        --pattern (specify the sequence of the pattern in order ),

    Output  displays process model and / or export transformed log/model
    """
    try:
        ext = "json"
        transformed_filename = ""
        exported_transformed_filename = ""
        transformed_log = None

        # This file contains tandem arrays and maximal repeats sets
        filename = event_log.replace(".xes", "_patterns." + ext) \
                            .replace(".XES", "_patterns." + ext) \
                            .replace(".csv", "_patterns." + ext) \
                            .replace(".CSV", "_patterns." + ext) \
                            .replace("_transformed_patterns." + ext, "_patterns." + ext)

        filepath = os.path.dirname(event_log)

        file = os.path.basename(event_log)
        name = file.split('.')[0]

        if event_log.endswith('.xes') or event_log.endswith('.XES'):
            log = utils.import_log_XES(event_log)
        elif event_log.endswith('.csv') or event_log.endswith('.CSV'):
            log = utils.import_csv(event_log)

        # defining file names
        if (event_log.endswith('.xes') or event_log.endswith('.XES')) or (event_log.endswith('.csv') or event_log.endswith('.CSV')):

            if '_transformed' not in event_log:

                transformed_filename = \
                    filepath + '\\' + name + "_transformed.XES"
                display_name = name + "_transformed.XES"

                exported_transformed_filename = \
                    filepath + '\\' + \
                    name + "_transformed_exported.XES"
                display_name_exported = name + "_transformed_exported.XES"

                transformed_model_name = \
                    filepath + '\\' + name + "_transformed.svg"
                display_name_model = name + "_transformed.svg"

                exported_transformed_model_name = \
                        filepath + '\\' + \
                        name + "_transformed_exported.svg"
                display_name_model_exported = name + "_transformed_exported.svg"

            else:
                transformed_filename = \
                    filepath + '\\' + name + ".XES"
                display_name = name + "_transformed.XES"

                exported_transformed_filename = \
                    filepath + '\\' + \
                    name + "_exported.XES"
                display_name_exported = name + "_exported.XES"

                transformed_model_name = \
                    filepath + '\\' + name + ".svg"
                display_name_model = name + ".svg"

                exported_transformed_model_name = \
                    filepath + '\\' + \
                    name + "_exported.svg"
                display_name_model_exported = name + "_exported.svg"

        # perform abtsraction with filename_patterns.json.
        pattern_dic = utils.import_pattern_json(filename)
        # read the activities and timestamps from the given log
        concatenated_traces, concatenated_timestamps = read_log(log)
        # concatenated_traces, concatenated_timestamps = read_log(log)
        abstracted_traces, abstracted_timestamps = \
            perform_abstractions(
                            patterns, pattern_dic,
                            concatenated_traces,
                            concatenated_timestamps
                            )

        # generate transformed log
        if (event_log.endswith('.xes') or event_log.endswith('.XES')) or (event_log.endswith('.csv') or event_log.endswith('.CSV')):
            # This file contains case ids but we do not require case ids in final log
            log_content = generate_transformed_log_XES(
                                                event_log,
                                                abstracted_traces,
                                                abstracted_timestamps,
                                                transformed_filename
                                                )
            log = utils.import_log_XES(transformed_filename)
            # calling this method does not contain case ids, get final log
            log_content = transform_log(log)
            with open(transformed_filename, 'w') as f:
                f.write(log_content)
            # if export log is true then it will export the latest log object without case id
            log = utils.import_log_XES(transformed_filename)
        else:
            raise

        display_message(
            '''Log is transformed'''.format(
                                    display_name
                                    ))

        # generate transformed process model
        dfg = utils.generate_process_model(log)

        if (os.path.exists(transformed_filename)):
            os.remove(transformed_filename)

        display_message("Process model is generated for transformed log (Popping up)")

        if (export_log):
            if (event_log.endswith('.xes') or event_log.endswith('.XES')) or (event_log.endswith('.csv') or event_log.endswith('.CSV')):
                utils.export_log(log, exported_transformed_filename)

            display_message(
                '''Log exported as {}'''.format(
                                                display_name_exported
                ))
        if (export_model):

            utils.export_process_model(
                dfg, log,
                exported_transformed_model_name
                )

            display_message(
                "Process Model exported as {}"
                .format(
                        display_name_model_exported
                        ))
        return True
    except Exception as e:
        print("Exception!!!... -> " + str(e))
        return False


def transform_log(log):
    """
    Desc.   Transform log having start and complete lifecycle:transition
    Used    When user pattern numbers are not provided then it is called
    Input   log
    Output  content of transformed log file
    """
    transformed_log_content = ""
    try:
        if (log is not None):
            transformed_log_content = str(
                    '''<?xml version="1.0" encoding="UTF-8" ?>\n'''
                    '''<log xes.version="1.0" xmlns="http://code.deckfour.org/xes" xes.creator="Fluxicon Nitro">\n'''
                    '''\t<extension name="Concept" prefix="concept" uri="http://www.xes-standard.org/concept.xesext"/>\n'''
                    '''\t<extension name="Time" prefix="time" uri="http://www.xes-standard.org/time.xesext"/>\n'''
                    '''\t<extension name="Lifecycle" prefix="lifecycle" uri="http://www.xes-standard.org/lifecycle.xesext"/>\n'''
                    '''\t<classifier name="Event Name" keys="concept:name"/>\n'''
                    '''\t<classifier name="(Event Name AND Lifecycle transition)" keys="concept:name lifecycle:transition"/>\n'''
                    '''\t<string key="concept:name" value="XES Event Log"/>\n''')

            for trace in log:
                transformed_log_content = \
                    transformed_log_content + '''\t<trace>\n'''

                for event in trace:
                    if ('lifecycle:transition' in event):
                        if (event['lifecycle:transition'].lower() == 'start'):
                            transformed_log_content = transformed_log_content + \
                                str(
                                    '''\t\t<event>\n'''
                                    '''\t\t\t<string key="concept:name" '''
                                    '''value="{event}"/>\n'''
                                    '''\t\t\t<string key="lifecycle:transition" '''
                                    '''value="start"/>\n'''
                                    '''\t\t\t<date key="time:timestamp" '''
                                    '''value="{timestamp_start}"/>\n'''
                                    '''\t\t</event>\n'''
                                    .format(
                                            event=event['concept:name'],
                                            timestamp_start=event['time:timestamp'],
                                            ))
                        elif (event['lifecycle:transition'].lower() == 'complete'):
                            transformed_log_content = transformed_log_content + \
                                str(
                                    '''\t\t<event>\n'''
                                    '''\t\t\t<string key="concept:name" '''
                                    '''value="{event}"/>\n'''
                                    '''\t\t\t<string key="lifecycle:transition" '''
                                    '''value="complete"/>\n'''
                                    '''\t\t\t<date key="time:timestamp" '''
                                    '''value="{timestamp_complete}"/>\n'''
                                    '''\t\t</event>\n'''
                                    .format(
                                            event=event['concept:name'],
                                            timestamp_complete=event['time:timestamp']
                                            ))
                    else:
                        transformed_log_content = transformed_log_content + \
                            str(
                                '''\t\t<event>\n'''
                                '''\t\t\t<string key="concept:name" '''
                                '''value="{event}"/>\n'''
                                '''\t\t\t<string key="lifecycle:transition" '''
                                '''value="start"/>\n'''
                                '''\t\t\t<date key="time:timestamp" '''
                                '''value="{timestamp_start}"/>\n'''
                                '''\t\t</event>\n'''
                                '''\t\t<event>\n'''
                                '''\t\t\t<string key="concept:name" '''
                                '''value="{event}"/>\n'''
                                '''\t\t\t<string key="lifecycle:transition" '''
                                '''value="complete"/>\n'''
                                '''\t\t\t<date key="time:timestamp" '''
                                '''value="{timestamp_complete}"/>\n'''
                                '''\t\t</event>\n'''
                                .format(
                                        event=event['concept:name'],
                                        timestamp_start=event['time:timestamp'],
                                        timestamp_complete=event['time:timestamp']
                                        ))
                transformed_log_content = \
                    transformed_log_content + '''\t</trace>\n'''

            transformed_log_content = \
                transformed_log_content + '''</log>'''
        return transformed_log_content

    except Exception as e:
        print("Exception!!!... -> " + str(e))
        return


def display_message(message):
    """
    Desc.   displays messages to the user after each action in a fancy way
    Used    transformation.py is executed
    Input:  message to display
    Output  N/A
    """
    print()
    print('*'*100)
    print(message)
    print('*'*100)


if __name__ == "__main__":

    """
    Desc.   runnable function from the command line
    Used    transformation.py is executed
    Input:
        --path (designated path along with filename),
        --pattern (specify the sequence of the pattern in order ),
        --downloadLog (to export log)
        --downModel (to export process model)
    Output  N/A
    """

    event_log = None
    ext = "json"
    transformed_filename = ""
    exported_transformed_filename = ""
    transformed_log = None

    try:
        parser = argparse.ArgumentParser(
            description='''To transform the logs with the pattern.
                        The --path and --pattern number are mandatory.'''
            )

        # definition of --path argument
        parser.add_argument(
            '--path',
            required=True,
            type=argparse.FileType('r'),
            metavar='xes_file_name',
            help='specify the path of xes file. e.g. test.xes'
            )

        # definition of --pattern argument
        parser.add_argument(
            '--pattern',
            type=str,
            required=True,
            metavar='pattern_ID',
            nargs='+',
            help='''Referring to the xes_file_name.pattern,
            specify the sequence of the pattern
            in order which you want to make abstractions with.
            \n e.g. 1 2 3 1 '''
        )

        # definition of --downloadLog argument
        parser.add_argument(
            '--downloadLog',
            action='store_true',
            help='flag to export/download transformed log'
            )

        # definition of --downloadModel argument
        parser.add_argument(
            '--downloadModel',
            action='store_true',
            help='flag to export/download process model'
            )

        parser.add_argument(
            '-filename',
            type=check_if_xes,
            default=parser.parse_args().path.name,
            metavar='filename',
            help=argparse.SUPPRESS
            )

        parser.add_argument(
            '-patternfile',
            type=argparse.FileType('r'),
            default=parser.parse_args().path.name
                                            .replace(".xes", "_patterns.json")
                                            .replace(".XES", "_patterns.json")
                                            .replace(".csv", "_patterns.json")
                                            .replace(".CSV", "_patterns.json"),
            metavar='patternfile',
            help=argparse.SUPPRESS
            )

        # getting the arguments by parse_args
        args = parser.parse_args()

        perform_transformation(args.path.name,
                               args.downloadLog,
                               args.downloadModel,
                               args.pattern)

    except Exception as e:
            print("Exception!!!... -> " + str(e))
