import json
import argparse
import os
import sys
import log_filtering.utils as utils


def print_traces_stamps(traces, stamps, message):
    """
    desc    print the traces and timestamps in the format
    Input   traces, timestamps, message
    output  n/a (just printing the inputs in a clean manner)
    """
    print("\n\n{}\n".format(message), traces, "\n")
    for i in range(len(traces)):
        if type(stamps[i]) == list:
            print(f'{traces[i]:40}  {stamps[i][0]} \t {stamps[i][1]}')
        else:
            print(f'{traces[i]:40}  {stamps[i]}')


def read_log(logs):
    """
    desc    read and concatenate the traces and timestamps from the log
    Input   logs
    output  con_traces , con_stamps
    NOTE    concatenated == con_
    """
    con_traces = []
    con_timestamps = []
    activity = logs.classifiers['activity classifier']
    timestamp = logs.classifiers['timestamp']

    for log in logs:
        for l in log:
            con_traces.append(l[activity])
            con_timestamps.append(l[timestamp])
        con_traces.append("|")
        con_timestamps.append("|")
    return con_traces, con_timestamps


def read_pattern_file(file):
    """
    desc    read the pattern file and create the dictionary
    Input   file (pattern file name)
    output  pattern_dic

    """
    try:
        json_data = open(file, "r").read()
        pattern_information = json.loads(json_data)

    except:
        print('cannot open the pattern file', file, 'please check again')
        return

    pattern_dic = {}
    for row in pattern_information:
        idx = str(row['ID'])
        pattern_dic[idx] = {}
        pattern_dic[idx]['Name'] = row['Name']
        pattern_dic[idx]['Pattern'] = row['Pattern']

    return pattern_dic


def check_pattern(patterns, pattern_dic):
    """
    desc    check if the your input on the pattern exist in the pattern file
    Input   patterns, pattern_dic
    output  True or False
    """
    # print(patterns, pattern_dic)
    for pattern in patterns:
        try:
            pattern_dic[pattern]

        except:
            print("the list of the pattern in pattern file")
            for pd in pattern_dic:
                print(pd, pattern_dic[pd]['Name'], pattern_dic[pd]['Pattern'])
            print(
                "\nSome of your input",
                ','.join(patterns),
                "Not in pattern file. Ref. to the above, please try again"
            )
            return False
    return True


def perform_abstraction(
                    pattern,
                    abstraction,
                    con_traces,
                    con_timestamps,
                    start=0
):
    """
    desc    the pattern in traces are abstracted
    Input   pattern                     pattern to be abstracted
            abstraction                 the abstraction replacing the pattern
            con_traces                  concatenated traces for abstraction
            con_timestamps,             concatenated timestamps for abstraction
            start=0                     index number to start to search
    output  (abstracted) con_traces, con_stamps
    example
                con_traces              : abcabc
                con_timestamps          : 1may,2may,3may,4may,5may,6may
                pattern                 : abc
                abstraction             : Group1

                Abstration (abc => Group1)
                con_traces              : Group1Group1
                con_timestamps          : 1may, 4may
    """

    try:
        print("in abstraction = ", pattern[0])
        idx = con_traces.index(pattern[0], start)

    # if idx does not exist, error occur
    except:
        return con_traces, con_timestamps,

    # print(con_traces[idx:idx+len(pattern)], pattern, idx )

    # if found in the pattern, it replaced with the abstraction
    if con_traces[idx:idx+len(pattern)] == pattern:

        # the first timestamp of the activities will represent the group
        group_time = [
            con_timestamps[idx],
            con_timestamps[idx+len(pattern)-1]
        ]
        del con_traces[idx:idx+len(pattern)]
        del con_timestamps[idx:idx+len(pattern)]
        con_traces.insert(idx, abstraction)
        con_timestamps.insert(idx, group_time)

        # then recursive call for further abstraction
        con_traces, con_timestamps = perform_abstraction(
                                        pattern,
                                        abstraction,
                                        con_traces,
                                        con_timestamps,
                                        start=0
                                    )

    # if pattern is not matched, to further search (start position = idx + 1)
    else:
        con_traces, con_timestamps = perform_abstraction(
                                        pattern,
                                        abstraction,
                                        con_traces,
                                        con_timestamps,
                                        start=idx+1
                                    )

    return con_traces, con_timestamps


def perform_abstractions(
        abs_sequence,
        pattern_dic,
        con_traces,
        con_timestamps
):
    """
    desc    run the perform_abstraction multiple times through the loop
    Input   abs_sequence, pattern_dic, con_traces, con_timestamps
    output  (abstracted) con_traces, con_stamps

    """
    print("in print_abstractions")
    pattern_dic_array = {}
    for row in pattern_dic:
        idx = str(row['ID'])
        pattern_dic_array[idx] = {}
        pattern_dic_array[idx]['Name'] = row['Name']
        pattern_dic_array[idx]['Pattern'] = row['Pattern']

    pattern_dic = pattern_dic_array
    print(pattern_dic)

    for seq in abs_sequence:
        pattern = pattern_dic[str(seq)]
        print(pattern['Name'], pattern['Pattern'])
        con_traces, con_timestamps = perform_abstraction(
            pattern['Pattern'],
            pattern['Name'],
            con_traces,
            con_timestamps
        )
        # print(con_traces)
    return con_traces, con_timestamps


def check_if_xes(file):
    """
    Desc.   check if the given file is xes or not
    Used    in add_argument, main(), abstraction.py
    Input   file, filename given by the user
    Output  raise error for non xes, else return file
    """
    if not (file.lower().endswith(".xes") | file.lower().endswith(".csv")):
        msg = "%s is not the XES/CSV file" % file
        raise argparse.ArgumentTypeError(msg)
    return file


def get_traces_from_log(log):
    """
    Desc.   read the traces from the log
    Used    perform_pattern_abstraction(), abstraction_suppot_functions.py
    Input   log, object of log imported by PM4py
    Output  list of traces

    BY SAUD
    """
    traces = []
    for trace in log:
        t = [l['Activity'] for l in trace]
        traces.append(t)
    return traces
