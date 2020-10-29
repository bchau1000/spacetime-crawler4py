import re
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from PartA import Tokenizer
from PartB import common_tokens


def scraper(url, resp):
    if is_valid(url):
        pass

    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    res = []
    # parse web page
    soup = BeautifulSoup(resp.raw_response.text, 'html.parser')
    # parse links from page content
    for link in soup.find_all('a'):
        link = link.get('href')
        if is_valid(link):
            parsed = urlparse(link)
            res.append(urlunparse(parsed._replace(fragment='')))

    return res

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        # check if link is not within a valid domain
        if not re.search(r'\.ics\.uci\.edu' +
                         r'|\.cs\.uci\.edu' +
                         r'|\.informatics\.uci\.edu' +
                         r'|\.stat\.uci\.edu', parsed.netloc)\
            and not (re.match(r'today\.uci\.edu', parsed.netloc.lower())\
            and re.match(r'\/department\/information_computer_sciences', parsed.path)):
            return False

        print(parsed.path.lower())
        # check if link is not a file
        return not re.search(
            r"[\.\/](css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise