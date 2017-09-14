#!/usr/bin/env python3

import json
import sys

OBSERVED_TYPES = {}

def add_observation(path):

    node = OBSERVED_TYPES
    for i in range(0, len(path) - 1):
        k = path[i]
        if k not in node:
            node[k] = {}
        node = node[k]

    node[path[-1]] = True

def add_observations(path, data):
    if isinstance(data, dict):
        for key in data:
            add_observations(path + ["object", key], data[key])
    elif isinstance(data, list):
        for item in data:
            add_observations(path + ["array"], item)
    elif isinstance(data, str):
        add_observation(path + ["string"])
    elif isinstance(data, bool):
        add_observation(path + ["boolean"])
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
                for obj_key in obs['object']:
                    result['properties'][obj_key] = to_json_schema(obs['object'][obj_key])

        elif key == 'array':
            result['type'] += ['array']
            result['items'] = to_json_schema(obs['array'])

        elif key == 'string':
            result['type'] += ['string']

        elif key == 'boolean':
            result['type'] += ['boolean']

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

    print(json.dumps(to_json_schema(OBSERVED_TYPES), indent=2))
