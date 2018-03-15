import re
import os
import sys
import getopt

def find_match_in_corpus(regex):
    print("Searching for pattern that matches the regex pattern r'{}' in the corpus...".format(regex))
    input_dir_raw = os.path.join('extracted-text', '')
    input_dir_processed = os.path.join('processed-text', '')

    regex = regex.casefold()
    isFound = False
    
    print("Searching for pattern {} in 'extracted-text\\'...".format(regex))
    for filename in os.listdir(input_dir_raw):
        filepath = os.path.join(input_dir_raw, filename)
        file_reader = open(filepath, encoding='utf-8', errors='ignore')
        content = file_reader.read().casefold()
        
        if (re.search(regex, content) != None):
            isFound = True
            print("\t[Found match]'{}'.".format(filename))
        
        file_reader.close()
    
    # print("Searching for pattern {} in 'processed-text\\'...".format(regex))
    # for filename in os.listdir(input_dir_processed):
        # filepath = os.path.join(input_dir_processed, filename)
        # file_reader = open(filepath, encoding='utf-8', errors='ignore')
        # content = file_reader.read()
        
        # if (re.search(regex, content) != None):
            # isFound = True
            # print("\t[Found match]'{}'.".format(filename))
        
        # file_reader.close()

    if(not isFound):
        print("No match found in corpus.")

    return

if (__name__ == '__main__'):
    args = sys.argv
    if(len(args) != 2):
        print("Usage: A regex pattern must be given as a cmd arg.")
        sys.exit(2)

    regex = args[1]
    find_match_in_corpus(regex)
    print("FindInCorpus.py has finished running :)")
