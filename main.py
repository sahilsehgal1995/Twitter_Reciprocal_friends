"""
@Copyright Sahil Sehgal | SU ID: 343-933-724

Program for finding reciprocal friends of 100 users who are connected internally.
Check more info in Readme.md file
"""

import sys
import time
from urllib.request import URLError
from http.client import BadStatusLine
import twitter
import networkx as nx
import matplotlib.pyplot as plt

class TwitterHelper():
	"""
	Docstring for TwitterHelper
	Twitter Helper class which will make twitter requests and handle all the errors.
	Source: Twitter Cookbook
	"""
	CONSUMER_KEY = 'Ud6qUZ7tYU9hjxKpAHRBY9rYD'
	CONSUMER_SECRET = 'MrpXsMRiNxwHoIlvt4AuETwaBJT8jlFt3LEZv1rWnEchIrdn7d'
	OAUTH_TOKEN = '831134511274483712-mEZ6SQxqS5ZXsOFjI361y2uCllObclA'
	OAUTH_TOKEN_SECRET = 'VTphzGsZWMQnGrctjBOiyU95wnHwj8Y2bwq1oNcrivzSQ'


	def __init__(self):
		# Constructor function instanciating an twitter_api function used for making twitter request
		self.auth = twitter.oauth.OAuth(self.OAUTH_TOKEN, self.OAUTH_TOKEN_SECRET,
			self.CONSUMER_KEY, self.CONSUMER_SECRET)

		self.twitter_api = twitter.Twitter(auth=self.auth)


	def make_twitter_request(self, twitter_api_func, max_errors=10, *args, **kw):
		# A nested helper function that handles common HTTPErrors. Return an updated
	    # value for wait_period if the problem is a 500 level error. Block until the
	    # rate limit is reset if it's a rate limiting issue (429 error). Returns None
	    # for 401 and 404 errors, which requires special handling by the caller.

	    def handle_twitter_http_error(e, wait_period=2, sleep_when_rate_limited=True):
	    	# Error handling function for handling all the type of network and server errors.
    
	        if wait_period > 3600: # Seconds
	            print (sys.stderr , ' Too many retries. Quitting.', sep=' ')
	            raise e
	    
	        # See https://dev.twitter.com/docs/error-codes-responses for common codes
	    
	        if e.e.code == 401:
	        	# Network error 401 For handling unauthorized request.
	            print (sys.stderr, 'Encountered 401 Error (Not Authorized)', sep=' ')
	            return None

	        elif e.e.code == 403:
	        	# Network error 403, For handling request which are rejected by Twitter API
	            print (sys.stderr, 'Encountered 404 Error (Request understood but refused)', sep=' ')
	            return None

	        elif e.e.code == 404:
	        	# Network error 404, For handling url not found requests.
	            print (sys.stderr, 'Encountered 404 Error (Not Found)', sep=' ')
	            return None

	        elif e.e.code == 429: 
	        	# Network Error 429, For handling rate limit calls.
	            print (sys.stderr, 'Encountered 429 Error (Rate Limit Exceeded)', sep=' ')
	            if sleep_when_rate_limited:
	                print (sys.stderr, "Retrying in 15 minutes...ZzZ...", sep=' ')
	                sys.stderr.flush()
	                time.sleep(60*15 + 5)
	                print (sys.stderr, '...ZzZ...Awake now and trying again.', sep=' ')
	                return 2

	            else:
	            	# Caller must handle the rate limiting issue
	                raise e

	        elif e.e.code in (500, 502, 503, 504):
	        	# Exception for handling rest server related errors.
	            print (sys.stderr, 'Encountered %i Error. Retrying in %i seconds' % \
	                (e.e.code, wait_period), sep=' ')
	            time.sleep(wait_period)
	            wait_period *= 1.5
	            return wait_period

	        else:
	        	# Raise an exception if nothing is matched.
	            raise e


	    wait_period = 2 
	    error_count = 0 

	    while True:
	        try:
	            return twitter_api_func(*args, **kw)
	        
	        except twitter.api.TwitterHTTPError as e:
	            error_count = 0 
	            wait_period = handle_twitter_http_error(e, wait_period)
	            if wait_period is None:
	                return
	        except URLError as e:
	            error_count += 1
	            time.sleep(wait_period)
	            wait_period *= 1.5
	            print (sys.stderr, "URLError encountered. Continuing.", sep=' ')
	            if error_count > max_errors:
	                print (sys.stderr, "Too many consecutive errors...bailing out.", sep=' ')
	                raise
	        except BadStatusLine as e:
	            error_count += 1
	            time.sleep(wait_period)
	            wait_period *= 1.5
	            print (sys.stderr, "BadStatusLine encountered. Continuing.", sep=' ')
	            if error_count > max_errors:
	                print (sys.stderr, "Too many consecutive errors...bailing out.", sep=' ')
	                raise


