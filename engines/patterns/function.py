# A pattern function represents one specific HTML logic on Zippyshare side to get the file
# download link. Zippyshare keeps updating this logic and so do we in order to keep up with
# them. The following patterns have been observed on the zippyshare site.

## CONTRIBUTING:
# If you'd like to contribute the latest pattern on the zippyshare site (not already here),
# please use this specification of a `pattern` function.
# It takes a BeautifulSoup object which contains all the HTML from the Zippyshare page.
# And it returns a single file download link. You can use any logic you want to but you
# refer to some of the following functions to check how I've done it. If useful, you can also use
# some of the utils I've created around extracting download link from HTML.

import re
import engines.patterns.utils as utils
import math

# This has always been common across all patterns
REGEX_1 = r'(\(\'dlbutton\'\)\.href = )(.*)(\;)'


def pattern_1(soup):
    REGEX_2 = r'(\".*\")(\+)(.*)(\+)(\".*\")'

    script = utils.get_script_block(soup)
    matcher = re.search(REGEX_1, script)
    if matcher is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_1 failed for pattern #1')
        return None

    expression = matcher.group(2)
    parts = re.search(REGEX_2, expression)
    if parts is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_2 failed for pattern #1')
        return None

    part1 = parts.group(1).replace('"', '')
    a = int(utils.get_value_var(script, 'a'))
    b = int(utils.get_value_var(script, 'b'))
    a = math.floor(a / 3)

    part2 = eval(parts.group(3))
    part3 = parts.group(5).replace('"', '')

    extract = part1 + part2 + part3
    extract = re.sub('/pd/', '/d/', extract)

    return extract


def pattern_2(soup):
    REGEX_2 = r'(\")(.*)(\/\"\ \+\ )(.*)(\ \+\ \")(.*)(\")'

    script = utils.get_script_block(soup)

    matcher = re.search(REGEX_1, script)
    if matcher is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_1 failed for pattern #2')
        return None

    expression = matcher.group(2)
    parts = re.search(REGEX_2, expression)
    if parts is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_2 failed for pattern #2')
        return None

    part_1 = parts.group(2)
    part_3 = parts.group(6)
    part_2 = eval(parts.group(4))

    extract = "{}/{}{}".format(part_1, part_2, part_3)
    extract = re.sub('/pd/', '/d/', extract)

    return extract


def pattern_3(soup):
    REGEX_2 = r'((\")(.*)(\"))\ ?\+\ ?(\((.*)\))\ ?\+\ ?(\"(.*)\")'

    script = utils.get_script_block(soup)

    matcher = re.search(REGEX_1, script)
    if matcher is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_1 failed for pattern #3')
        return None

    expression = matcher.group(2)
    parts = re.search(REGEX_2, expression)
    if parts is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_2 failed for pattern #3')
        return None

    part_1 = parts.group(3)
    part_3 = parts.group(8)

    arith_exp = parts.group(6)

    a = lambda: 1
    b = lambda: a() + 1
    c = lambda: b() + 1
    d = int(soup.select('span[id="omg"]')[0].get('class')[0]) * 2

    part_2 = int(eval(arith_exp))

    extract = "{}{}{}".format(part_1, part_2, part_3)
    extract = re.sub('/pd/', '/d/', extract)

    return extract


def pattern_4(soup):
    REGEX_2 = r'((\")(.*)(\"))\+(\((.*)\))\+(\"(.*)\")'

    script = utils.get_script_block(soup)
    matcher = re.search(REGEX_1, script)
    if matcher is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_1 failed for pattern #4')
        return None

    expression = matcher.group(2)
    parts = re.search(REGEX_2, expression)
    if parts is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_2 failed for pattern #4')
        return None

    part_1 = parts.group(3)
    part_3 = parts.group(8)

    script = script.replace('var d = 9;', '')

    a = eval(utils.get_value_var(script, 'a'))
    b = eval(utils.get_value_var(script, 'b'))
    c = 8
    d = eval(utils.get_value_var(script, 'd'))

    part_2 = a * b + c + d

    extract = "{}{}{}".format(part_1, part_2, part_3)
    extract = re.sub('/pd/', '/d/', extract)

    return extract


def pattern_5(soup):
    REGEX_2 = r'((\")(.*)(\"))\+(\((.*)\))\+(\"(.*)\")'

    script = utils.get_script_block(soup)
    matcher = re.search(REGEX_1, script)
    if matcher is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_1 failed for pattern #5')
        return None

    expression = matcher.group(2)
    parts = re.search(REGEX_2, expression)
    if parts is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_2 failed for pattern #5')
        return None

    part_1 = parts.group(3)
    part_3 = parts.group(8)

    n = eval(utils.get_value_var(script, 'n'))
    b = eval(utils.get_value_var(script, 'b'))
    part_2 = (n + n * 2 + b)

    extract = "{}{}{}".format(part_1, part_2, part_3)
    extract = re.sub('/pd/', '/d/', extract)

    return extract


def pattern_6(soup):
    REGEX_2 = r'((\")(.*)(\"))\+(\((.*)\))\+(\"(.*)\")'

    script = utils.get_script_block(soup)
    matcher = re.search(REGEX_1, script)
    if matcher is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_1 failed for pattern #6')
        return None

    expression = matcher.group(2)
    parts = re.search(REGEX_2, expression)
    if parts is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_2 failed for pattern #6')
        return None

    part_1 = parts.group(3)
    part_3 = parts.group(8)

    a = math.ceil(eval(utils.get_value_var(script, 'a')) / 3)
    b = eval(utils.get_value_var(script, 'b'))

    part_2 = eval(parts.group(5))

    extract = "{}{}{}".format(part_1, part_2, part_3)
    extract = re.sub('/pd/', '/d/', extract)

    return extract


def pattern_7(soup):
    REGEX_2 = r'(\")(.*)(\") ?\+ ?(.*) ?\+ ?(\")(.*)(\")'

    script = utils.get_script_block(soup)

    matcher = re.search(REGEX_1, script)
    if matcher is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_1 failed for pattern #7')
        return None

    expression = matcher.group(2)
    parts = re.search(REGEX_2, expression)
    if parts is None:
        # TODO: Replace this with proper logging
        print('[!] REGEX_2 failed for pattern #7')
        return None

    part_1 = parts.group(2)
    part_2 = eval(parts.group(4))
    part_3 = parts.group(6)

    extract = "{}{}{}".format(part_1, part_2, part_3)
    extract = re.sub('/pd/', '/d/', extract)

    return extract
