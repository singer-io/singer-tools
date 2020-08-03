import unittest

import singertools.infer_schema as infer

rec = {"name": "Joe", "age": 55, "money": 5.87, "is_cool": True, "birthday": "02-22-1970"}
rec2 = {"name": "Joe", "age": 55, "money": 5.87, "is_cool": True, "birthday": "02-22-1970",
        "info": {"today": "08-03-2020", "test": 1, "hello": "world"}}

class InferSchema(unittest.TestCase):

    def test_add_observations(self):
        infer.add_observations([], rec)
        self.assertEqual(infer.OBSERVED_TYPES,
                         {'object': {'age': {'integer': True},
                                     'name': {'string': True},
                                     'is_cool': {'boolean': True},
                                     'money': {'number': True},
                                     'birthday': {'date': True}}})
        infer.OBSERVED_TYPES = {}
        infer.add_observations([], rec2)
        self.assertEqual(infer.OBSERVED_TYPES,
                         {'object': {'money': {'number': True},
                                     'info': {'object': {'test': {'integer': True},
                                                         'hello': {'string': True},
                                                         'today': {'date': True}}},
                                     'is_cool': {'boolean': True},
                                     'name': {'string': True},
                                     'birthday': {'date': True},
                                     'age': {'integer': True}}})


    def test_to_json_schema(self):
        infer.OBSERVED_TYPES = {}
        infer.add_observations([], rec)
        result = infer.to_json_schema(infer.OBSERVED_TYPES)
        self.assertEqual(result,
                         {'properties': {'money': {'type': ['null', 'string'], 'format': 'singer.decimal'},
                                         'birthday': {'type': ['null', 'string'], 'format': 'date-time'},
                                         'is_cool': {'type': ['null', 'boolean']},
                                         'age': {'type': ['null', 'integer']},
                                         'name': {'type': ['null', 'string']}},
                          'type': ['null', 'object']})

        infer.OBSERVED_TYPES = {}
        infer.add_observations([], rec2)
        result = infer.to_json_schema(infer.OBSERVED_TYPES)
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
