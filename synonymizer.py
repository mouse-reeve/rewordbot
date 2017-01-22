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

    def __init__(self, show_tokens=False):
        client = ApiClient(settings.WORDNIK_API_KEY,
                           'http://api.wordnik.com/v4')
        self.wordnik_api = WordApi(client)
        self.show_tokens = show_tokens
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
            new_word = self.get_synonym(word)

            new_word = reform_word(original, new_word, pos)
            reworded.append(new_word)

        # save updated thesaurus to file
        with open('thesaurus.json', 'w') as outfile:
            json.dump(self.wordcache, outfile)

        # restructure text
        text = ' '.join(reworded)

        # remove spaces around punctuation tokens
        text = re.sub(r'\s([\'\.,\?!])', r'\1', text)

        return text.encode('utf-8', 'ignore')


    def get_synonym(self, word):
        ''' lookup synonyms for a word in cache or from api '''
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
        return random.choice(self.wordcache[word])


def strip_word(word, pos):
    ''' find lemmas/base forms for words '''
    word = word.lower()

    # lemmatize non-base words (generalized here as penn treebank
    # symbols longer than 2 chars)
    if len(pos) > 2:
        word = lemma(word)

    # singularize
    if pos in ['NNS', 'NNPS']:
        word = singularize(word)

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
    parser.add_argument('--show_tokens', '-s',
                        help='print tokenized and pos tagged text')
    args = parser.parse_args()
    if args.file:
        input_text = open(args.file).read()
    elif args.text:
        input_text = args.text
    else:
        input_text = 'I love to talk about nothing. ' \
              'It\'s the only thing I know anything about.'

    print Reword(show_tokens=args.show_tokens).reword(input_text)
