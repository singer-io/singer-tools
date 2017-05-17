import json
import argparse
import difflib

def load_jsonl_file(file_path):
    with open(file_path) as file_obj:
        lines = [json.loads(line) for line in file_obj.readlines()]
    return lines

def prettify(lines):
    pretty_lines = [json.dumps(line, sort_keys=True, indent=4) for line in lines]
    pretty_lines = sorted(pretty_lines)
    return '\n'.join(pretty_lines)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("file1")
    parser.add_argument("file2")
    args = parser.parse_args()

    lines1 = load_jsonl_file(args.file1)
    lines2 = load_jsonl_file(args.file2)

    pretty_lines1 = prettify(lines1)
    pretty_lines2 = prettify(lines2)


    for line in difflib.context_diff(pretty_lines1.splitlines(), pretty_lines2.splitlines(),
                                     fromfile=args.file1, tofile=args.file2):
        print(line)
