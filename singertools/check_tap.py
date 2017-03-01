#!/usr/bin/env python3

import argparse
import attr
import singer
import subprocess
import sys
from terminaltables import AsciiTable

@attr.s
class StreamAcc(object):

    name = attr.ib()
    num_records = attr.ib(default=0)
    num_schemas = attr.ib(default=0)
    latest_schema = attr.ib(default=None, repr=False)


@attr.s
class OutputSummary(object):

    streams = attr.ib(default={})
    num_states = attr.ib(default=0)
    
    def ensure_stream(self, stream_name):
        if stream_name not in self.streams:
            self.streams[stream_name] = StreamAcc(stream_name)
        return self.streams[stream_name]
    
    def add(self, message):
        if isinstance(message, singer.RecordMessage):
            self.ensure_stream(message.stream).num_records += 1

        elif isinstance(message, singer.SchemaMessage):
            self.ensure_stream(message.stream).num_schemas += 1

        elif isinstance(message, singer.StateMessage):
            self.latest_state = message.value
            self.num_states += 1

    def num_records(self):
        return sum([stream.num_records for stream in self.streams.values()])

    def num_schemas(self):
        return sum([stream.num_schemas for stream in self.streams.values()])    

    def num_messages(self):
        return self.num_records() + self.num_schemas() + self.num_states


def summarize_output(output):
    summary = OutputSummary()
    for line in output:
        summary.add(singer.parse_message(line))
    return summary


def print_summary(summary):

    print('The output is valid.')
    print('It contained {} messages for {} streams.'.format(summary.num_messages(), len(summary.streams)))
    print('')
    print('{:7} schema messages'.format(summary.num_schemas()))
    print('{:7} record messages'.format(summary.num_records()))
    print('{:7} state messages'.format(summary.num_states))
    print('')
    print('Details by stream:')
    headers = [['stream', 'records', 'schemas']]
    rows = [[s.name, s.num_records, s.num_schemas] for s in summary.streams.values()]
    data = headers + rows

    table = AsciiTable(data)
    print(table.table)


def check_with_no_state(args):
    return summarize_output(subprocess.check_output([args.tap, '--config', args.config]))
    

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-t',
        '--tap',
        help='Tap program to execute')
    
    parser.add_argument(
        '-c',
        '--config',
        help='Config file for tap')

    args = parser.parse_args()

    if args.tap:
        if args.config:
            print('Checking tap {} with config {}'.format(args.tap, args.config))
            summary = check_with_no_state(args)
        else:
            print('If you provide --taps you must also provide --config')
            exit(1)
    else:
        print('Checking stdin for valid Singer-formatted data')
        summary = summarize_output(sys.stdin)

    print_summary(summary)


if __name__ == '__main__':
    main()
