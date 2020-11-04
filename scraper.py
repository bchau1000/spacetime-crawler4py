import re
import requests
from urllib.parse import urlparse, urlunparse
from bs4 import BeautifulSoup
from PartA import Tokenizer
from PartB import common_tokens
from readability import Document


def tokenize(words):
    res = []
    pattern = re.compile(r'[A-Za-z0-9]+')
    for word in words:
        match = pattern.match(word)
        if match and len(match.string) > 1:
            res.append(match.string)

    return res

def scraper(url, resp):
    ########## add code to write url to file to answer report #############
    #
    links = []

    if resp.raw_response != None and not (resp.raw_response.status_code >= 400) and is_valid(url) and resp.raw_response.content != b'':
        if is_valid(resp.raw_response.url):
        # pattern to split by anything that is not alphanumeric or an apostrophe
        # pattern = re.compile(r"[^A-Za-z0-9']")

        # doc = Document(resp.raw_response.content)
        # words = pattern.split(doc.title.replace('\'', ''))        # strip title of apostrophes and split
        # soup = BeautifulSoup(doc.summary(), 'html.parser')       # parse readable text from the html
        # words += pattern.split(soup.get_text().replace('\'', '')) # strip content of apostrophes and split

        # tokens = tokenize(words) # tokenize list of words from the web page

            links = extract_next_links(resp.raw_response.url, resp)

    return links

def extract_next_links(url, resp):
    res = []
    # parse web page
    soup = BeautifulSoup(resp.raw_response.text, 'html.parser')
    # parse links from page content
    for link in soup.find_all('a'):
        link = link.get('href')
        if link != None:
            # if its just a fragment, skip it
            if link.startswith('#') or link.startswith('mailto'):
                continue
            # if full link without schema
            if re.match(r'\/\/', link):
                link = 'http:' + link
            # check if link is a relative path
            if link != None and re.match(r'\/.*', link):
                link = resp.raw_response.url + link
            parsed = urlparse(link)
            link = urlunparse(parsed._replace(fragment=''))
            if is_valid(link):
                res.append(link)

    return res

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # check if link is not within a valid domain
        if not re.match(r'^ics\.uci\.edu|.+\.ics\.uci\.edu' +
                         r'|^cs\.uci\.edu|.+\.cs\.uci\.edu' +
                         r'|^informatics\.uci\.edu|.+\.informatics\.uci\.edu' +
                         r'|^stat\.uci\.edu|.+\.stat\.uci\.edu', parsed.netloc)\
            and not (re.match(r'today\.uci\.edu', parsed.netloc.lower())\
            and re.match(r'\/department\/information_computer_sciences(?:\/.+)*', parsed.path.lower())):
            return False

        # check if its a calendar
        if re.search(r'\/calendar\/.+|\/events\/.+', parsed.path.lower()):
            return False

        # check for repeating directories or directory path after file
        # /folder/folder/folder
        # /text.txt/folder
        if re.match(r'.*?\/(.+?)\/.*?\1.*|.*?\/(.+?)\/\2.*', parsed.path.lower()) or\
           re.match(r'.*\..+\/', parsed.path.lower()):
            return False

        # check for exrta question mark in queries or directory path in queries
        # i.e. www.ics.uci.edu?id=5?key=55
        # i.e. www.ics.uci.edu?id=5/new/directory/path
        if re.match(r'.*\?.*|.*\/', parsed.query.lower()):
            return False
        
        # check for extraneous directories
        if re.search(r'\/involved\/.+\/.+', parsed.path.lower()):
            return False

        # check if link is not an unreadable file
        return not re.search(
            r"[\.\/](css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)", parsed.path.lower() + parsed.query.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise