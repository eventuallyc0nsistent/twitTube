import os

# # local
db_param = dict (
					DBHOST = 'localhost',
					DBNAME = 'twitTube', 
					DBUSER = 'root',
					DBPASS = 'root',
					SECRET_KEY = os.urandom(24),
					DEBUG = True
				) 