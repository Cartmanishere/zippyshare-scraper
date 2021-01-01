import re
import urllib.parse
from functools import reduce
import json
import requests

VAR_REGEX = r'(var {} = )([0-9%]+);'

def get_value_var(script, varname):
    """
    Given a javascript `script` block and variable name, returns the value of the of the variable
    as defined in javascript.
    """
    matcher = re.search(VAR_REGEX.format(varname), script)
    if matcher is None:
        return None

    var = matcher.group(2)
    return var

def get_domain(link):
    """
    Given a URL, it returns the domain name.
    E.g: https://google.com => google.com
    """
    return '{uri.scheme}://{uri.netloc}/'.format(uri=urllib.parse.urlparse(link))


def get_script_block(bsobj):
    """
    Given a BeautifulSoup object, get all the contents of the <script> tags in  a single string.
    """
    return reduce(lambda x, y: x + y.text, bsobj.find_all("script"), '')


def is_valid_link(session, link):
    """
    Verify that the generated link points to a downloadable file.

    It was observed that sometimes, even after generating the link, it would still point
    to an HTML page. So based on the `Content-Type` header in the response for that link,
    we can determine whether the link points to a file or an HTML page.

    Note: In case, it actually points to a file, we don't want to download the whole file
    just to check header. Some servers do no support `HEAD` request, so we are use `Range`
    request header. It has been tested that Zippyshare servers respect the `Range` header.

    Added benefit of using `Range` header instead of `HEAD` request is that the link is
    marked as downloaded by the Zippyshare server. So validating the link, also renews it.
    """
    headers = {'Range': 'bytes=0-200'}
    r = session.get(link, headers=headers)
    return r.headers.get('Content-Type', 'text/html;charset=UTF-8') != 'text/html;charset=UTF-8'




