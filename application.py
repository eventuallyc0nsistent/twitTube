import os
from flask import Flask,render_template,request,redirect,send_from_directory, session,url_for, jsonify, flash
from werkzeug.utils import secure_filename
from config import db_param
import config
import controller
import MySQLdb,md5,sys
from boto.s3.connection import S3Connection
from boto.s3.connection import Location
from boto.s3.key import Key
from boto.s3.bucket import Bucket
from boto.elastictranscoder.layer1 import ElasticTranscoderConnection
from datetime import datetime
from datetime import timedelta
from boto.sns import SNSConnection
from flask_oauth import OAuth

UPLOAD_FOLDER = 'static/videos/'
ALLOWED_EXTENSIONS = set(['webm'])

# S3 connection established here
conn = S3Connection()
sns_conn = SNSConnection()

# OAuth
oauth = OAuth()
twitter = oauth.remote_app('twitter',
    # unless absolute urls are used to make requests, this will be added
    # before all URLs.  This is also true for request_token_url and others.
    base_url='https://api.twitter.com/1/',
    # where flask should look for new request tokens
    request_token_url='https://api.twitter.com/oauth/request_token',
    # where flask should exchange the token with the remote application
    access_token_url='https://api.twitter.com/oauth/access_token',
    # twitter knows two authorizatiom URLs.  /authorize and /authenticate.
    # they mostly work the same, but for sign on /authenticate is
    # expected because this will give the user a slightly different
    # user interface on the twitter side.
    authorize_url='https://api.twitter.com/oauth/authenticate',
    # the consumer keys from the twitter application registry.
    consumer_key='yY26jAcu4t1UyyVpGfDylkwbd',
    consumer_secret='5baSJHTCDf5FXER0dBAvHPnnAhR2ZoSs3DSY3l99p6nE9scWeQ'
)

application = app = Flask(__name__)
app.config.update(db_param)
app.secret_key = db_param['SECRET_KEY']
app.permanent_session_lifetime = timedelta(minutes=10)

@twitter.tokengetter
def get_twitter_token(token=None):
	return session.get('twitter_token')

@app.route('/twitter-login')
def twitter_login():
	if(session.has_key('twitter_token')):
		session['logged_in'] = True
		return redirect('post-new-video')
	else:
		return twitter.authorize(callback=url_for('oauth_authorized',next=request.args.get('next') or request.referrer or None))

@app.route('/oauth-authorized')
@twitter.authorized_handler
def oauth_authorized(resp):

	next_url = request.args.get('next') or url_for('index')

	if resp is None :
		flash(u'You denied request to sign in')
		return redirect(next_url)

	session['twitter_token'] = (resp['oauth_token'], resp['oauth_token_secret'])
	session['twitter_user'] = resp['screen_name']

	session['logged_in'] = True

	#Signup the new user
	signup_obj = controller.loginUser()

	# Check if user already present else signup
	if(controller.loginUser().check_oauth_user(resp['screen_name'])):
		session['twitter_token'] = (controller.loginUser().check_oauth_user(resp['screen_name'])[0][1], controller.loginUser().check_oauth_user(resp['screen_name'])[0][2])
		session['uid'] = controller.loginUser().check_oauth_user(resp['screen_name'])[0][0]
	else :
		last_inserted_id = signup_obj.signup(username=resp['screen_name'], oauth_token=resp['oauth_token'], oauth_token_secret=resp['oauth_token_secret'])

	flash('Hello %s' % resp['screen_name'])
	return redirect(next_url)

@app.route('/')
def index():
	if is_logged_in():
		user_video_obj = controller.videoFetch()
		user_videos = user_video_obj.get_videos(session['uid'])
		return render_template("user_home.html",logged_in=is_logged_in(),user_videos_list=user_videos)
	else:
		return render_template("index.html",logged_in=is_logged_in())

@app.route('/upload-video',methods=['GET','POST'])
def save_video():
	
	if(request.args):
		sender_id = int(request.args['sender'])
		sender_post_id = int(request.args['post-id'])

	# get uid from session and set session for UID
	user_id = session['uid']
	user_bucket_id = str(user_id)+"/"


	if request.method == 'POST':

		video_record_obj = controller.videoRecord()
		count_videos_for_user = video_record_obj.count_videos_for_user(user_id) # get count of vids for a user
		count_videos_for_user = count_videos_for_user[0][0] + 1

		video_bucket_id = user_bucket_id + str(count_videos_for_user)
		post_video_status = video_record_obj.post_video(user_id,video_bucket_id)

		# upload to s3 bucket : twittubeflask
		bucket_name = 'twittubeflask'
		bucket = conn.lookup(bucket_name)
		k = Key(bucket)
		k.key = video_bucket_id
		k.set_contents_from_string(request.data)

		# transcode video in the bucket when contents have been set
		transcode_video(k.key)

		if(request.args):
			post_reply_for_vid = video_record_obj.post_reply_for_vid(user_id,count_videos_for_user,sender_id,sender_post_id)
			print post_reply_for_vid
			send_sns_notification(post_reply_for_vid)

		return "Recorded Video"

	return "upload-video incomplete"


