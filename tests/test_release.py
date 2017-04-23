import unittest
from singertools.release import parse_version_number

class TestRelease(unittest.TestCase):

    def test_parse_version_number_simple(self):
        version = parse_version_number("""
          setup(name='singer-python',
                version='1.2.3',
                description='Singer.io utility library')
        """.splitlines())
        self.assertEqual('1.2.3', version)

    def test_parse_version_number_alpha(self):
        version = parse_version_number("""
          setup(name='singer-python',
                version='1.2.3a1',
                description='Singer.io utility library')
        """.splitlines())
        self.assertEqual('1.2.3a1', version)        

    def test_parse_version_number_double_quotes(self):
        version = parse_version_number('''
          setup(name="singer-python",
                version="1.2.3a1",
                description="Singer.io utility library")
        '''.splitlines())
        self.assertEqual('1.2.3a1', version)        
        
