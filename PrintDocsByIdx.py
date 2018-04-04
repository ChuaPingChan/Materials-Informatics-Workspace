import re
import os
import sys
import getopt

def print_all_docs_with_idx():
    input_dir_processed = os.path.join('processed-text', '')
    currIdx = 1
    for filename in os.listdir(input_dir_processed):
        print('\t' + str(currIdx) + '.', filename)
        currIdx += 1
    return

if (__name__ == '__main__'):
    print_all_docs_with_idx()
