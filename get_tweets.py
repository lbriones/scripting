
from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener
#import MySQLdb
import time
import json

#        replace mysql.server with "localhost" if you are running via your own server!
#                        server       MySQL username	MySQL pass  Database name.
#conn = MySQLdb.connect("mysql.server","beginneraccount","cookies","beginneraccount$tutorial")

#c = conn.cursor()


#consumer key, consumer secret, access token, access secret.
ckey="NhKXNHp5u9yTtNZdmHGs5NCtd"
csecret="LKHqoFsCCAnPZGe9IXEkwpCv0LQVvdtvRJSqPkKnKpuILr22ml"
atoken="523419774-rXzTBTkVQW6XqO7vimDhSf5l6TgAPiJAwuyiN13t"
asecret="yncMCCkfPPwz0d22BfszVVamKiQ5b1Os7fkn4mCTNduqx"

class listener(StreamListener):

    def on_data(self, data):
        all_data = json.loads(data)
        if  not all_data["text"].startswith('RT'):
            #Do processing here 
            
            tweet = all_data["text"].encode('ascii', 'ignore')
            
            username = all_data["user"]["screen_name"]
            
            #c.execute("INSERT INTO taula (time, username, tweet) VALUES (%s,%s,%s)",
            #    (time.time(), username, tweet))
    
            #conn.commit()
    
            print((username,tweet))
            
            return True

    def on_error(self, status):
        print status

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["Justin Bieber"])
