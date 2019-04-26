#!/usr/bin/env python3

from collections import Counter
import json
import sys
from terminaltables import AsciiTable


NUM_LEVELS = 3
NUM_TO_PRINT_PER_LEVEL = 20

def get_paths_from_rec(rec, path_to_rec):
    unique_fields = set()
    for this_key in rec.keys():
        this_path = path_to_rec + "/" + this_key
        unique_fields.add(this_path)
        if isinstance(rec[this_key],dict):
            unique_fields = unique_fields.union(get_paths_from_rec(rec[this_key], this_path))
        elif isinstance(rec[this_key], list):
            for list_entry in rec[this_key]:
                if isinstance(list_entry, dict):
                    unique_fields = unique_fields.union(get_paths_from_rec(list_entry, this_path))
    return unique_fields

def get_counts(unique_fields, level):
    split_fields = [f.split('/') for f in unique_fields]
    nested_fields = [f for f in split_fields if len(f) > level]
    nested_fields_level = ['/'.join(f[1:(level+1)]) for f in nested_fields]
    return dict(Counter(nested_fields_level))

def print_summary(unique_fields):
    count_level_map = {}
    print('=====================================================')
    for level in range(0,(NUM_LEVELS+1)):

        if level != 0:
            print('\nLevel ' + str(level))
        counts = get_counts(unique_fields, level)
        sorted_counts = sorted(counts.items(), key=lambda x: x[1], reverse=True)
        num_sorted_output = 0

        if level == 0:
            print("Total Fields: " + str(sorted_counts[0][1]))            
        else:
            headers = [['Path', 'Num Nested Fields']]
            rows = [[f[0], f[1]] for f in sorted_counts[0:(NUM_TO_PRINT_PER_LEVEL+1)]]
            data = headers + rows
            table = AsciiTable(data)
            print(table.table)
        
    print('=====================================================')
        
def main():
    num_recs = 0
    unique_fields = set()
    for line in sys.stdin:
       rec = json.loads(line)
       if rec['type'] == 'RECORD':
           rec_unique_fields = get_paths_from_rec(rec['record'], "")
           unique_fields = unique_fields.union(rec_unique_fields)
           num_recs += 1
    print_summary(unique_fields)
