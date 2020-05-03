import unittest
from zippyshare import ZippyParser


class ZippyParserTest(unittest.TestCase):

    def setUp(self):
        self.zippy = ZippyParser()
        self.links = []
        with open('resources/test-links.txt', 'r') as f:
            for line in f:
                self.links.append(line.replace('\r', '').replace('\n', ''))

    def test_zippy_parse(self):
        links, failed = self.zippy.parse_links(self.links)
        self.assertEqual(len(links), len(self.links), 'Failed to parse all links')
