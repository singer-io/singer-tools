#!/usr/bin/env python3

import json
import sys
import pprint
import json

past_headers = False
observed_types = {}

def add_observation(path):

    global observed_types
    node = observed_types
    for i in range(0, len(path) - 1):
        k = path[i]
        if k not in node:
            node[k] = {}
        node = node[k]

    node[path[-1]] = True

pp = pprint.PrettyPrinter(indent=4)
    
def add_observations(path, data):
    if isinstance(data, dict):
        for key in data:
            add_observations(path + ["object", key], data[key])
    elif isinstance(data, list):
        for item in data:
            add_observations(path + ["array"], item)
    elif isinstance(data, str):
        add_observation(path + ["string"])
    elif isinstance(data, int):
        add_observation(path + ["integer"])
    elif isinstance(data, float):
        add_observation(path + ["number"])
    elif data is None:
        add_observation(path + ["null"])
    else:
        raise Exception("Unexpected value " + repr(data) + " at path " + repr(path))

def to_json_schema(obs):
    result = {'type': ['null']}

    for key in obs:

        if key == 'object':
            result['type'] += ['object']
            if 'properties' not in result:
                result['properties'] = {}
                for key in obs['object']:
                    result['properties'][key] = to_json_schema(obs['object'][key])

        elif key == 'array':
            result['type'] += ['array']
            result['items'] = to_json_schema(obs['array'])

        elif key == 'string':
            result['type'] += ['string']

        elif key == 'integer':
            result['type'] += ['integer']

        elif key == 'number':
            result['type'] += ['number']

        elif key == 'null':
            pass

        else:
            raise Exception("Unexpected data type " + key)
        
    return result


def main():
    for line in sys.stdin:
        rec = json.loads(line)
        if rec['type'] == 'RECORD':
            add_observations([], rec['record'])

    print(json.dumps(to_json_schema(observed_types), indent=2))
