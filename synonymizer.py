''' reword bot '''
import re
import settings
from TwitterAPI import TwitterAPI
from wordnik.swagger import ApiClient
from wordnik.WordApi import WordApi


sentence = 'I love to talk about nothing. ' \
           'It\'s the only thing I know anything about.'

api = TwitterAPI(settings.TWITTER_API_KEY, settings.API_SECRET,
                 settings.TWITTER_ACCESS_TOKEN, settings.ACCESS_SECRET)

# tokenize
tokens = sentence.split(' ')

# find synonyms
client = ApiClient(settings.WORDNIK_API_KEY, 'http://api.wordnik.com/v4')
api = WordApi(client)

for word in tokens:
    word = re.sub(r'[\.,i\?!]', '', word)

    results = api.getRelatedWord(word, useCanonical=True,
                                 relationshipTypes='synonym')
    import pdb;pdb.set_trace()


# restructure text

# tweet
