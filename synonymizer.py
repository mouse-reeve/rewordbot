''' reword bot '''
import random
import re
import settings
from TwitterAPI import TwitterAPI
from wordnik.swagger import ApiClient
from wordnik.WordApi import WordApi


sentence = 'I love to talk about nothing. ' \
           'It\'s the only thing I know anything about.'

twitter_api = TwitterAPI(settings.TWITTER_API_KEY,
                         settings.TWITTER_API_SECRET,
                         settings.TWITTER_ACCESS_TOKEN,
                         settings.TWITTER_ACCESS_SECRET)

# tokenize
tokens = sentence.split(' ')

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
print ' '.join(reworded)

# tweet
