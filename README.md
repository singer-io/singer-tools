# singer-tools
Tools for working with Singer Taps and Targets

* `singer-check-tap` - validates Tap output
* `singer-infer-schema` - infers a json-schema from Tap output

# Installation

This package can be installed with pip:

```
$ pip install singer-tools
```

# Running

## singer-check-tap

You can use `singer-check-tap` to check whether a Tap conforms to the
Singer specification.

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
