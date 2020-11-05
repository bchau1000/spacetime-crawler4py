import re
import requests
from urllib.parse import urlparse, urlunparse
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from PartA import Tokenizer
from PartB import common_tokens
from readability import Document


def tokenize_page(url, resp):
    try:
        f = open('bad_urls.txt', 'r')
        
        listBadURLs = list()
        for line in f:
            listBadURLs.extend(list(line.split()))
        f.close()
        setBadURLs = listBadURLs
        
        if url in setBadURLs:
            return 0


        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        # Tokenize the page with regex split
        tokens_raw = list(re.split(r'[^a-zA-Z0-9]', soup.get_text().lower()))


        # Initialize list of stop words from NLTK
        stop_words = set(stopwords.words('english'))
        tokens_filtered = list()

        # Filter out stop words, append text to tokens.txt
        for token in tokens_raw:
            if (token not in stop_words) and len(token) > 1:
                tokens_filtered.append(str(token))

        f = open('text/tokens.txt', '+a')
        for token in tokens_filtered:
            f.write(str(token) + ' ')
        f.close()

        # Return the number of tokens in the page after stop word filter
        return len(tokens_filtered)
    except:
        f = open("text/errors.txt","a+")
        f.write("Has tokenize error: " + url + "\n")
        f.close()

    return 0

def scraper(url, resp):
    ########## add code to write url to file to answer report #############
    
    links = []

    if resp.raw_response != None and not (resp.raw_response.status_code >= 400) and is_valid(url) and resp.raw_response.content != b'':
        if is_valid(resp.raw_response.url):
            pageLength = tokenize_page(url, resp)
            links = extract_next_links(resp.raw_response.url, resp)

            lenFile = open('text/length.txt', '+a')
            urlFile = open('text/URLs.txt', '+a')
            urlLenFile = open('text/urlLen.txt', '+a')

            lenFile.write(str(pageLength) + ' ')
            urlFile.write(url + '\n')
            urlLenFile.write(url + ' ' + str(pageLength) + '\n')

            urlLenFile.close()
            urlFile.close()
            lenFile.close()

    return links

def extract_next_links(url, resp):
    res = []
    # parse web page
    soup = BeautifulSoup(resp.raw_response.text, 'html.parser')
    # parse links from page content
    for link in soup.find_all('a'):
        link = link.get('href')
        if link != None:
            # if full link without schema
            if re.match(r'\/\/', link):
                link = 'http:' + link
            # check if link is a relative path
            if link != None and re.match(r'\/.*', link):
                relativeLink = link
                parsed = urlparse(url)
                link = str(parsed.scheme) + '://' + str(parsed.netloc) + str(link)

            if is_valid(link):
                res.append(link)

    return res

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False

        if len(parsed.fragment):
            return False

        # check if link is not within a valid domain
        if not re.match(r'^(?:www.)?ics\.uci\.edu|.+\.ics\.uci\.edu' +
                         r'|^(?:www.)?cs\.uci\.edu|.+\.cs\.uci\.edu' +
                         r'|^(?:www.)?informatics\.uci\.edu|.+\.informatics\.uci\.edu' +
                         r'|^(?:www.)?stat\.uci\.edu|.+\.stat\.uci\.edu', parsed.netloc)\
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
        
        # check if query is a reply to comment trap
        if re.search(r'replytocom=', parsed.query.lower()):
            return False
        
        # check for extraneous directories
        if re.search(r'\/involved\/.+\/.+', parsed.path.lower()):
            return False

        # check if link is not an unreadable file
        return not re.search(
            r"[\.\/](css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|ppsx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)", parsed.path.lower() + parsed.query.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise