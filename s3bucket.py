from boto.s3.connection import S3Connection
from boto.s3.connection import Location
from boto.s3.key import Key
from boto.s3.bucket import Bucket
import config

# S3 connection established here
conn = S3Connection()

# get locations to create Bucket
print "----------------------------"
print "Locations to create bucket:"
print "----------------------------"
print '\n'.join(i for i in dir(Location) if i[0].isupper())
print '\n'

# create a bucket in the Northeast location named ='twittube'
print "--------------------------------------"
print "Creating bucket in selected region"
print "--------------------------------------"
#conn.create_bucket('twittubeflask')
print " Bucket created ! ! ! "

bucket = conn.lookup('twittubeflask')
print bucket
k = Key(bucket)
k.key = '7/7'

print "--------------------------------------"
print "Generate URL for key"
print "--------------------------------------"
print k.key+":"
print k.generate_url(3000,method='GET')
print '\n'

print "--------------------------------------"
print "Store and retrive local file"
print "--------------------------------------"
# k.key = 'demo'

print "--------------------------------------"
print "List keys of bucket"
print "--------------------------------------"
bucket_list = bucket.list()
for x in bucket_list:
	print x
