import pint 		as config

from dateutil 		import relativedelta 	as rd
from praw.models 	import Comment
from praw.models 	import Submission
from datetime 		import timedelta

import datetime 	as dt
import sqlite3
import praw
import re
import time
import sys

#DEVELOPMENT VERSION FOR STREAMING
#pip install --upgrade https://github.com/praw-dev/praw/archive/master.zip

sub_name 		= "casualuk"
comment_limit 	= 20
post_limit 		= 20
sleep_seconds 	= 60

trigger_word 	= ["wetherspoons","wetherspoon"]

bot_version 	= 0.5
user_agent 		= "/r/{0} bot to check for Wetherspoons in posts and comments - v{1}".format(sub_name, bot_version)

db_name 		= "wetherspoons.db"
tbl_last 		= "wsLast"

test 			= True
debug 			= True
show_sql		= False

def BotLogin():

	print("Logging in as %s..." %config.username) 	#LOGIN USING CREDENTIALS FROM CONFIG FILE (SEPERATE FILE)
	r = praw.Reddit(username = config.username,
					password = config.password,
					client_id = config.client_id,
					client_secret = config.client_secret,
					user_agent = user_agent)
					
	print("Logged in at {0}".format(CurrentTime()))
	print("Subreddits: {0}".format(sub_name))
	print("\n"*3)

	#SEND THE LOGGED IN OBJECT BACK
	return r

def ProcessComments(r):

	print("*"*50)
	print("Starting ProcessComments...\n")
	
	try:
		print("Getting {0} comments...".format(comment_limit))	
		comments = list(r.subreddit(sub_name).comments(limit=comment_limit))
	except:
		print("#"*35)
		print("ERROR GETTING COMMENTS FROM REDDIT")
		print("#"*35)
		return

	try:
		print("Getting {0} posts...\n".format(post_limit))
		posts = list(r.subreddit(sub_name).new(limit=post_limit))
	except:
		print("#"*35)
		print("ERROR GETTING POSTS FROM REDDIT")
		print("#"*35)
		return
		
	#COMBINE LISTS
	all_items = comments + posts
	
	for item in reversed(all_items):

	#STREAMING TURNED OFF
	#for item in r.subreddit(sub_name).stream.submissions():
	
			#if debug:
			#	print(item.id)
		
			#IGNORE COMMENT BY ITSELF
			if str(item.author).lower() == config.username.lower():
				if debug:
					print("{0} - Ignoring bot comment...\n".format(item.id))
			
				continue
		
			#RESET
			is_comment = False
	
			#IF IT'S A COMMENT
			if isinstance(item, Comment):
				is_comment = True
				item_type = "comment"
			else:
				item_type = "submission"
			
			#GET THE COMMENT BODY
			if is_comment:
				item_body = item.body.lower()
			else:
				if isinstance(item, Submission):
					item_body = item.selftext.lower()
	
			if any(word in item_body for word in trigger_word):

				print("{0} - {1}".format(item.id, item_type))
				
				strSQL = "SELECT CommentID FROM {0} WHERE CommentID = ?".format(tbl_last)
				
				if show_sql:
					print("\t\t{0}".format(strSQL))
				
				cur.execute(strSQL, (item.id,))
				
				if cur.fetchone():
					print("\tAlready drank from this glass.\n")
					continue

				#################
				#    MAX TIME
				#################
				
				strSQL = "SELECT Max(PostTime) FROM {0}".format(tbl_last)
				
				if show_sql:
					print("\t\t{0}".format(strSQL))
				
				cur.execute(strSQL)
				
				#IF NOTHING RETURNED, USE A FAKE DATE (FOR FIRST TIME)
				try:
					max_time = dt.datetime.strptime(cur.fetchone()[0],('%Y-%m-%d %H:%M:%S'))
				except:
					max_time = (CurrentTime() - dt.timedelta(days=1))
				
				#ADD TO DATABASE AFTER MAX VALUE
				new_time = dt.datetime.strptime(ConvertUTC(item.created_utc),('%Y-%m-%d %H:%M:%S'))
				
				print("\tNew Time: {0}".format(new_time))
				
				strSQL = "INSERT INTO {0} Values(?, ?, ?, ?, ?)".format(tbl_last)

				if show_sql:
					print("\t\t{0}".format(strSQL))
				
				if is_comment:
					sub_id = str(item.submission.id)
				else:
					sub_id = item.id
				
				cur.execute(strSQL, (CurrentTime(), str(item.author), str(item.id), sub_id, new_time,))
				
				print("\tMax time: {0}".format(max_time))
				
				#####################
				#    PROCESS TIME
				#####################
				
				#difference = rd.relativedelta(new_time, max_time)				
				difference = new_time - max_time
				
				#difference = difference.hours
				difference = float(difference.total_seconds())
				
				#IF UNDER 1 HOUR
				if abs(difference/60/60) < 1:
					
					#IF UNDER 1 MINUTE
					if abs(int(difference/60)) < 1:
						
						#SHOW TOTAL SECONDS
						time_unit = "{0} seconds".format(int(difference))
					
					else:

						if abs(int(difference/60)) == 1:

							#SHOW TOTAL MINUTES
							time_unit = "{0} minute".format(int(difference/60))
							
						else:
						
							#SHOW TOTAL MINUTES
							time_unit = "{0} minutes".format(int(difference/60))
				
				else:
					
					#IF ITS 1 HOUR
					if abs(int(difference/60/60)) == 1:
						
						#SINGULAR HOUR
						time_unit = "{0} hour".format(int(difference/60/60))
					
					else:
						
						#PLURAL HOURS
						time_unit = "{0} hours".format(int(difference/60/60))
					
				
				print("\tDifference: {0}\n".format((time_unit)))
				
				#IF IT IS A POSITIVE DIFFERENCE, THEN UPDATE IT
				if difference >= 0:
				
					reply_msg = "CasualUK has proudly gone _{0}_ without a Wetherspoons {1}.\n".format(time_unit, item_type.lower())
				
					if not test:
						print("\tPulling pint...")
						comm = item.reply(reply_msg)
					else:
						print("\t{0}".format(reply_msg))

				if debug:
					time.sleep(3)

	sql.commit()				
	print("*"*50)
	print("Finishing ProcessComments...\n")
	
def CurrentTime():
	return dt.datetime.today().replace(microsecond=0)

def ConvertUTC(utcTime):
	result =  dt.datetime.fromtimestamp(int(utcTime)).strftime('%Y-%m-%d %H:%M:%S')
	return result

def db_check():

	print("Checking database...")
	#CONNECTION TO DATABASE GLOBALLY
	
	#RUN ONLY ONCE EVERYTIME YOU RUN IT
	cur.execute("CREATE TABLE IF NOT EXISTS %s (ProcessedTime TEXT, Redditor TEXT, CommentID TEXT, SubmissionID TEXT, PostTime TEXT)" %tbl_last)
	
try:
	print("Connecting to {0}...".format(db_name))
	sql = sqlite3.connect(db_name)
	cur = sql.cursor()
except:
	print("ERROR - QUITTING - {0} database not found!".format(db_name))
	sys.exit()

r = BotLogin()
db_check()

while True:

	if r:
		ProcessComments(r)
	
	print("Sleeping for {0} seconds...".format(sleep_seconds))
	time.sleep(sleep_seconds)