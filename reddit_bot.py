import praw
from bot_values import client_id, client_secret, username, password, user_agent
from datetime import datetime


reddit= praw.Reddit(client_id=client_id,client_secret=client_secret,username=username,password=password,user_agent=user_agent)
def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results

subreddit = reddit.subreddit('waterdebate47')

stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(subreddit, **kwargs))
user_reports= {}
for post in stream:
	if type(post).__name__ == 'Submission':
		user= post.author #instance of redditor class
		posts=0
		reports=0
		for submission in user.submissions.top('all'):
			if submission.subreddit=='DebateTrade':
				posts+=1
		if user in user_reports:
			reports=user_reports[user]
		else:
			user_reports[user]=0
			reports= user_reports[user]

		print(f'User {user} has {posts} posts in the /r/debatetrade server and {reports} reports')
	elif type(post).__name__ == 'Comment':
		message= str(post.body).split()
		if message[0]=='!report' and message[1][0:3]=='/u/':

			print('________________')

			try:
				z= reddit.redditor(message[1][3:])
				print(z.comment_karma)
			except:
				print(f'Error Occured for user {message[1][3:]}')
			print('----------------')
   

def report(user):
	try:
		user_reports[user]+=1
	except KeyError:
		user_reports[user]=1





