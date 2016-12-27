''' tweetbot for reword '''
import settings
import synonymizer
from TwitterAPI import TwitterAPI

twitter_api = TwitterAPI(settings.TWITTER_API_KEY,
                         settings.TWITTER_API_SECRET,
                         settings.TWITTER_ACCESS_TOKEN,
                         settings.TWITTER_ACCESS_SECRET)

# tweet
