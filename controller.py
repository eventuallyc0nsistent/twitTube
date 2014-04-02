import db_connection
import json
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from datetime import datetime
from wtforms import Form, BooleanField, TextField, PasswordField, validators

class loginUser:

	def __init__(self):
		self.db_obj = db_connection.DB()

	def authenticateUser(self,username,password):

		login_status=self.db_obj.loginUser(username,password)
		return login_status

	def signup(self,email=None,username=None,password=None,firstname=None,lastname=None, oauth_token_secret=None, oauth_token=None):

		insert_user_status=self.db_obj.signup_user(email,username,password,firstname,lastname,oauth_token, oauth_token_secret)
		return insert_user_status

	def check_oauth_user(self,username):
		return self.db_obj.check_oauth_user(username)


class videoRecord:

	def __init__(self):
		self.db_obj = db_connection.DB()

	def post_video(self,user_id,video_bucket_id):

		post_video_status=self.db_obj.post_video(user_id,video_bucket_id)
		return post_video_status

	def count_videos_for_user(self,user_id):

		count_videos_for_user=self.db_obj.count_videos_for_user(user_id)
		return count_videos_for_user

	def post_reply_for_vid(self,user_id,user_bucket_id,sender_id,sender_bucked_id):
		
		list_of_users_to_notify = self.db_obj.post_reply_for_vid(user_id,user_bucket_id,sender_id,sender_bucked_id)
		return list_of_users_to_notify

class videoFetch:
	def __init__(self):
		self.db_obj = db_connection.DB()
		self.s3_connection = S3Connection()

	def get_videos(self,user_id):
		
		user_video_lists = []

		try :

			fetched_videos = self.db_obj.get_videos(user_id)

			if(fetched_videos):
				for row in fetched_videos:
					sender_id = row[0].split('/')[0]
					post_id = row[0].split('/')[1]
					video_bucket_id = row[0]
					video_time = self.pretty_date(row[1])
					video_url = self.get_video_url(video_bucket_id)
					username = row[2]
					user_video_lists.append({'post_id':post_id,'video_time':video_time,'video_url' : video_url,'username':username,'sender_id':sender_id})

		except Exception, e:
			pass


			
		return user_video_lists
	
	def get_video_url(self,bucket_id):
		bucket_name = 'twittubeflask-transcoded-media'
		bucket = self.s3_connection.get_bucket(bucket_name)
		s3key = Key(bucket)
		s3key.key = bucket_id
		return s3key.generate_url(3000,method='GET')


	def get_video_replies(self,post_id,sender_id):

		reply_video_list = []

		original_sender_list = []
		original_sender_url = str(sender_id)+'/'+str(post_id)
		original_sender_list = {'video_url':self.get_video_url(original_sender_url)}
		
		reply_video_list.append(original_sender_list)
		reply_video_list_db = self.db_obj.get_video_replies(post_id,sender_id)
		if(reply_video_list_db):
			for row in reply_video_list_db:
				fetch_url = self.get_video_url(row[0])
				reply_video_list.append({'video_url':fetch_url})
		return reply_video_list

	def pretty_date(self,time=False):
		now = datetime.now()
		if type(time) is int:
			diff = now - datetime.fromtimestamp(time)
		elif isinstance(time,datetime):
			diff = now - time
		elif not time:
			diff = now - now
		second_diff = diff.seconds
		day_diff = diff.days
		
		if day_diff < 0:
			return ''



		if day_diff == 0:
			if second_diff < 10:
				return "just now"
			if second_diff < 60:
			    return str(second_diff) + " seconds ago"
			if second_diff < 120:
			    return  "a minute ago"
			if second_diff < 3600:
			    return str( second_diff / 60 ) + " minutes ago"
			if second_diff < 7200:
			    return "an hour ago"
			if second_diff < 86400:
				return str( second_diff / 3600 ) + " hours ago"

		if day_diff == 1:
			return "Yesterday"
		if day_diff < 7:
			return str(day_diff) + " days ago"
		if day_diff < 31:
			return str(day_diff/7) + " weeks ago"
		if day_diff < 365:
			return str(day_diff/30) + " months ago"

		return str(day_diff/365) + " years ago"

class RegistrationForm(Form):
	firstname = TextField('Firstname',[validators.Required(),validators.Length(min=4)])
	lastname = TextField('Lastname',[validators.Required(),validators.Length(min=4)])
	username = TextField('Username',[validators.Required(),validators.Length(min=4,max=25)])
	email = TextField('Email',[validators.Required(),validators.Email()])
	password = PasswordField('Password',[validators.Required(),validators.EqualTo('confirm',message = 'Passwords must match')])
	confirm = PasswordField('Confirm Password')