''' reword bot '''
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

    # tokenize
    text = re.sub(r'([A-z])-([A-z])', r'\1 \2', text)
    tokens = text.split(' ')

    # find synonyms
    reworded = []
    for original in tokens:
        # remove non alphanumeric characters
        word = re.sub(r'\W', '', original)
        word = word.lower()

        if not word:
            # probably it's a bit of punctuation or emoji or something
            reworded.append(original)
            continue

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
            # presumably, no synonyms found, just use the original word
            wordcache[word] = [word]
    return random.choice(wordcache[word])


if __name__ == '__main__':
    sentence = 'I love to talk about nothing. ' \
               'It\'s the only thing I know anything about.'
    print reword(sentence)
