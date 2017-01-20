''' reword bot '''
import argparse
import json
from nltk import pos_tag, word_tokenize
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

        # tokenization and part of speech taggin
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

            word = word.lower()

            # find synonyms
            new_word = self.get_synonym(word)

            # restore formatting
            if len(original) > 1 and re.match(r'^[A-Z]+$', original):
                # all caps
                new_word = new_word.upper()
            elif re.match(r'^[A-Z]', original):
                # first letter cap
                new_word = new_word[0].upper() + new_word[1:]
            # any other capitalization patterns can lump it

            reworded.append(new_word)

        # save thesaurus to file
        with open('thesaurus.json', 'w') as outfile:
            json.dump(self.wordcache, outfile)

        # restructure text
        text = ' '.join(reworded)

        # TODO: remove spaces around punctuation tokens

        return text


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
