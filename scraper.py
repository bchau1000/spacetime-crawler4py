import re

import nltk 
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import os

def scraper(url, resp):
    links = extract_next_links(url, resp)

    lenFile = open('text/length.txt', '+a')
    pageLength = tokenize_page(url, resp)
    lenFile.write(str(pageLength) + ' ')
    lenFile.close()

    urlFile = open('text/URLs.txt', '+a')
    for link in links:
        urlFile.write(link + '\n')
    urlFile.close()

    return links

def tokenize_page(url, resp):
    try:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        fileName = 'text/token1.txt'
        textFile = open(fileName, '+a')

        file_stats = os.stat(fileName)
        file_size = file_stats.st_size / (1024 * 1024)

        if(file_size > 30.0):
            textFile.close()
            textFile = open('text/token2.txt', '+a')

        tokens_raw = list(re.split(r'[^a-zA-Z0-9]', soup.get_text().lower()))
        stop_words = set(stopwords.words('english'))
        tokens_filtered = list()

        for token in tokens_raw:
            if (token not in stop_words) and len(token) > 1:
                tokens_filtered.append(str(token))
                textFile.write(str(token) + ' ')

        return len(tokens_filtered)
    except:
        f = open("text/errors.txt","a+")
        f.write("Has tokenize error: " + url + "\n")
        f.close()

    return 0

def extract_next_links(url, resp):
    urlList = list()

    try:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')
        for link in soup.find_all('a'):
            if is_valid(link.get('href')):
                urlList.append(link.get('href'))
    except:
        f = open("text/errors.txt","a+")
        f.write("Has extract error: " + url + "\n")
        f.close()

    
    return urlList

def is_valid(url):
    try:
        parsed = urlparse(url)

        if len(parsed.fragment):
            f = open("text/errors.txt","a+")
            f.write("Has skipped fragment: " + url + "\n")
            f.close()
            return False
        
        if parsed.scheme not in set(["http", "https"]):
            return False

        listURLs = ['ics.uci.edu', 'cs.uci.edu',
                    'informatics.uci.edu', 'stat.uci.edu',
                    'today.uci.edu/department/information_computer_sciences']

        validNetLoc = False

        for netloc in listURLs:
            if(netloc in parsed.netloc):
                validNetLoc = True

        if not validNetLoc:
            return False

        urlPath = (parsed.path + parsed.params).lower()

        return not re.match(r"^.*\b(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|calendar|calendars|event|events"
            + r"|comment|response|respond|ppsx)\b.*$", urlPath)

    except TypeError:
        print ("TypeError for ", parsed)
        raise

