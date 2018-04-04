import re
import os
import sys
import getopt

def list_doc_by_idx(idx_list):
    """
    Prints the names of text files in "processed-text\" according
    to the index in the same order
    """
    print("Printing names of documents " + str(idx_list))
    input_dir_processed = os.path.join('processed-text', '')
    num_to_list = len(idx_list)
    idx_set = set(idx_list)
    idx_2_filename_map = dict()
    
    currIdx = 1
    count = 0
    for filename in os.listdir(input_dir_processed):
        if(currIdx in idx_set):
            count += 1
            idx_2_filename_map[currIdx] = os.path.splitext(filename)[0]
        
        currIdx += 1
        if (count == num_to_list):
            break
    
    # Print filenames
    for idx in idx_list:
        print('    {} -'.format(idx), idx_2_filename_map[idx])

    return

if (__name__ == '__main__'):
    """
    Expects a command line arg to be:
    $ python ListDocByIdx 10 2 5 9
    """
    args = sys.argv
    
    idx_list = []
    if (len(args) < 2):
        print("No cmd line args detected, using hardcoded doc indices")
        idx_list = []
    else:
        idx_list = [int(docIdx) for docIdx in args[1:]]

    list_doc_by_idx(idx_list)
    
