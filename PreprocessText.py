import re
import os
import sys
import getopt
from collections import Counter
from nltk.stem.porter import PorterStemmer
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize
from nltk.corpus import stopwords
import unidecode

def remove_punctuations(string):
    assert(type(string) == str)
    modified_string = re.sub(r"['\-]+(\w)", r'\1', string)
    modified_string = re.sub(r'[^a-zA-Z0-9\s]', ' ', modified_string)
    return modified_string

def tokenize_string(string):
    return word_tokenize(string)

# TODO: Remove. Debugging
lemmatized_dict = dict()
def lemmatize_tokens(list_of_tokens):
    """
    Pre-conditions:
    - list_of_tokens must be a list of strings to lemmatize
    """
    assert(type(list_of_tokens) == list)
    
    lmtzr = WordNetLemmatizer()
    lemmatized_tokens = [lmtzr.lemmatize(token) for token in list_of_tokens]
    
    # TODO: Remove. Debugging
    for (s1, s2) in zip(list_of_tokens, lemmatized_tokens):
        if (s1 not in lemmatized_dict and s1 != s2):
            lemmatized_dict[s1] = s2
    
    return lemmatized_tokens

def stem_tokens(list_of_tokens):
    """
    Pre-conditions:
    - list_of_tokens must be a list of strings to stem
    """
    assert(type(list_of_tokens) == list)
    
    stemmer = PorterStemmer()
    stemmed_tokens = [stemmer.stem(token) for token in list_of_tokens]
    return stemmed_tokens

def remove_eng_stopwords(string):
    """
    Tokenizes the given string, remove tokens which are identified as stopwords
    by nltk, and join the tokens back (separated by a space) to form a string.
    """
    stopwords_set = set(stopwords.words('english'))
    
    words = tokenize_string(string)
    return ' '.join([word for word in words if word not in stopwords_set])

def remove_newlines(s):
    """Replaces all newline characters with ' '."""
    res = re.sub(r"[\r\n|\n|\r]", ' ', s)
    return res

def preprocess_string(s, doStemming=False, doLemmatization=False):
    """
    Proprocessing operations
        - Replace r"-[\r\n|\n]" with ''
        
        - casefold()
        - Remove stopwords
        - Accent-folding using unidecode.unidecode(accented_string)
        - Replace r"[-.'´¨]" with ''
        - Remove punctuations r"[^\w\d]" with ''
        - Remove pure numbers r"\s\d+\s" with ''
        - Join multiple spaces
        - stemming (??)
    """
    
    s = re.sub(r"-[\r\n|\n|\r]", '', s)
    s = s.casefold()
    s = remove_eng_stopwords(s)
    s = unidecode.unidecode(s)  # Remove accented chars
    s = re.sub(r"[´¨]", '', s)
    s = remove_punctuations(s)
    s = re.sub(r"\b\d+\b", '', s)  # Remove fully numeric terms
    s = re.sub(r"\s+", ' ', s)

    tokens = tokenize_string(s)
    MIN_TOKEN_CHAR_NUM = 3
    MAX_TOKEN_CHAR_NUM = 20
    tokens = [token for token in tokens if ((len(token) >= MIN_TOKEN_CHAR_NUM)
                                            and (len(token) <= MAX_TOKEN_CHAR_NUM))]
    
    if (doLemmatization):
        tokens = lemmatize_tokens(tokens)

    if (doStemming):
        tokens = stem_tokens(tokens)

    s = ' '.join(tokens)
    
    return s

