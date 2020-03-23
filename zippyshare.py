import re
import argparse
import requests
import urllib.parse
from bs4 import BeautifulSoup
import logging
import math
import json
from concurrent.futures import as_completed, ThreadPoolExecutor


class ZippyParser():

    def __init__(self):
        self.sess = requests.Session()
        self.VAR_REGEX = r'(var {} = )([0-9%]+);'
        self.REGEX_1 = r'(\(\'dlbutton\'\)\.href = )(.*)(\;)'
        FORMAT = '[*] %(message)s'
        logging.basicConfig(level=logging.INFO, format=FORMAT)
        self.logger = logging.getLogger('Zippyparse')
        self.parser = None

    @staticmethod
    def __get_domain(link):
        return '{uri.scheme}://{uri.netloc}/'.format(uri=urllib.parse.urlparse(link))

    @staticmethod
    def __get_script(soup):
        script = ''
        for i in soup.find_all("script"):
            script += i.text
        return script

    @staticmethod
    def decrypt_dlc(dlcfile):
        if dlcfile.split('.')[-1] != 'dlc':
            print("This is not a .dlc file.")
            exit(1)
        try:
            post_data = {'content': open(dlcfile, 'r').read()}
            r = requests.post('http://dcrypt.it/decrypt/paste', data=post_data)
            if r.status_code == 200:
                jobj = json.loads(r.content.decode())
                if jobj.get('success') is None:
                    print('[*] DLC decryption failed')
                    exit(1)

                links = jobj.get('success').get('links', [])
                return links
        except Exception as e:
            print('[*] {}'.format(e))
            exit(1)

    def get_value_of_var(self, script_block, var):
        matcher = re.search(self.VAR_REGEX.format(var), script_block)
        if matcher is None:
            return None

        var = matcher.group(2)
        return var

    def get_download_link(self, link):
        html = self.sess.get(link)
        soup = BeautifulSoup(html.content, "lxml")

        if self.parser is not None:
            extract = self.parser(soup)
            if extract is None:
                logging.error('Selected parser {} failed'.format(self.parser.__name__))
                return None

            return extract, link
        else:
            # Try and figure out which pattern works
            parsers = [self.pattern_1,
                       self.pattern_2,
                       self.pattern_3,
                       self.pattern_4,
                       self.pattern_5,
                       self.pattern_6]

            for parser_fn in parsers:
                try:
                    extract = parser_fn(soup)
                    if extract is not None:
                        self.parser = parser_fn
                        return extract, link
                    raise Exception
                except Exception as e:
                    logging.warning(parser_fn.__name__ + " has failed")
                    logging.warning("Trying next pattern")

            logging.error("All patterns have failed")

            # TODO:: Check for 404 or link removed and then exit
            return None, link

    def verify_link(self, link):
        headers = {"Range": "bytes=0-200"}
        count = 0
        while True:
            count += 1
            if count > 3:
                logging.error('{} redirected more than 3 times'.format(link))
                return None

            check = self.sess.get(link, headers=headers)
            if check.headers.get('Content-Type') == 'text/html;charset=UTF-8':
                link = ZippyParser.__get_domain(link)[:-1] + self.get_download_link(link)[0]
                continue

            return link

    def parse_links(self, links):
        """
        Parses the zippyshare page to generate direct download links
        :param links: List of zippyshare URLS
        :return:
        """
        rlinks = []
        count = 0

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.get_download_link, url) for url in links]
            for f in as_completed(futures):
                extract, link = f.result()
                if extract is None:
                    self.logger.error('Failed to parse - {}'.format(link))
                    continue
                dlink = ZippyParser.__get_domain(link)[:-1] + extract
                count += 1
                self.logger.info('{}/{} links parsed'.format(count, len(links)))
                rlinks.append(dlink)

        self.logger.info('Verifying download links...')
        flinks = []
        count = 0

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.verify_link, url) for url in rlinks]
            for f in as_completed(futures):
                if f.result() is not None:
                    flinks.append(f.result())
                    count += 1
                    self.logger.info('{}/{} links verified'.format(count, len(rlinks)))

        return flinks

    def pattern_1(self, soup):
        """
        First pattern in the zippyshare html page to create download link
        :param soup: Soup for the complete webpage
        :return: Extracted direct download link
        """
        REGEX_2 = r'(\".*\")(\+)(.*)(\+)(\".*\")'

        script = ZippyParser.__get_script(soup)

        matcher = re.search(self.REGEX_1, script)
        if matcher is None:
            logging.debug('Failed REGEX_1 for pattern 1')
            return None

        expression = matcher.group(2)
        parts = re.search(REGEX_2, expression)

        if parts is None:
            logging.debug('Failed REGEX_2 for pattern 1')
            logging.debug(expression)
            return None

        part_1 = parts.group(1).replace("\"", '')
        a = int(self.get_value_of_var(script, 'a'))
        b = int(self.get_value_of_var(script, 'b'))
        a = math.floor(a / 3)
        part_2 = eval(parts.group(3))
        part_3 = parts.group(5).replace('"', '')

        extract = "{}{}{}".format(part_1, part_2, part_3)
        extract = re.sub('/pd/', '/d/', extract)

        return extract

    def pattern_2(self, soup):
        """
        Second pattern in the zippyshare html page to create download link
        :param soup: Soup for the complete webpage
        :return: Extracted direct download link
        """
        REGEX_2 = r'(\")(.*)(\/\"\ \+\ )(.*)(\ \+\ \")(.*)(\")'

        script = ZippyParser.__get_script(soup)

        matcher = re.search(self.REGEX_1, script)
        if matcher is None:
            logging.debug('Failed REGEX_1 for pattern 2')
            return None

        expression = matcher.group(2)
        parts = re.search(REGEX_2, expression)

        if parts is None:
            logging.debug('Failed REGEX_2 for pattern 2')
            return None

        part_1 = parts.group(2)
        part_3 = parts.group(6)
        part_2 = eval(parts.group(4))

        extract = "{}/{}{}".format(part_1, part_2, part_3)
        extract = re.sub('/pd/', '/d/', extract)

        return extract

    def pattern_3(self, soup):
        """
        Third pattern in the zippyshare html page to create download link
        :param soup: Soup for the complete webpage
        :return: Extracted direct download link
        """
        # REGEX_2 = r'(\")(.*)(\/\"\ \+\ )(.*)(\ \+\ \")(.*)(\")'
        REGEX_2 = r'((\")(.*)(\"))\+(\((.*)\))\+(\"(.*)\")'

        script = ZippyParser.__get_script(soup)

        matcher = re.search(self.REGEX_1, script)
        if matcher is None:
            logging.debug('Failed REGEX_1 for pattern 3')
            return None

        expression = matcher.group(2)
        parts = re.search(REGEX_2, expression)

        if parts is None:
            logging.debug('Failed REGEX_2 for pattern 3')
            return None

        part_1 = parts.group(3)
        part_3 = parts.group(8)

        arith_exp = parts.group(5)

        a = lambda: 1
        b = lambda: a() + 1
        c = lambda: b() + 1
        d = int(soup.select('span[id="omg"]')[0].get('class')[0]) * 2

        part_2 = int(eval(arith_exp))

        extract = "{}{}{}".format(part_1, part_2, part_3)
        extract = re.sub('/pd/', '/d/', extract)

        return extract

    def pattern_4(self, soup):
        """
        Fourth pattern in the zippyshare html page to create download link
        :param soup: Soup for the complete webpage
        :return: Extracted direct download link
        """
        REGEX_2 = r'((\")(.*)(\"))\+(\((.*)\))\+(\"(.*)\")'

        script = ZippyParser.__get_script(soup)

        matcher = re.search(self.REGEX_1, script)
        if matcher is None:
            logging.debug('Failed REGEX_1 for pattern 4')
            return None

        expression = matcher.group(2)
        parts = re.search(REGEX_2, expression)

        if parts is None:
            logging.debug('Failed REGEX_2 for pattern 4')
            return None

        part_1 = parts.group(3)
        part_3 = parts.group(8)

        script = script.replace('var d = 9;', '')

        a = eval(self.get_value_of_var(script, 'a'))
        b = eval(self.get_value_of_var(script, 'b'))
        c = 8
        d = eval(self.get_value_of_var(script, 'd'))

        part_2 = a * b + c + d

        extract = "{}{}{}".format(part_1, part_2, part_3)
        extract = re.sub('/pd/', '/d/', extract)

        return extract

    def pattern_5(self, soup):
        """
        Fifth pattern in the zippyshare html page to create download link
        :param soup: Soup for the complete webpage
        :return: Extracted direct download link
        """
        REGEX_2 = r'((\")(.*)(\"))\+(\((.*)\))\+(\"(.*)\")'

        script = ZippyParser.__get_script(soup)

        matcher = re.search(self.REGEX_1, script)
        if matcher is None:
            logging.debug('Failed REGEX_1 for pattern 5')
            return None

        expression = matcher.group(2)
        parts = re.search(REGEX_2, expression)

        if parts is None:
            logging.debug('Failed REGEX_2 for pattern 5')
            return None

        part_1 = parts.group(3)
        part_3 = parts.group(8)

        n = eval(self.get_value_of_var(script, 'n'))
        b = eval(self.get_value_of_var(script, 'b'))

        part_2 = (n + n * 2 + b)

        extract = "{}{}{}".format(part_1, part_2, part_3)
        extract = re.sub('/pd/', '/d/', extract)

        return extract

    def pattern_6(self, soup):
        """
        Sixth pattern in the zippyshare html page to create download link
        :param soup: Soup for the complete webpage
        :return: Extracted direct download link
        """
        REGEX_2 = r'((\")(.*)(\"))\+(\((.*)\))\+(\"(.*)\")'

        script = ZippyParser.__get_script(soup)

        matcher = re.search(self.REGEX_1, script)
        if matcher is None:
            logging.debug('Failed REGEX_1 for pattern 5')
            return None

        expression = matcher.group(2)
        parts = re.search(REGEX_2, expression)

        if parts is None:
            logging.debug('Failed REGEX_2 for pattern 5')
            return None

        part_1 = parts.group(3)
        part_3 = parts.group(8)

        a = eval(self.get_value_of_var(script, 'a'))
        b = 3

        part_2 = ((a ** 3) + b)

        extract = "{}{}{}".format(part_1, part_2, part_3)
        extract = re.sub('/pd/', '/d/', extract)

        return extract


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--in-file', dest='infile', default=None, help='path to file containing links to be processed')
    parser.add_argument('--out-file', dest='outfile', default='links.txt',
                        help='path to file in which resultant links will be stored')
    parser.add_argument('--dlc', dest='dlcfile', default=None,
                        help='If you have a dlc file, you can use that instead of a txt file')

    args = parser.parse_args()

    if args.dlcfile is not None:
        urls = ZippyParser.decrypt_dlc(args.dlcfile)

    elif args.infile is not None:
        with open(args.infile, 'r') as f:
            urls = []
            for line in f:
                # TODO: Add more cleaning and validation to the links
                urls.append(line.replace('\r', '').replace('\n', ''))

    else:
        urls = []
        while True:
            ui = input('Enter URLs (leave blank to stop): ')
            if ui != '':
                urls.append(ui.strip())
                continue
            break

    zippy = ZippyParser()
    links = zippy.parse_links(urls)

    with open(args.outfile, 'w') as f:
        for link in links:
            f.write(link + '\n')
        zippy.logger.info('All download links saved at {}'.format(args.outfile))
