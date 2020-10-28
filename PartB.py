from PartA import Tokenizer
from sys import argv

# Copying a list into a set in linear in time relative to input size. 
# O(N) + O(M) where N and M are the sizes of each of the list of tokens. 
# Taking the intersection of those two sets is also linear in time relative to input size
# O(min(len(N), len(M))) Iterate through the smaller set and check in constant time O(1) if that element is in the larger set.
# Also stated in https://wiki.python.org/moin/TimeComplexity that built in set intersection is on average linear time.
#
# O(N) + O(M) + O(min(N, M)) = O(max(N, M))
# In general the function runs in linear time. More specifically, linear in respect to the longer list of tokens.
def common_tokens(tokens1, tokens2):
    tokens1 = set(tokens1)
    tokens2 = set(tokens2)

    return len(tokens1 & tokens2)


if __name__ == '__main__':
    if len(argv) >= 3:
        tokens1 = Tokenizer.tokenize(argv[1])
        tokens2 = Tokenizer.tokenize(argv[2])

        print(common_tokens(tokens1, tokens2))
    else:
        print(f'Insufficient file arguments. Expected 2 but got {len(argv) - 1}.')