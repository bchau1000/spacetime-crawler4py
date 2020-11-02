import re

import nltk
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib import robotparser
import os

from pymongo import MongoClient

client = MongoClient('localhost')


db = client['cs121Assignment2']
tokenCol = db['tokenCollection']
urlCol = db['urlCollection']

def scraper(url, resp):
    f = open('text/link_info.txt', '+a')
    if(int(resp.status) in range(200, 300)):
        links = extract_next_links(url, resp)
        pageLength = tokenize_page(url, resp)

        # lenFile = open('text/length.txt', '+a')
        # urlFile = open('text/URLs.txt', '+a')

        if int(resp.status) != 200:
            f.write(str(url) + ' <' + str(resp.status) + '>\n')

        # lenFile.write(str(pageLength) + ' ')
        # urlFile.write(url + '\n')
        doc = {
            "url": "",
            "length": 0
        }
        doc["url"] = url
        doc["length"] = pageLength

        urlCol.insert_one(doc)

        # urlFile.close()
        # lenFile.close()

        return links
    else:
        # Output links that don't output status between 200 and 299
        f.write(str(url) + ' <' + str(resp.status) + '>\n')

    f.close()
    return list()

def tokenize_page(url, resp):
    try:
        soup = BeautifulSoup(resp.raw_response.content, 'html.parser')

        # Tokenize the page with regex split
        tokens_raw = list(re.split(r'[^a-zA-Z0-9]', soup.get_text().lower()))

        # Initialize list of stop words from NLTK
        stop_words = set(stopwords.words('english'))
        tokens_filtered = list()

        # Filter out stop words, append text to tokens.txt
        # f = open('text/tokens.txt', '+a')
        for token in tokens_raw:
            if (token not in stop_words) and len(token) > 1:
                tokens_filtered.append(str(token))
                # f.write(str(token) + ' ')
        # f.close()
        map = computeWordFrequencies(tokens_filtered)
        for t in map:
            doc = {
            "token": '',
            "count": map[t]
            }
            doc["token"] = t;

            if(tokenCol.find_one({'token': t}) == None):
                # print("token not found, inserting")
                tokenCol.insert_one(doc)
            else:
                # print ("token found... need to update")
                tokenCol.update_one({'token': t}, {"$inc": {'count' : map[t]}})


        # Return the number of tokens in the page after stop word filter
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

        # Get all links on the page
        for link in soup.find_all('a'):
            # Append to the list if is_valid()
            if is_valid(link.get('href')):
                urlList.append(link.get('href'))
    except:
        f = open("text/errors.txt","a+")
        f.write("Has extract error: " + url + "\n")
        f.close()

    return urlList

# Called check_robots in is_valid(), but commented out since it's slow
# Causes the crawler to run very slow, likely due to having to download the webpage???
# Needs optimizing
def check_robots(url):
    try:
        parsed = urlparse(url)

        # Create the URL to the robots.txt
        # e.g. if the URL passed is 'https://www.stat.uci.edu/contact-the-department/'
        #      we change it to 'https://www.stat.uci.edu/robots.txt'
        robotsURL = str(parsed.scheme) + '://' + str(parsed.netloc) + '/robots.txt'

        # Create the robot parser, set the URL to robotsURL, then read the robots.txt
        readRobots = robotparser.RobotFileParser()
        readRobots.set_url(robotsURL)
        readRobots.read()

        # Check if the URL we passed can be fetched
        # '*' is the USERAGENT
        # parsed.path is the path we check against robots.txt
        return readRobots.can_fetch('*', parsed.path)
    except:
        f = open("text/errors.txt","a+")
        f.write("No robots.txt: " + url + "\n")
        f.close()
        return True

def is_valid(url):
    try:
        parsed = urlparse(url)
        listURLs = ['ics.uci.edu', 'cs.uci.edu',
                    'informatics.uci.edu', 'stat.uci.edu',
                    'today.uci.edu/department/information_computer_sciences']

        if parsed.scheme not in set(["http", "https"]):
            return False

        # Check if the domain is in the scope of the assignemnt
        validNetLoc = False
        for netloc in listURLs:
            if(netloc in parsed.netloc):
                validNetLoc = True
        if not validNetLoc:
            return False

        #if not check_robots(url):
            #return False

        # Completely skip URLs with fragments since they're internal references
        if len(parsed.fragment):
            f = open("text/errors.txt","a+")
            f.write("Skipped internal reference: " + url + "\n")
            f.close()
            return False

        return not re.match(r"^.*\b(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz"
            + r"|calendar|calendars|event|events"
            + r"|comment|response|respond|ppsx)\b.*$", url.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


def computeWordFrequencies(tokenized):
    # loop through tokens

    map = {}
    for x in tokenized:
        # if exists, up the counter.
        # if doesn't exist, add.
        if x in map:
            map[x] += 1
        else:
            map[x] = 1

    return map
