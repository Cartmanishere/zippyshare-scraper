import re
import json
import requests
import urllib
from bs4 import BeautifulSoup


def get_domain(link):
    """
    Given a URL, it returns the domain name.
    E.g: https://google.com => google.com
    """
    return '{uri.scheme}://{uri.netloc}/'.format(uri=urllib.parse.urlparse(link))


def decrypt_dlc(contents):
    """
    Decrypt the dlc file data using the decrypt.it endpoint.
    """
    try:
        data = {'content': contents}
        r = requests.post('http://dcrypt.it/decrypt/paste', data=data)
        # Raise HTTP Exception if got response code other than 200
        if r.status_code != 200:
            r.raise_for_status()

        jobj = json.loads(r.content.decode())
        if jobj.get('success') is None:
            raise Exception('Dcrypt server did not have `success` key in response.')

        links = jobj.get('success').get('links', [])
        return links

    except Exception as e:
        # TODO: Replace this with proper logging
        print('[*] {}'.format(e))
        exit(1)


def load_from_file(fname):
    """
    Load the links from the given file. Each line is considered as one line.
    """
    with open(fname, 'r') as f:
        urls = []
        for line in f:
            # TODO: Add more cleaning and validation to the links
            urls.append(line.replace('\r', '').replace('\n', ''))
    return urls


def load_from_terminal():
    """
    Get the list of links from the terminal input.
    """
    urls = []
    while True:
        ui = input('Enter URLs (leave blank to stop): ')
        if ui != '':
            urls.append(ui.strip())
            continue
        break
    return urls


def load_from_filecrypt(url):
    """
    Download the dlc content from the filecrypt url and try to decrypt it to get
    the links.
    Note: Does not work with password or captcha protected filecrypt urls.
    """
    try:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'lxml')
        button = soup.select('button[class="dlcdownload"]')
        if len(button) == 0:
            raise ValueError('%s does not contain dlc download option.' % url)

        onclick = button[0].get('onclick')
        if onclick is None:
            raise ValueError('%s is not supported. Try opening the link manually.' % url)

        link_id = re.search(".*\(\'(.*)\'\).*", onclick).group(1)
        domain = utils.get_domain(url)
        link = domain + 'DLC/' + link_id + '.dlc'
        dlc = requests.get(link)
        return decrypt_dlc(dlc.content)

    except Exception as e:
        # TODO: Replace this with proper logging
        print('[*] {}'.format(e))
        exit(1)


def load_from_dlcfile(file):
    """
    Given a path to the dlc file, decrypt the file to get the zippyshare links.
    """
    # Validate that the given `file` is indeed dlc.
    if file.split('.')[-1] != 'dlc':
        # TODO: Replace this with proper logging
        print('[!] This is not a dlc file. Please provide path to a valid dlc file.')
        exit(1)

    # Make the api call and decrypt the dlc.
    with open(file, 'r') as f:
        contents = f.read()
    return decrypt_dlc(contents)
