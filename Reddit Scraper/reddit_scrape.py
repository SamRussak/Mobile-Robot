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

 