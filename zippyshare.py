import time
import argparse
import requests
import loaders
import logging
from engines.text import TextEngine
from engines.js import JSEngine
from engines.patterns import utils
from concurrent.futures import as_completed, ThreadPoolExecutor


class ZippyParser:
    def __init__(self, workers=10, engine=None):
        self.sess = requests.Session()
        FORMAT = '[*] %(message)s'
        logging.basicConfig(level=logging.INFO, format=FORMAT)
        self.logger = logging.getLogger('Zippyparse')
        self.parser = None
        self.workers = workers
        if engine is None:
            self.engine = JSEngine(logger=self.logger)
        else:
            self.engine = engine(logger=self.logger)
        self.logger.info('Using {} for generating links'.format(self.engine))

    def get_download_link(self, link):
        """
        Parse the contents from the Zippyshare site to extract the actual download link
        of the file. The zippyshare site has javascript logic around how to construct
        the download link.
        """

        extract, link = self.engine.get_download_link(link)
        return extract, link

    def verify_link(self, link):
        """
        Verify that the extracted link points to actual downloadable file.
        In case it points to a Zippyshare site (HTML page), retry the parsing.
        After 3 retries, it gives up.
        """
        count = 0
        while True:
            count += 1
            if count > 8:
                logging.error('{} redirected more than 3 times'.format(link))
                return None

            if not utils.is_valid_link(self.sess, link):
                link = utils.get_domain(link)[:-1] + self.get_download_link(link)[0]
                continue

            return link

    def parse_links(self, links):
        """
        Parse the zippyshare page to generate direct download links
        :param links: List of zippyshare URLS
        :return:
        """
        rlinks = []
        failed = []
        count = 0

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.get_download_link, url) for url in links]
            for f in as_completed(futures):
                extract, link = f.result()
                if extract is None:
                    self.logger.error('Failed to parse - {}'.format(link))
                    failed.append(link)
                    continue
                dlink = utils.get_domain(link)[:-1] + extract
                count += 1
                self.logger.info('{}/{} links parsed {}'.format(count, len(links), dlink))
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

        return flinks, failed


def load_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--engine', dest='engine', default='js',
                        help='Link generating engine to use for generating links. Valid options are "js" and "text".')
    parser.add_argument('--in-file', dest='infile', default=None, help='path to file containing links to be processed')
    parser.add_argument('--out-file', dest='outfile', default='links.txt',
                        help='path to file in which resultant links will be stored')
    parser.add_argument('--dlc', dest='dlcfile', default=None,
                        help='If you have a dlc file, you can use that instead of a txt file')
    parser.add_argument('--filecrypt', dest='filecrypt_url', default=None,
                        help='Filecrypt link which has a dlc option. Link should not have a captcha or a password.')

    return parser.parse_args()


def save_links(success, failed, outfile):
    with open(args.outfile, 'w') as f:
        for link in success:
            f.write(link + '\n')
        zippy.logger.info('All download links saved at {}'.format(outfile))

    with open("failed.log", 'w') as f:
        for link in failed:
            f.write(link + '\n')
        if len(failed) > 0:
            zippy.logger.info('All failed links saved at failed.log')


if __name__ == "__main__":

    args = load_args()

    if args.filecrypt_url is not None:
        urls = loaders.load_from_filecrypt(args.filecrypt_url)
    elif args.dlcfile is not None:
        urls = loaders.load_from_dlcfile(args.dlcfile)
    elif args.infile is not None:
        urls = loaders.load_from_file(args.infile)
    else:
        urls = loaders.load_from_terminal()

    if len(urls) == 0:
        print('[*] No URLS found!')
        exit(1)

    start = time.time()
    engine = JSEngine
    if args.engine == 'text':
        engine = TextEngine

    zippy = ZippyParser(engine=engine)
    links, fails = zippy.parse_links(urls)
    end = time.time()
    print('Time taken: {:.3f}s'.format(end - start))
    save_links(links, fails, args.outfile)

