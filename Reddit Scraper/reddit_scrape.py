import pandas as pd
import sys
import csv
import praw
import string


reddit = praw.Reddit('bot1')
sub = reddit.subreddit("politics")

for entries in sub.hot(limit=5):
	print("Title: ", entries.title)
	print("Text: ", entries.url)
	print("Score: ", entries.score)
	print("---------------------------------\n")

 