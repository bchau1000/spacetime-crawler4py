import re
from collections import defaultdict
from collections import OrderedDict
from urllib.parse import urlparse
import itertools 

def tokenCount():
    textList = list()
    textFile = open('text/tokens.txt', 'r')
    for line in textFile:
        textList.extend(line.split())
    textFile.close()

    return textList

def computeWordFrequencies(tokenList):
    if not tokenList:
        print("List is empty.")
        return {}
    else:
        tokenDict = defaultdict(int)

        for i in tokenList:
            if not i.isnumeric() and len(i) > 2:
                tokenDict[i] += 1;

        return tokenDict

def printList(tokenDict):
    if not tokenDict:
        print("Dictionary is empty.")
        return;
    else:
        f = open('report/top50tokens.txt', '+a')
        sortDict = dict(sorted(tokenDict.items(), key=lambda x: x[1], reverse=True))
        out = dict(itertools.islice(sortDict.items(), 50))
        rank = 1
        for i, j in out.items():
            f.write(str(rank) + '. ' + str(i) + ' = ' + str(j) + '\n')
            rank += 1
            
def getLargestLength():
    f = open('text/length.txt', 'r')
    lengthList = list()
    for line in f:
        lengthList.extend(line.split())
        
    maxLen = int(lengthList[0])
    for i in lengthList:
        if int(i) > maxLen:
            maxLen = int(i)
    f.close()
    
    return maxLen

def getSubdomains(fileName):
    f = open(str(fileName), 'r')
    subdomains = defaultdict(int)
    
    for url in f:
        url = url.strip('\n')
        parsed = urlparse(str(url))
        netloc = parsed.netloc.lower()
        if 'www' in netloc:
            netloc = netloc[4: len(url)]
            
        
        if len(netloc):
            subdomains[netloc] += 1
        
    return subdomains

def main():
    f = open('report/subdomains.txt', '+a')
    tokenList = tokenCount()
    tokenDict = computeWordFrequencies(tokenList)
    printList(tokenDict)
    print('The longest page had ' + str(getLargestLength()) + ' tokens.')
    subdomains = getSubdomains('text/URLs.txt')

    total = 0
    for subdomain, count in sorted(subdomains.items()):
        total += count
        f.write(str(count) + ' ' + str(subdomain) + '\n')
        
    print(str(total) + ' unique links.')

main()