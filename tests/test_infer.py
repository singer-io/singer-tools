import unittest
import sys
import tempfile
import os
import io
import json

import singertools.infer_schema as infer

rec = {"name": "Joe", "age": 55, "money": 5.87, "is_cool": True, "birthday": "02-22-1970"}
rec2 = {"name": "Joe", "age": 55, "money": 5.87, "is_cool": True, "birthday": "02-22-1970",
        "info": {"today": "08-03-2020", "test": 1, "hello": "world"}}

class InferSchema(unittest.TestCase):

    def test_add_observations(self):
        obs1 = infer.add_observations({}, [], rec)
        self.assertEqual(obs1,
                         {'object': {'age': {'integer': True},
                                     'name': {'string': True},
                                     'is_cool': {'boolean': True},
                                     'money': {'number': True},
                                     'birthday': {'date': True}}})
        obs2 = infer.add_observations({}, [], rec2)
        self.assertEqual(obs2,
                         {'object': {'money': {'number': True},
                                     'info': {'object': {'test': {'integer': True},
                                                         'hello': {'string': True},
                                                         'today': {'date': True}}},
                                     'is_cool': {'boolean': True},
                                     'name': {'string': True},
                                     'birthday': {'date': True},
                                     'age': {'integer': True}}})


    def test_to_json_schema(self):
        obs1 = infer.add_observations({}, [], rec)
        result = infer.to_json_schema(obs1)
        self.assertEqual(result,
                         {'properties': {'money': {'type': ['null', 'string'], 'format': 'singer.decimal'},
                                         'birthday': {'type': ['null', 'string'], 'format': 'date-time'},
                                         'is_cool': {'type': ['null', 'boolean']},
                                         'age': {'type': ['null', 'integer']},
                                         'name': {'type': ['null', 'string']}},
                          'type': ['null', 'object']})
        obs2 = infer.add_observations({}, [], rec2)
        result = infer.to_json_schema(obs2)
        self.assertEqual(result,
                         {'properties': {'money': {'format': 'singer.decimal', 'type': ['null', 'string']},
                                         'info': {'properties': {'test': {'type': ['null', 'integer']},
                                                                 'hello': {'type': ['null', 'string']},
                                                                 'today': {'format': 'date-time', 'type': ['null', 'string']}},
                                                  'type': ['null', 'object']},
                                         'name': {'type': ['null', 'string']},
                                         'is_cool': {'type': ['null', 'boolean']},
                                         'birthday': {'format': 'date-time', 'type': ['null', 'string']},
                                         'age': {'type': ['null', 'integer']}}, 'type': ['null', 'object']})

    def test_infer_end_to_end(self):
        rec_messages = [{"type": "RECORD", "stream": "one", "record": {"test": "value"}},
                        {"type": "RECORD", "stream": "one", "record": {"another_key": 1.1}},
                        {"type": "RECORD", "stream": "two", "record": {"another": 1}},
                        {"type": "RECORD", "stream": "three", "record": {"hello": True}}]

        one_schema = {'type': ['null', 'object'], 'properties': {'test': {'type': ['null', 'string']},
                                                                 'another_key': {'type': ['null', 'string'], 'format': 'singer.decimal'}}}
        two_schema = {'type': ['null', 'object'], 'properties': {'another': {'type': ['null', 'integer']}}}
        three_schema = {'type': ['null', 'object'], 'properties': {'hello': {'type': ['null', 'boolean']}}}

        with tempfile.TemporaryDirectory() as td:
            messages = [json.dumps(r) for r in rec_messages]
            infer.infer_schemas(messages, td)
            
            self.assertEqual(len(os.listdir(td)), 3)

            one = json.load(open(os.path.join(td, 'one.inferred.json')))
            self.assertEqual(one, one_schema)
            two = json.load(open(os.path.join(td, 'two.inferred.json')))
            self.assertEqual(two, two_schema)
            three = json.load(open(os.path.join(td, 'three.inferred.json')))
            self.assertEqual(three, three_schema)
            
            
