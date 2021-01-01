import unittest
from loaders import load_from_filecrypt
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


class FilecryptTest(unittest.TestCase):

    def test_load_from_filecrypt(self):
        url = 'https://filecrypt.co/Container/501DC8D388.html'
        results = ['https://www18.zippyshare.com/v/NQx3c648/file.html',
                   'https://www18.zippyshare.com/v/xpC6ZOHB/file.html',
                   'https://www18.zippyshare.com/v/4Cul2DpC/file.html']
        # Verify that both the lists contain same elements without considering order.
        # Someone messed up while naming the following function.
        self.assertCountEqual(load_from_filecrypt(url), results, 'Failed to load links from filecrypt')

