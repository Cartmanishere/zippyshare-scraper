import os
import js2py
import requests
import logging
from bs4 import BeautifulSoup


def get_dir(file):
    """
    Return the absolute path of the file relative to this dir.
    :param file: filename
    :return path: absolute path of the file.
    """
    dir_path = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(dir_path, file)


class JSEngine:
    def __init__(self, log_format='[*] %(message)s', logger=None):
        if logger is None:
            logging.basicConfig(level=logging.INFO, format=log_format)
            self.logger = logging.getLogger('Zippyparse:JSEngine')
        else:
            self.logger = logger
        self.sess = requests.Session()
        self.context = js2py.EvalJs()
        self.__preload_js(get_dir('stub.js'))

    def __repr__(self):
        return 'JSEngine'

    def __preload_js(self, file):
        """
        Load any javascript code at the start of the JS context.
        :param file: Javascript file with code.
        :return:
        """
        with open(file, 'r') as f:
            code = f.read()
        self.context.execute(code)

    @staticmethod
    def get_script(soup):
        """
        Get the javascript code part which constructs the download link.
        :param soup: A beautiful soup object with the zippyshare page's contents
        :return code: Javascript code.
        """
        for i in soup.find_all('script'):
            if 'dlbutton' in i.text:
                return i.text

    def run_js(self, code):
        """
        Run javascript code in the current JS context.
        :param code: Javascript code to run.
        :return:
        """
        self.context.execute(code)

    def get_link(self):
        """
        Get the required download link part from the javascript runtime after the
        javascript code to generate the link has been executed.
        :return extract: download link part.
        """
        try:
            dl_button = self.context.document.dlbutton
            if dl_button is None:
                return None
            return dl_button.href
        except Exception as e:
            self.logger.error(e)
            return None

    def get_download_link(self, link):
        """
        Extract the zippyshare link part.
        :param link:
        :return:
        """
        r = self.sess.get(link)
        soup = BeautifulSoup(r.content, 'lxml')
        code = JSEngine.get_script(soup)
        if code is None:
            self.logger.error('Did not find the required logic for creating link - {}'.format(link))
            return None, link
        self.run_js(code)
        extract = self.get_link()
        if extract is None:
            self.logger.error('Failed to generate the link using javascript code!')
            return None, link

        return extract, link


if __name__ == "__main__":
    j = JSEngine()
    # j.get_download_link('')