class Twitter(TwitterHelper):
	"""
	Docstring for Twitter class
	Twitter API class for finding reciprocal friends, search user, generate graph.
	"""

	# private variable for storing all the user IDs and their reciprocal friends
	usersDirectory = {}

	def __init__(self):
		# Constructor function invoking TwitterHelper class which will instantiate the twitter_api variable
		TwitterHelper.__init__(self)

	def search_user(self, SEARCH_TEXT):
		"""
		Search user method accepting twitter ID or names and performing following functions
		1. Search twitter database and look for matching user.
		2. Fetch reciprocal friends using other class methods.
		3. Call create graph method to generate the network graph.
		""" 

		if(SEARCH_TEXT == ""):
			# Handling base case if user didn't enter any output.
			print ("User input required.")
			return

		results = self.make_twitter_request(self.twitter_api.users.search, q = SEARCH_TEXT)

		if results is None or len(results) == 0:
			print ("User not found.")
			return

		# Fetch results for first user found.
		user = results[0]

		print("@%s | ID: %d" % (user["screen_name"], user["id"]))
		print("Friend Count: %d" % (user["friends_count"]))
		print("Followers Count: %d\n" % (user["followers_count"]))

		# Queue for storing all the users IDS
		queue = [user['id']]

		# CurrentUserIndex for which reciprocal friends are being searched.
		currentUserIndex = 0

		while(len(queue) < 100 and currentUserIndex < len(queue)):

			# Window length for performing breadth first search.
			windowLength = len(queue)

			self.usersDirectory[ queue[currentUserIndex] ] = []

			# Calling find_reciprocal_friends function to get all the reciprocal friends
			reciprocalFriends = self.find_reciprocal_friends(queue[currentUserIndex])

			if reciprocalFriends is None:
				currentUserIndex += 1
				continue

			for friend in reciprocalFriends:
				
				if(friend['id'] in queue or len(queue) > 100):
					# If user already exists in the list or the total count is more than 100, continue
					continue

				queue.append(friend['id'])
				
				# Add id to the friend list of the current user 
				self.usersDirectory[queue[currentUserIndex]].append(friend['id'])

			currentUserIndex += 1

			print("Users found: %d" % (len(queue)))

		print ("Search completed with %d users found" % (len(self.usersDirectory.keys())))
		self.create_graph()


	def find_reciprocal_friends(self, userId):
		# Reciprocal friend function returning top 5 friends IDs based on followers count who are both friends and followers. 

		ids = list(set(self.get_followers(userId)) & set(self.get_friends(userId)))

		reciprocalFriends = self.make_twitter_request(self.twitter_api.users.lookup, user_id = ids)

		if reciprocalFriends == None:
			return []

		print ("User Id: %d has %d reciprocalFriends " % (userId, len(reciprocalFriends)))

		return (sorted(reciprocalFriends, key = lambda i: i["followers_count"],reverse=True))[:5]


	def get_followers(self, userId):
		# Get list of IDs of all the followers of the given userId
		
		followers = self.make_twitter_request(self.twitter_api.followers.ids, user_id = userId, count = 5000)
		
		if followers is None:
			return []

		return followers['ids']


	def get_friends(self, userId):
		# Get list of IDs of all the friends of the given userId
		
		friends = self.make_twitter_request(self.twitter_api.friends.ids, user_id = userId, count = 5000)

		if friends is None:
			return []
		
		return friends['ids']


	def create_graph(self):
		# Method for generating a graph, calculating average distance and diameter using networkx package.
		# Finally saving the image of the graph using matplot.lib package

		
		G=nx.Graph()

		for k,v in self.usersDirectory.items():
			for x in v:
				G.add_edge(k,x)

		try:
			diameter = 0
			averageDistance = 0
			nx.draw(G, with_labels = True)
			
			plt.savefig("twitter.png")

			if(len(list(G.nodes)) == 0):
				print("No connecting nodes are found for calculating diameter and average distance")

			else:
				diameter = nx.diameter(G)
				averageDistance =nx.average_shortest_path_length(G)

			print ("Diameter of Graph: %d" % (diameter))
			print ("Average distance of Graph: %d" % (averageDistance))

		except Exception as e:
			print ("Sorry couldn't create graph or find distance or calculate average distance.")
			print ("Error: " % str(e))


if __name__ == '__main__':
	# Main function instanciating twitter_obj and asking for twitter ID / Name.
	twitter_obj = Twitter()
	twitterID = input("Enter twitter ID you want to search?\n")
	twitter_obj.search_user(twitterID)

# End of Program