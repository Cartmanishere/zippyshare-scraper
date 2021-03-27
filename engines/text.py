import requests
from bs4 import BeautifulSoup
import logging
from engines.patterns import *

# Define supported patterns
PATTERNS = [pattern_1, pattern_2, pattern_3,
            pattern_4, pattern_5, pattern_6,
            pattern_7]


class TextEngine:
    def __init__(self, log_format='[*] %(message)s', logger=None):
        self.sess = requests.Session()
        if logger is None:
            logging.basicConfig(level=logging.INFO, format=log_format)
            self.logger = logging.getLogger('Zippyparse:TextEngine')
        else:
            self.logger = logger
        self.parser = None

    def __repr__(self):
        return 'TextEngine'

    def get_download_link(self, link):
        """
        Parse the contents from the Zippyshare site to extract the actual download link
        of the file. The zippyshare site can have dynamic logic around how to construct
        the download link. Various patterns have been coded for these.

        We try all the present patters and if one of the pattern is able to successfully
        parse the zippyshare site, keep using the same pattern for all the remaining links.
        If any page fails to parse with a selected pattern, try all other patterns once
        before failing.
        """
        html = self.sess.get(link)
        soup = BeautifulSoup(html.content, "lxml")

        if self.parser is not None:
            extract = self.parser(soup)
            if extract is None:
                logging.error('Selected parser {} failed'.format(self.parser.__name__))
                self.parser = None
                self.get_download_link(link)

            return extract, link
        else:
            # Try and figure out which pattern works
            parsers = PATTERNS

            for parser_fn in parsers:
                try:
                    extract = parser_fn(soup)
                    if extract is not None:
                        self.parser = parser_fn
                        return extract, link
                    raise Exception
                except Exception as e:
                    logging.warning(parser_fn.__name__ + " has failed for link: " + link)
                    logging.warning("Trying next pattern")

            logging.error("All patterns have failed")

            # TODO:: Check for 404 or link removed and then exit
            return None, link
