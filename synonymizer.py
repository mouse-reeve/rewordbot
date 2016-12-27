''' reword bot '''
import random
import re
import settings
from wordnik.swagger import ApiClient
from wordnik.WordApi import WordApi

def reword(text):
    ''' replace words with synonyms '''

    # tokenize
    tokens = text.split(' ')

    # find synonyms
    client = ApiClient(settings.WORDNIK_API_KEY, 'http://api.wordnik.com/v4')
    wordnik_api = WordApi(client)

    reworded = []
    for word in tokens:
        word = re.sub(r'[\.,\?!]', '', word)

        results = wordnik_api.getRelatedWords(word, useCanonical=True,
                                              relationshipTypes='synonym')
        try:
            options = results[0].words
            reworded.append(random.choice(options))
        except TypeError:
            reworded.append(word)

    # restructure text
    return ' '.join(reworded)


if __name__ == '__main__':
    sentence = 'I love to talk about nothing. ' \
               'It\'s the only thing I know anything about.'
    print reword(sentence)

