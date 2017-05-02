''' reword bot '''
import argparse
import json
from nltk import pos_tag, word_tokenize
from pattern.en import conjugate, lemma, pluralize, singularize
import random
import re
import settings
import time
from wordnik.swagger import ApiClient
from wordnik.WordApi import WordApi

class Reword(object):
    ''' functionality for rewording text with synonyms '''

    def __init__(self, show_tokens=False, include_all=False):
        client = ApiClient(settings.WORDNIK_API_KEY,
                           'http://api.wordnik.com/v4')
        self.wordnik_api = WordApi(client)
        self.show_tokens = show_tokens
        self.include_all = include_all
        self.wordcache = json.load(open('thesaurus.json'))


    def reword(self, text):
        ''' update words in a block of text'''

        text = text.decode('utf-8')

        # tokenization and part of speech taggin
        # the pattern pos tagger was dropping the first words in each
        # sentence after the first one
        tokens = pos_tag(word_tokenize(text))
        if self.show_tokens:
            print tokens

        # find synonyms
        reworded = []
        for token in tokens:
            word, pos = token
            original = word

            # only convert nouns, verbs, and adjs, and check for if it's a word
            if not re.match(r'NN|VB|JJ', pos) or \
                    not re.sub(r'\W', '', token[0]):
                reworded.append(original)
                continue

            word = strip_word(word, pos)

            # find synonyms
            new_words = self.get_synonym(word, original)

            # only rebuild the word if it might not be the original
            if len(new_words) == 1:
                reworded.append(original)
                continue

            if not self.include_all:
                new_words = [random.choice(new_words)]

            new_words = [reform_word(original, w, pos)  for w in new_words]
            reworded.append('|'.join(new_words))

        # save updated thesaurus to file
        with open('thesaurus.json', 'w') as outfile:
            json.dump(self.wordcache, outfile)

        # restructure text
        text = ' '.join(reworded)

        # remove spaces around punctuation tokens
        text = re.sub(r'\s([\'\.,\?!])', r'\1', text)

        return text.encode('utf-8', 'ignore')


    def get_synonym(self, word, original):
        ''' lookup synonyms for a word in cache or from api '''
        if word not in self.wordcache and original in self.wordcache:
            word = original
        if word not in self.wordcache:
            results = self.wordnik_api.getRelatedWords(
                word, useCanonical=True,
                relationshipTypes='synonym')

            # api politeness -- wait 1/2 a second between queries
            time.sleep(0.5)
            try:
                self.wordcache[word] = results[0].words + [word]
            except TypeError:
                # presumably, no synonyms found, just use the token word
                self.wordcache[word] = [word]

        return self.wordcache[word]


def strip_word(word, pos):
    ''' find lemmas/base forms for words '''
    word = word.lower()

    # singularize
    if pos in ['NNS', 'NNPS']:
        word = singularize(word)
    # lemmatize non-base words (generalized here as penn treebank
    # symbols longer than 2 chars)
    elif len(pos) > 2:
        word = lemma(word)

    return word


def reform_word(original, word, pos):
    ''' decline the newly found synonym '''
    # restore verb conjugation
    if 'VB' in pos and not pos == 'VB':
        word = conjugate(word, pos)

    # restore plurals
    if pos in ['NNS', 'NNPS']:
        word = pluralize(word)

    # restore caps
    if len(original) > 1 and re.match(r'^[A-Z]+$', original):
        # all caps
        word = word.upper()
    elif re.match(r'^[A-Z]', original):
        # first letter cap
        word = word[0].upper() + word[1:]
    # any other capitalization patterns can lump it
    return word


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='reword text with a thesaurus')
    parser.add_argument('--text', '-t',
                        help='text string to be improved')
    parser.add_argument('--file', '-f',
                        help='filename of text file to be improved')
    parser.add_argument('--show_tokens', '-s', action='store_true',
                        help='print tokenized and pos tagged text')
    parser.add_argument('--include_all', '-i', action='store_true',
                        help='embed all synonym options in text')
    args = parser.parse_args()
    if args.file:
        input_text = open(args.file).read()
    elif args.text:
        input_text = args.text
    else:
        input_text = 'I love to talk about nothing. ' \
              'It\'s the only thing I know anything about.'

    print Reword(show_tokens=args.show_tokens,
                 include_all=args.include_all).reword(input_text)
