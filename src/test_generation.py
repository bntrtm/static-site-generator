import unittest

from generation import *

class TestHeaderExtraction(unittest.TestCase):
    def test_wrong_line(self):
        md = 'This is a markdown file without a heading in the first line.\n# It should raise an error.'
        with self.assertRaises(Exception):
            extract_title(md)
    def test_wrong_syntax(self):
        with self.assertRaises(Exception):
            md = '#This is a markdown file whose h1 header line fails to include the whitespace required for header syntax.\nIt should return an error.'
            extract_title(md)
    def test_correct_syntax(self):
        result = extract_title('# This is a markdown file whose h1 header line correctly includes the whitespace required for header syntax in markdown.\nIt should return no errors.')
        self.assertEqual(result, 'This is a markdown file whose h1 header line correctly includes the whitespace required for header syntax in markdown.')

