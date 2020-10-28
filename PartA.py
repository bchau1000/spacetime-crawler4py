import re
from collections import defaultdict
from sys import argv

class Tokenizer:

    token_cases = [
        r"\W*[A-Za-z0-9]+'?[A-Za-z0-9]*\W*",   # alphanumeric or has apostrophe in the middle or at the end i.e. friend's, friends', they've
        r"\W*'[A-Za-z0-9]+\W*",                # begins with apostrophe i.e. 'twas
        r"\W*([A-Za-z0-9]+)(?:[-,./]+|--)([A-Za-z0-9]+)\W*"    # separated words such as a hyphenated word or tokens in a link
    ]

    # For each line I split it into an array of words which is takes O(M) where M is the number of characters in the line.
    # I loop through the words in each line once and try to match it to the regular expression which is linear
    # relative to the length of the word. So looking through all words in a line for matches is essentially O(M) too.
    # Replacing non-alphanumeric characters to empty characters and making the string lower case are both linear in respect
    # to word size so both operations inside the loop end up summing up to about O(M) as well.
    # To sum it up, I am essentially peforming multiple linear passes over the entire file.
    #  
    # O(N) Tokenizing the file is linear in time with respect to the size of the file.
    @staticmethod
    def tokenize(infile: str) -> [str]:
        res = []
        try:
            with open(infile, encoding='utf-8') as file:
                pattern = re.compile('|'.join(Tokenizer.token_cases))
                while True:
                    try:
                        line = file.readline()
                        if len(line) == 0: break
                        words = line.split() 
                        for word in words: 
                            match = pattern.fullmatch(word)
                            if match:
                                groups = match.groups()
                                if groups[0] != None: # if its a separated token
                                    res.append(groups[0].lower())
                                    res.append(groups[1].lower())
                                else:
                                    res.append(re.sub(r'\W', '', match.string).lower())
                    except Exception as e:
                        print(e)
                      
        except Exception as e:
            print(e)

        return res


    # This function runs in linear time relative to input size (the list of tokens) 
    # because we are looping through the list of tokens once performing constant 
    # time operations.
    # Computing the word frequencies runs in O(N) time where N is the length of the list.
    @staticmethod
    def compute_word_frequencies(tokens: [str]) -> {str: int}:
        res = defaultdict(int)
        for t in tokens:
            res[t] += 1
        return res


    # The call to frequencies.items() creates a list of tuples copied from the dictonary in linear time.
    # Sorting the list of tuples is done in O(NlogN) time.
    # Finally, we do a single pass through the list so printing all items is linear in time relative to input size.
    #
    # The function to print out the dictionary in non-ascending order runs in O(NlogN + N + N) = O(NlogN) time
    # where N is the length of the dictionary.
    @staticmethod
    def print(frequencies: {str: int}) -> None:
        for t, c in sorted(frequencies.items(), key=lambda x: -x[1]):
            print(f'{t} -> {c}')



if __name__ == '__main__':
    if len(argv) >= 2:
        tokens = Tokenizer.tokenize(argv[1])
        word_freq = Tokenizer.compute_word_frequencies(tokens)
        Tokenizer.print(word_freq)
    else:
        print(f'Insufficient file arguments. Expected 1 but got {len(argv) - 1}.')
    