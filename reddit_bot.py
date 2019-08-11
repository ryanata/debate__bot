import praw
from bot_values import client_id, client_secret, username, password, user_agent
from datetime import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import operator

'''
This program uses two main apis- Google Sheets and Reddit praw. A google sheet is updated with every report that runs through
the program. 
'''

scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

creds= ServiceAccountCredentials.from_json_keyfile_name("Debate Trade Bot-50c9eb8adba7.json",scope)

client = gspread.authorize(creds)

sheet_one= client.open('debateBot').sheet1
sheet_two=client.open('debateBot').get_worksheet(1)


reddit= praw.Reddit(client_id=client_id,client_secret=client_secret,username=username,password=password,user_agent=user_agent)

user_reports= {}
reporters={}

reply_template = '[Github](https://github.com/ryanata/debate__bot)'
bottom_text=f'\n\n ______________________________\n\n^(this is a bot. more info can be retrieved here : ) ^{reply_template} '

def report(user):
	try:
		user_reports[user]+=1
	except KeyError:
		user_reports[user]=1
	
def update_sheet():
	sheet_two.resize(rows=1)
	sheet_two.resize(rows=4000)
	sorted_reports = sorted(user_reports.items(), key=operator.itemgetter(1))
	for x,y in sorted_reports:
		sheet_two.insert_row([x,y],2)
		


def timediff(utc):
	then = datetime.fromtimestamp(utc)
	now  = datetime.now()                         
	duration = now - then                         
	duration_in_s = duration.total_seconds()
	days  = duration.days       
	days  = divmod(duration_in_s, 86400)[0] 
	return days


def submissions_and_comments(subreddit, **kwargs):
    results = []
    results.extend(subreddit.new(**kwargs))
    results.extend(subreddit.comments(**kwargs))
    results.sort(key=lambda post: post.created_utc, reverse=True)
    return results

def user_stats(user):
	posts=0
	reports=0
	place= user.id

	for submission in user.submissions.top('all'):
		if submission.subreddit=='DebateTrade':
			posts+=1

	if str(user.name) in user_reports:
		reports=user_reports[user.name]
	else:
		rports=0

	return (f'User {user} has {posts} posts in the /r/debatetrade server and {reports} reports. Their account was created {int(timediff(user.created_utc))} days ago')

subreddit = reddit.subreddit('waterdebate47')



stream = praw.models.util.stream_generator(lambda **kwargs: submissions_and_comments(subreddit, **kwargs))

for post in stream:
	'''
	Updated stats that is auto-commented with every submission
	'''
	if type(post).__name__ == 'Submission' and post.author is not None:

		user= post.author #instance of redditor class
		
		comment_tree= list(map(lambda c: c.author.name if c.author is not None else 'ha', post.comments))
		if 'Debate__Bot' in comment_tree:
			print(user_stats(user))
			print('Debate Bot has already been in this thread, skip it.')
		else:
			out=(user_stats(user))
			post.reply(f'{out}{bottom_text}')
			print(out)
	
	elif type(post).__name__ == 'Comment' and post.author is not None:

		post.refresh()
		comment_tree=list(map(lambda c: c.author.name if c.author is not None else 'ha', post.replies))
		message= str(post.body).split()
		commented=False


		if 'Debate__Bot' in comment_tree:
			print('Debate Bot has already replied to this comment, skip it')
			commented=True

		if message[0]=='!report' and message[1][0:3]=='/u/':
			real=True

			try:
				z= reddit.redditor(message[1][3:]) #this is the reported user
				placeholder= z.id # Automatically assigns the case-sensitive username of the redditor (maybe a bug)
			except:
				print('Inputted username is not an actual user')
				real=False

			if real:
				age= int(timediff(post.author.created_utc))
				print(f'{post.author} account is {age} days old') 

			if real and z.name=='Debate__Bot':
				if not commented:
					post.reply(f'Nice try.{bottom_text}')
				real=False
				print('User tried to report Bot')
				

			#Slew of code that executes if someone tries to report

			if real and age<90: #checks if person reporting is elligible to report
				print(f'Sorry,{post.author}, your account is under 3 months old.')
				if not commented:
					post.reply(f'Sorry,{post.author}, your account is under 3 months old.{bottom_text}')
				real=False
			elif real and post.author not in list(reporters): # checks if the person reporting has reported before
				report(z.name)
				print(f'User {z.name} has been officially reported. Their number of reports is: {user_reports[z.name]}')
				if not commented:
					post.reply(f'User {z.name} has been officially reported. Their number of reports is: {user_reports[z.name]}{bottom_text}')
				sheet_one.insert_row([str(post.author),str(post.body)],2)
				reporters[post.author]=[z.name] #the commentor now has a value in the dictionary with index 0 being the most recently reported person
				update_sheet()
			elif real and z.name not in reporters[post.author]: # checks to see if the commenter's target was already reported by the commenter
				report(z.name)
				print(f'User {z.name} has been officially reported. Their number of reports is: {user_reports[z.name]}')
				if not commented:
					post.reply(f'User {z.name} has been officially reported. Their number of reports is: {user_reports[z.name]}{bottom_text}')
				sheet_one.insert_row([str(post.author),str(post.body)],2)
				reporters[post.author].append(z.name)
				update_sheet()
			elif real:
				print(f'Sorry, {post.author}, you have already reported {z.name}!')
				if not commented:
					post.reply(f'Sorry, {post.author}, you have already reported {z.name}!{bottom_text}')


		elif message[0]=='!report' and 'www' in message[1]:
			print('Sorry, but I think you copied and pasted from another comment :p. This gives me a hyperlink not a username, please either remove formatting or type out the username manually.')
			if not commented:
				post.reply(f'Sorry, but I think you copied and pasted from another comment :p. This gives me a hyperlink not a username, please either remove formatting or type out the username manually.{bottom_text}')

		elif message[0]=='!stats' and message[1][0:3]=='/u/':
			real=True

			try:
				z= reddit.redditor(message[1][3:])
				placeholder= z.id # Automatically assigns the case-sensitive username of the redditor (maybe a bug)
			except:
				print('Inputted username is not an actual user')
				real=False

			if real:
				var= user_stats(z)
				print(var)
				if not commented:
					post.reply(f'{var}{bottom_text}')



   
