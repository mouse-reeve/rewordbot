''' reword bot '''

import re
import settings
from TwitterAPI import TwitterAPI


sentence = 'I love to talk about nothing. ' \
           'It\'s the only thing I know anything about.'

api = TwitterAPI(settings.TWITTER_API_KEY, settings.API_SECRET,
                 settings.TWITTER_ACCESS_TOKEN, settings.ACCESS_SECRET)

# tokenize
tokens = sentence.split(' ')

# find synonyms
for word in tokens:
    word = re.sub(r'[\.,?!]', '', word)


# restructure text

# tweet