def send_sns_notification(list_of_users):
	arn_num = 'arn:aws:sns:us-east-1:926344641371:'

	for user in list_of_users:
		target_arn = arn_num+user[0]
		message = "You have an update on a video you have subscribed to"
		subject = "You have received 1 notification"
		message_structure = 'html'
		try:
			sns_conn.publish(message=message, subject=subject, target_arn=target_arn, message_structure=message_structure)
		except Exception, e:
			pass

def transcode_video(input_key):
	transcoder = ElasticTranscoderConnection()
	op_pipeline_id ="1395000193222-s45vju"
	preset_id = "1395001226755-9doyhg" # preset ID for the transcoder

	op_input_name = {
						"Key":input_key,
						"FrameRate":"auto",
						"Resolution":"auto",
						"AspectRatio":"auto",
						"Container": "webm"
					}
	op_outputs = [
				  	{
					  "Key": input_key,
					  "FrameRate": "auto",
					  "PresetId": preset_id,
					  "Watermarks": [
										    {
										      "PresetWatermarkId": "BottomRight",
										      "InputKey": "logo.png"
										    }
									  ],
					}
				]
	# op_output_key_prefix = input_key
	transcoder.create_job(pipeline_id=op_pipeline_id, outputs=op_outputs, input_name=op_input_name)

@app.route('/demo')
def demo():
	if is_logged_in():
		user_video_obj = controller.videoFetch()
		user_videos = user_video_obj.get_videos(session['uid'])
		return render_template("user_home.html",logged_in=is_logged_in(),user_videos_list=user_videos)
	else:
		user_video_obj = controller.videoFetch()
		user_videos = user_video_obj.get_videos(0)
		return render_template('demo.html',logged_in=is_logged_in(),user_videos_list=user_videos)

@app.route('/signup',methods=['GET','POST'])
def signup():
	error = None
	form = controller.RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		signup_obj = controller.loginUser()
		last_inserted_id = signup_obj.signup(form.email.data,form.username.data,form.password.data,form.firstname.data,form.lastname.data)

		if (last_inserted_id):
			session['logged_in'] = True
			session['uid']= last_inserted_id

			# create sns subscription for user
			sns_conn.create_topic(form.username.data) 
			arn_num = 'arn:aws:sns:us-east-1:926344641371:'+form.username.data
			protocol = 'email'
			endpoint = form.email.data
			sns_conn.subscribe(arn_num,protocol,endpoint)
			
			return redirect(url_for('login'))
		else:
			error = 'Username / Email already exists !'
			return render_template("signup.html",form=form,error=error)
	else :
		return render_template("signup.html",form=form,error=error)

@app.route('/login',methods=['GET','POST'])
def login():

	error = None
	
	if request.method == 'POST':

		loginUser_obj = controller.loginUser()
		login_status = loginUser_obj.authenticateUser(request.form['username'],request.form['password'])
		# set user ID in session
		if(login_status):
			user_id = login_status[0][0]
			session['logged_in'] = True
			session['uid'] = user_id
			return redirect(url_for('index'))
			
	
		else:
			error = "Invalid username or password"
			return render_template('login.html',error=error)

	elif is_logged_in():
		return redirect(url_for('index'))

	else :
		error = None
		return render_template("login.html",error = error)

@app.route('/logout')
def logout():
	if 'logged_in' in session.keys():
		session.pop('logged_in',None)
		del session['uid']
		logged_in = 0
	else :
		logged_in = 0
	return redirect(url_for('index',logged_in=logged_in))

@app.errorhandler(404)
def page_not_found(e):
	return render_template("404.html"),404

@app.route('/post-new-video')
def post_new_video():
	if is_logged_in():
		return render_template("post-new-video.html",logged_in=is_logged_in())
	else :
		return render_template("login.html")

@app.route('/reply',methods=['GET'])
def reply():

	post_id = int(request.args['post-id'])
	sender_id = int(request.args['sender'])

	if(is_logged_in()):
		user_video_obj = controller.videoFetch()
		get_reply_list = user_video_obj.get_video_replies(post_id,sender_id)
		return render_template("reply.html",logged_in=is_logged_in(),reply_video_list=get_reply_list)
	else :
		return render_template("login.html")

def is_logged_in():
	if session.has_key('logged_in'):
		logged_in = True
	else:
		logged_in = False

	return logged_in


if __name__=='__main__':
	application.run(debug=True)