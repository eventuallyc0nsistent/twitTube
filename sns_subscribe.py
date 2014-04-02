from boto.sns import SNSConnection

#create connection	
conn  = SNSConnection()
topic_name = 'test-topic'

#create new SNS topic
# conn.create_topic('test-topic')

# ARN Number of topic
arn_num = 'arn:aws:sns:us-east-1:926344641371:'+topic_name

# get attr for the ARN topic
# topic_attr = conn.get_topic_attributes(arn_num)


#subscribe to a topic
protocol = 'email'
endpoint = 'kiranrkoduru@gmail.com'
#conn.subscribe(arn_num,protocol,endpoint)

#publish to a topic

message = "This is a test message. <br> -Kiran"
subject = "Test SNS subscription"
message_structure = 'html'
conn.publish(message=message, subject=subject, target_arn=arn_num, message_structure=message_structure)