def remove_common_and_rare_words(corpus_dir, max_allowable_percentage = 90,
                                 min_wordfreq = 3):
    """
    Parses all text documents in corpus_dir and remove words with appearance
    percentages above max_allowable_percent of all files.

    Pre-condition(s):
    - corpus_dir should be a directory that contains text files which are
    properly processed to be tokenized and directly stored in a dictionary
    - Each text file in corpus_dir should represent a document
    """
    assert(os.path.exists(corpus_dir) and os.path.isdir(corpus_dir))
    assert(max_allowable_percentage <= 100 and max_allowable_percentage > 0)

    corpus_size = 0
    docfreq_counter = Counter()
    wordfreq_counter = Counter()
    terms_2_filenames_set = dict()

    # Parsing corpus and computing terms statistics
    print('Collecting corpus terms statistics...')
    for filename in os.listdir(corpus_dir):
        filepath = os.path.join(corpus_dir, filename)
        corpus_size += 1

        file_reader = open(filepath, encoding='utf-8', errors='ignore')
        content = file_reader.read()
        tokens = tokenize_string(content)
        tokens_set = set(tokens)
        docfreq_counter.update(tokens_set)
        wordfreq_counter.update(tokens)

    max_allowable_docfreq = corpus_size * max_allowable_percentage / 100


    # TODO: Debugging
    print('Removing words that appear less than {} times in corpus:'.format(min_wordfreq))
    print(str([term for (term, wordfreq)
               in sorted(wordfreq_counter.items())
               if wordfreq < min_wordfreq]))
    print('Removing words that appear in more than {}({}%) documents:'.format(max_allowable_docfreq, max_allowable_percentage))
    for (term, doc_freq) in ((term, doc_freq) for (term, doc_freq) in sorted(docfreq_counter.items(), key=lambda x: x[1], reverse=True)
                             if doc_freq > max_allowable_docfreq):
        print("\t'{}': Found in {}({}%) documents".format(term, doc_freq, doc_freq/corpus_size * 100))
    
    for filename in os.listdir(corpus_dir):
        filepath = os.path.join(corpus_dir, filename)
        corpus_size += 1

        file_reader = open(filepath, encoding='utf-8', errors='ignore')
        content = file_reader.read()
        tokens = tokenize_string(content)

        filtered_tokens = []
        for token in tokens:
            if (docfreq_counter[token] <= max_allowable_docfreq) and (wordfreq_counter[token] >= min_wordfreq):
                filtered_tokens.append(token)

        s = ' '.join(filtered_tokens)

        file_writer = open(filepath, 'w', encoding='utf-8')
        file_writer.write(s)
        file_writer.close()

def preprocess_text(doStemming=False, doLemmatization=False):
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'i:o:')
    except (getopt.GetoptError):
        print('TextManipulator.py -i <text-dir>')
        sys.exit(2)

    # Default directories
    input_dir = os.path.join('extracted-text', '')
    output_dir = os.path.join('processed-text', '')

    for o, a in opts:
        if (o == '-i'):
            input_dir = a
            assert(os.path.isdir(input_dir) and os.path.exists(input_dir))
            print('Texts directory: ' + os.path.join(os.getcwd(), input_dir))  # TODO: Logging
        elif (o == '-o'):
            output_dir = a
            assert(os.path.isdir(output_dir) and os.path.exists(output_dir))
            print('Output directory: ' + os.path.join(os.getcwd(), output_dir))  # TODO: Logging
        else:
            print('Invalid option: ' + o)

    # Process text
    MIN_FILE_CHAR_NUM = 2000
    
    for filename in os.listdir(input_dir):
        print('Processing: ' + filename[:55] + '...')
        filepath = os.path.join(input_dir, filename)

        file_reader = open(filepath, encoding='utf-8', errors='ignore')
        processed_string = preprocess_string(file_reader.read(), doStemming=doStemming, doLemmatization=doLemmatization)

        if (len(processed_string) < MIN_FILE_CHAR_NUM):
            print('\t[Rejected: Too short] ' + filename)
            continue

        # Write to file
        text_file_obj = open(os.path.join(output_dir, os.path.splitext(filename)[0] + '.txt'), 'w', encoding='utf-8')
        text_file_obj.write(processed_string)
        text_file_obj.close()

    remove_common_and_rare_words(output_dir, max_allowable_percentage=80, min_wordfreq=3)

def docs_2_single_file():
    print("Combining all text files in 'processed-text' into corpus.txt...")
    input_dir = os.path.join('processed-text', '')
    output_writer = open('corpus.txt', 'w', errors='ignore')

    for filename in os.listdir(input_dir):
        filepath = os.path.join(input_dir, filename)
        file_reader = open(filepath, encoding='utf-8', errors='ignore')

        content = file_reader.read()
        output_writer.write(content)
        output_writer.write('\n')
        file_reader.close()

    output_writer.close()
    return

if (__name__ == '__main__'):
    preprocess_text(doStemming=False, doLemmatization=True)
    docs_2_single_file()
    
    # TODO: Remove Debugging
    for s1 in sorted(lemmatized_dict):
        print("\t{} ---(lemmatize)---> {}".format(s1, lemmatized_dict[s1]))
    
    print('Finished running PreprocessText.py! :)')
