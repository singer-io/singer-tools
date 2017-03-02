# singer-tools
Tools for working with Singer Taps and Targets

* `singer-check-tap` - validates Tap output
* `singer-infer-schema` - infers a json-schema from Tap output

# Installation

This package can be installed with pip:

```
$ pip install singer-tools
```

# Tools

## singer-check-tap

You can use `singer-check-tap` to check whether a Tap conforms to the
Singer specification.

### Checking a tap

If you run `singer-check-tap` and provide a path to a Tap (with the
`--tap` option) and a configuration for that Tap, it will do the following:

1. Run the tap with the specified config and no `--state` option
2. Validate the output the tap produces
3. Check the exit status of the tap
4. Capture the final state produced by the Tap and save it to a file
5. Run the tap again, this time with a `--state` arg pointing to the final state produced by the first invocation
6. Validate the output the tap produces
7. Check the exit status

If all of the invocations of the Tap succeed (exit with status 0) and if
the output of the Tap conforms to the specification, this program will
exit with status 0. If any of the invocations of the Tap fail (exit
non-zero) or produce output that does not conform to the specification,
this program will print an error message and exit with a non-zero status.

### Checking output of a tap

Sometimes it's convenient to validate the output of a tap, rather have
`singer-check-tap` actually run the tap. You can do that by omitting the
`--tap` argument and providing the Tap output on STDIN. For example:

```bash
my-tap --config config.json | singer-check-tap
```

In this mode of operation, `singer-check-tap` will just validate the data
on stdin and exit with a status of zero if it's valid or non-zero
otherwise.

### Sample data

You can try `singer-check-tap` out on the data in the `samples` directory.

#### A good run:

```
$ singer-check-tap < samples/fixerio-valid-initial.json
Checking stdin for valid Singer-formatted data
The output is valid.
It contained 17 messages for 1 streams.

      1 schema messages
     15 record messages
      1 state messages

Details by stream:
+---------------+---------+---------+
| stream        | records | schemas |
+---------------+---------+---------+
| exchange_rate | 15      | 1       |
+---------------+---------+---------+
```

#### A bad run:

```
$ singer-check-tap < samples/fixerio-invalid-no-key-properties.json 
Checking stdin for valid Singer-formatted data
Traceback (most recent call last):
  File "/opt/code/singer-tools/venv/bin/singer-check-tap", line 11, in <module>
    load_entry_point('singer-tools', 'console_scripts', 'singer-check-tap')()
  File "/opt/code/singer-tools/singertools/check_tap.py", line 195, in main
    summary = summarize_output(sys.stdin)
  File "/opt/code/singer-tools/singertools/check_tap.py", line 90, in summarize_output
    summary.add(singer.parse_message(line))
  File "/opt/code/singer-tools/venv/lib/python3.4/site-packages/singer_python-0.2.1-py3.4.egg/singer/__init__.py", line 117, in parse_message
    key_properties=_required_key(o, 'key_properties'))
  File "/opt/code/singer-tools/venv/lib/python3.4/site-packages/singer_python-0.2.1-py3.4.egg/singer/__init__.py", line 101, in _required_key
    k, msg))
Exception: Message is missing required key 'key_properties': {'stream': 'exchange_rate', 'schema': {'properties': {'date': {'format': 'date-time', 'type': 'string'}}, 'additionalProperties': True, 'type': 'object'}, 'type': 'SCHEMA'}
```

## infer-schema

If the data source you're using does not publish a schema, you can use
`infer-schema` to parse a sample of JSON-formatted data and produce a
basic schema.

```bash
$ singer-infer-schema < data.json > schema.json
```

You should not consider the resulting schema to be complete. It's only
intended to be a starting point, and will likely require manual editing.
But it's probably easier than writing a schema from scratch.

License
-------

Copyright © 2017 Stitch

Distributed under the Apache License Version 2.0
