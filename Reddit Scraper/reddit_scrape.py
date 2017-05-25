<<<<<<< HEAD
import pandas as pd
import sys
import csv
import praw
import string


def pri(sub):
	print("Hot:")
	for entries in sub.hot(limit=5):
		print("Title: ", entries.title)
		print("---------------------------------\n")

	print("Rising:")
	for entries in sub.rising(limit=5):
		print("Title: ", entries.title)
		print("---------------------------------\n")


reddit = praw.Reddit('bot1')
sub = reddit.subreddit("worldnews")
pri(sub)
sub = reddit.subreddit("news")
pri(sub)
=======
import pandas as pd
import sys
import csv
import praw
import string

userInput = sys.argv
sub_name = userInput[1]
reddit = praw.Reddit('bot1')
sub = reddit.subreddit(sub_name)

for entries in sub.hot(limit=5):
	print("Title: ", entries.title)
	print("Text: ", entries.url)
	print("Score: ", entries.score)
	print("---------------------------------\n")

 
>>>>>>> origin/master
