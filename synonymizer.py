''' reword bot '''
from nltk import pos_tag, word_tokenize
import random
import re
import settings
import time
from wordnik.swagger import ApiClient
from wordnik.WordApi import WordApi

wordcache = {}
client = ApiClient(settings.WORDNIK_API_KEY, 'http://api.wordnik.com/v4')
wordnik_api = WordApi(client)

def reword(text):
    ''' replace words with synonyms '''

    # tokenization and part of speech taggin
    tokens = pos_tag(word_tokenize(text))
    print tokens

    # find synonyms
    reworded = []
    for token in tokens:
        word, pos = token
        original = word

        # only convert nouns, verbs, and adjs, and check for if it's a word
        if not re.match(r'NN|VB|JJ', pos) or not re.sub(r'\W', '', token[0]):
            reworded.append(original)
            continue

        word = word.lower()

        # find synonyms
        new_word = get_synonym(word)

        # restore formatting
        if len(original) > 1 and re.match(r'^[A-Z]+$', original):
            # all caps
            new_word = new_word.upper()
        elif re.match(r'^[A-Z]', original):
            # first letter cap
            new_word = new_word[0].upper() + new_word[1:]
        # any other capitalization patterns can lump it

        # real janky punctuation restoration
        if re.match(r'^[\"\']', original):
            new_word = original[0] + new_word
        if re.match(r'[\"\'\.,;?!]', original[-1]):
            new_word += original[-1]

        reworded.append(new_word)

    # restructure text
    return ' '.join(reworded)


def get_synonym(word):
    ''' lookup synonyms for a word in cache or from api '''
    if word not in wordcache:
        results = wordnik_api.getRelatedWords(word, useCanonical=True,
                                              relationshipTypes='synonym')
        time.sleep(0.5)
        try:
            wordcache[word] = results[0].words + [word]
        except TypeError:
            # presumably, no synonyms found, just use the token word
            wordcache[word] = [word]
    return random.choice(wordcache[word])


if __name__ == '__main__':
    sentence = 'I love to talk about nothing. ' \
               'It\'s the only thing I know anything about.'
    print reword(sentence)
