#!/usr/bin/env python3

import argparse
import copy
from datetime import datetime
import json
import os
import subprocess
from subprocess import Popen
import sys
import threading

from strict_rfc3339 import rfc3339_to_timestamp
import attr
from jsonschema import Draft4Validator, validators, FormatChecker
import singer

from terminaltables import AsciiTable



WORKING_DIR_NAME = 'singer-check-tap-data'


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for error in validate_properties(validator, properties, instance, schema):
            yield error

        for prop, subschema in properties.items():
            if "format" in subschema:
                if subschema['format'] == 'date-time' and instance.get(prop) is not None:
                    try:
                        datetime.utcfromtimestamp(rfc3339_to_timestamp(instance[prop]))
                    except Exception:
                        raise Exception('Error parsing property {}, value {}'
                                        .format(prop, instance[prop]))

    return validators.extend(validator_class, {"properties": set_defaults})


@attr.s # pylint: disable=too-few-public-methods
class StreamAcc(object):

    name = attr.ib()
    num_records = attr.ib(default=0)
    num_schemas = attr.ib(default=0)
    latest_schema = attr.ib(default=None, repr=False)


@attr.s
class OutputSummary(object):

    streams = attr.ib(default=attr.Factory(dict))
    num_states = attr.ib(default=0)

    def __init__(self):
        self.latest_state = None

    def ensure_stream(self, stream_name):
        if stream_name not in self.streams: # pylint: disable=unsupported-membership-test
            self.streams[stream_name] = StreamAcc(stream_name) # pylint: disable=unsubscriptable-object
        return self.streams[stream_name] # pylint: disable=unsubscriptable-object

    def add(self, message):
        if isinstance(message, singer.RecordMessage):
            stream = self.ensure_stream(message.stream)
            if stream.latest_schema:
                validator_fn = extend_with_default(Draft4Validator)
                validator = validator_fn(
                    stream.latest_schema, format_checker=FormatChecker())
                validator.validate(copy.deepcopy(message.record))
            else:
                print('I saw a record for stream {} before the schema'.format(
                    message.stream))
                exit(1)
            stream.num_records += 1

        elif isinstance(message, singer.SchemaMessage):
            stream = self.ensure_stream(message.stream)
            stream.num_schemas += 1
            stream.latest_schema = message.schema

        elif isinstance(message, singer.StateMessage):
            self.latest_state = message.value
            self.num_states += 1

    def num_records(self):
        return sum([stream.num_records for stream in self.streams.values()]) # pylint: disable=no-member

    def num_schemas(self):
        return sum([stream.num_schemas for stream in self.streams.values()]) # pylint: disable=no-member

    def num_messages(self):
        return self.num_records() + self.num_schemas() + self.num_states


class StdoutReader(threading.Thread):

    def __init__(self, process):
        self.process = process
        self.summary = None
        super().__init__()

    def run(self):
        self.summary = summarize_output(self.process.stdout)

    def finish_reading_logs(self):
        """Joins the thread with a timeout.

        Intended to be called on the parent thread.
        """
        print('Joining on thread {}'.format(self.name))
        self.join(timeout=5)
        if self.is_alive():
            print(
                'Thread {} did not finish within timeout'.format(self.name))
        else:
            print('Thread {} finished'.format(self.name))


def summarize_output(output):
    summary = OutputSummary()
    for line in output:
        summary.add(singer.parse_message(line))
    return summary


def print_summary(summary):

    print('The output is valid.')
    print('It contained {} messages for {} streams.'.format(
        summary.num_messages(), len(summary.streams)))
    print('')
    print('{:7} schema messages'.format(summary.num_schemas()))
    print('{:7} record messages'.format(summary.num_records()))
    print('{:7} state messages'.format(summary.num_states))
    print('')
    print('Details by stream:')
    headers = [['stream', 'records', 'schemas']]
    rows = [[s.name, s.num_records, s.num_schemas]
            for s in summary.streams.values()]
    data = headers + rows

    table = AsciiTable(data)
    print(table.table)


def run_and_summarize(tap, config, state=None, debug=False):
    cmd = [tap, '--config', config]
    if state:
        cmd += ['--state', state]
    print('Running command {}'.format(' '.join(cmd)))

    stderr = None if debug else subprocess.DEVNULL
    tap = Popen(cmd,
                stdout=subprocess.PIPE,
                stderr=stderr,
                bufsize=1,
                universal_newlines=True)
    summarizer = StdoutReader(tap)
    summarizer.start()
    returncode = tap.wait()
    if returncode != 0:
        print('ERROR: tap exited with status {}'.format(returncode))
        exit(1)

    return summarizer.summary


def check_with_no_state(args):
    return run_and_summarize(args.tap, args.config, debug=args.debug)


def check_with_state(args, state):
    state_path = os.path.join(WORKING_DIR_NAME, 'state.json')
    with open(state_path, mode='w') as state_file:
        json.dump(state, state_file)
    return run_and_summarize(
        args.tap, args.config, state=state_path, debug=args.debug)


def main():

    parser = argparse.ArgumentParser(
        description='''Verifies that a Tap conforms to the Singer
        specification.''',
        epilog='''If a --tap argument is provided, this program will
        exit zero if the Tap exits zero and produces valid output, or
        non-zero if the tap exits non-zero or if the output it
        produces is invalid. If no --tap is provided, exits zero if
        the data on stdin is valid, non-zero otherwise.''')

    parser.add_argument(
        '-t',
        '--tap',
        help='''Tap program to execute. If provided, I'll run this tap
        and check its output. Otherwise, I'll read from stdin.''')

    parser.add_argument(
        '-c',
        '--config',
        help='Config file for tap. Only used of --tap is also specified.')

    parser.add_argument(
        '-d',
        '--debug',
        action='store_true',

        help='''Turn on debugging. Show log output from tap. By default
        logging output from tap is suppressed.''')

    args = parser.parse_args()

    try:
        os.mkdir(WORKING_DIR_NAME)
    except FileExistsError:
        pass

    if args.tap:
        if not args.config:
            print('If you provide --taps you must also provide --config')
            exit(1)

    if args.tap:
        print('Checking tap {} with config {}'.format(args.tap, args.config))
        summary = check_with_no_state(args)
    else:
        print('Checking stdin for valid Singer-formatted data')
        summary = summarize_output(sys.stdin)

    print_summary(summary)

    if args.tap:
        if summary.latest_state:
            print('')
            print('')
            print('Now re-running tap with state produced by previous run')
            summary = check_with_state(args, summary.latest_state)
            print_summary(summary)

if __name__ == '__main__':
    main()
