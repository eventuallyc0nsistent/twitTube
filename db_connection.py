import config,MySQLdb,md5,random
from flask import session,url_for

class DB:
	def __init__(self):
		self.connect = False
		try:
			self.cursor=self.openDB(config.db_param['DBHOST'],config.db_param['DBUSER'],config.db_param['DBPASS'],config.db_param['DBNAME'])
		except Exception, e:
			print e

	def openDB(self, host, user, password, db):

			self.connect = MySQLdb.connect(host, user, password, db)
			self.connect.set_character_set('utf8')
			if self.connect.open:
				self.cursor = self.connect.cursor()
				return self.cursor
			else:
				return False

	def loginUser(self,username,password):
		if(self.cursor):
			query="select id,username,firstname,lastname from users where username=%s and password=%s"
			self.cursor.execute(query,[username,password])
			data=self.cursor.fetchall()
			if(data):
				return data
			else:
				return False
		else:
			return False

	def signup_user(self,email,username,password,firstname,lastname,oauth_token,oauth_token_secret):
		if(self.cursor):
			try:
				query='insert into users(email,username,password,firstname,lastname, oauth_token, oauth_token_secret) values ("%s","%s","%s","%s","%s","%s","%s")'%(email,username,password,firstname,lastname,oauth_token,oauth_token_secret)
				self.cursor.execute(query)
				self.connect.commit()
				last_inserted_id = self.cursor.lastrowid
				return last_inserted_id
				
			except Exception, e:
				return False
		else:
			return False

	def post_video(self,user_id,video_bucket_id):
		if(self.cursor):
			query='insert into user_video(userid,videoid) values (%d,"%s")'%(user_id,video_bucket_id)
			self.cursor.execute(query)
			self.connect.commit()
			return True
		else:
			return False


	def count_videos_for_user(self,user_id):
		if(self.cursor):
			query='SELECT COUNT(*) AS count_videos_for_user FROM user_video WHERE userid=%d' %user_id
			self.cursor.execute(query)
			data = self.cursor.fetchall()
			if(data):
				return data
			else :
				return False

	def get_videos(self,user_id):
		if(self.cursor):
			query = "SELECT UV.videoid , UV.timestamp, U.username FROM user_video UV,users U WHERE U.id = UV.userid AND UV.videoid NOT IN (SELECT VP.from_user_vid_id FROM video_post VP) ORDER BY UV.timestamp DESC"
			self.cursor.execute(query)
			data = self.cursor.fetchall()
			
			if(data):
				return data
			else:
				return False

		else:
			return False

	def get_video_replies(self,post_id,sender_id):
		if(self.cursor):
			post_id = str(sender_id)+"/"+str(post_id)
			query = "SELECT from_user_vid_id FROM video_post WHERE to_user_vid_id='%s'" %post_id
			self.cursor.execute(query)
			data = self.cursor.fetchall()

			if(data):
				return data
			else :
				return False
		else:
			return False

	def post_reply_for_vid(self,user_id,user_bucket_id,sender_id,sender_bucked_id):
		if(self.cursor):
			to_user_vid_id = str(sender_id)+"/"+str(sender_bucked_id)
			from_user_vid_id = str(user_id)+"/"+str(user_bucket_id)
			print to_user_vid_id
			print from_user_vid_id
			
			# first insert post into replies
			query = "INSERT INTO video_post(to_user_vid_id,from_user_vid_id) VALUES ('%s','%s')" %(to_user_vid_id,from_user_vid_id)
			self.cursor.execute(query)
			self.connect.commit()

			# now to fetch users to send notifications to
			query_notification = "SELECT U.username FROM user_video UV, users U WHERE UV.user_video_id IN ( SELECT DISTINCT VP.from_user_vid_id FROM video_post VP WHERE VP.to_user_vid_id = '%s' AND VP.from_user_vid_id <>  '%s') AND U.id = UV.userid" %(to_user_vid_id,from_user_vid_id)
			print query_notification
			self.cursor.execute(query_notification)
			data = self.cursor.fetchall()
			return data


	def check_oauth_user(self, username):
		if(self.cursor):
			query = "SELECT id, oauth_token, oauth_token_secret FROM users WHERE username='%s'" %username
			self.cursor.execute(query)
			data = self.cursor.fetchall()
			return data