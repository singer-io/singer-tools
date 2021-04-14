#!/usr/bin/env python3

import argparse
import os
import json
import sys
import dateutil.parser


def add_observation(acc, path):

    node = acc
    for i in range(0, len(path) - 1):
        k = path[i]
        if k not in node:
            node[k] = {}
        node = node[k]

    node[path[-1]] = True

# pylint: disable=too-many-branches
def add_observations(acc, path, data):
    if isinstance(data, dict):
        for key in data:
            add_observations(acc, path + ["object", key], data[key])
    elif isinstance(data, list):
        for item in data:
            add_observations(acc, path + ["array"], item)
    elif isinstance(data, str):
        # If the string parses as a date, add an observation that its a date
        try:
            # Parse it as an ISO-8601 date to avoid some kinds of false positives
            data = dateutil.parser.isoparse(data)
        except (dateutil.parser.ParserError, OverflowError, ValueError):
            data = None
        if data:
            add_observation(acc, path + ["date"])
        else:
            add_observation(acc, path + ["string"])

    elif isinstance(data, bool):
        add_observation(acc, path + ["boolean"])
    elif isinstance(data, int):
        add_observation(acc, path + ["integer"])
    elif isinstance(data, float):
        add_observation(acc, path + ["number"])
    elif data is None:
        add_observation(acc, path + ["null"])
    else:
        raise Exception("Unexpected value " + repr(data) + " at path " + repr(path))

    return acc

def to_json_schema(obs):
    result = {'type': ['null']}

    for key in obs:

        if key == 'object':
            result['type'] += ['object']
            if 'properties' not in result:
                result['properties'] = {}
                for obj_key in obs['object']:
                    result['properties'][obj_key] = to_json_schema(obs['object'][obj_key])

        elif key == 'array':
            result['type'] += ['array']
            result['items'] = to_json_schema(obs['array'])

        elif key == 'date':
            result['type'] += ['string']
            result['format'] = 'date-time'
        elif key == 'string':
            result['type'] += ['string']

        elif key == 'boolean':
            result['type'] += ['boolean']

        elif key == 'integer':
            result['type'] += ['integer']

        elif key == 'number':
            # Use type=string, format=singer.decimal
            result['type'] += ['string']
            result['format'] = 'singer.decimal'

        elif key == 'null':
            pass

        else:
            raise Exception("Unexpected data type " + key)

    return result


def infer_schemas(record_inputs, out_dir):
    """
    The main logic that iterates record_inputs and prints the resulting
    inferred schema to either outdir or stdout
    """
    streams = {}

    for line in record_inputs:
        rec = json.loads(line)
        if rec['type'] == 'RECORD':
            stream = rec['stream']
            if stream not in streams:
                streams[stream] = {}
            streams[stream] = add_observations(streams[stream], [], rec['record'])

    for stream, observations in streams.items():
        if out_dir:
            if not os.path.exists(out_dir):
                os.makedirs(out_dir)

            out_file = os.path.join(out_dir, "{}.inferred.json".format(stream))
            with open(out_file, 'w') as file:
                file.write(json.dumps(to_json_schema(observations), indent=2))
        else:
            # This is less useful now when used with more than one stream in the input
            print(json.dumps(to_json_schema(observations), indent=2))


def main():
    parser = argparse.ArgumentParser()

    # records defaults to stdin or otherwise expects iterable strings
    parser.add_argument(
        '-r', '--records',
        help='Iterable Records',
        required=False,
        default=sys.stdin)

    # out-dir redirects inferred schemas to a directory with naming "<stream>.inferred.json"
    parser.add_argument(
        '-o', '--out-dir',
        help='Output directory',
        required=False)
    parsed = parser.parse_args()

    infer_schemas(parsed.records, parsed.out_dir)
