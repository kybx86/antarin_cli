import boto3
import sys
from fabric.api import *
import time
from fabric.exceptions import NetworkError

def launch_instance(ami,keyname,instance_type,security_group):
	client = boto3.resource('ec2')

	hosts = []
	ids = []
	
	print ('Launching instance..')
	instances = client.create_instances(
		ImageId=ami,
		MinCount=1,
    	MaxCount=1,
        KeyName=keyname,
        InstanceType=instance_type,
        SecurityGroups=security_group)
	
	instance = None
	while 1:
		sys.stdout.flush()
		dns_name = instances[0].public_dns_name
		if dns_name:
			instance = instances[0]
			hosts.append(instance.public_dns_name)
			ids.append(instance.instance_id)
			break
		time.sleep(5.0)
		instances[0].load()
	print ('\nInstance launched.Public DNS:', instance.public_dns_name)

	print ('Connecting to instance.')
	while instance.state['Name'] != 'running':
		print ('.')
		time.sleep(5)
		instance.load()
	print ('Instance in Running state')
	print ('Initializing instance')
	c = boto3.client('ec2')
	while True:
		response = c.describe_instance_status(InstanceIds=ids)
		print ('.')
		#print response['InstanceStatuses'][0]['InstanceStatus']['Details'][0]['Status'],response['InstanceStatuses'][0]['SystemStatus']['Details'][0]['Status']
		if response['InstanceStatuses'][0]['InstanceStatus']['Details'][0]['Status'] == 'passed' and response['InstanceStatuses'][0]['SystemStatus']['Details'][0]['Status']=='passed':
			break
		time.sleep(15)

	time.sleep(15)
	return hosts,ids

def setup_instance(hosts,key_path): 
	env.hosts = hosts
	env.user = 'ubuntu'
	env.key_filename=key_path

def execute_instance():
	run('uname -a')
	# run('sudo apt-get update')
	# run('sudo apt-get install python-pip')
	# run('sudo pip install awscli')
	# run('aws configure')
	# run('mkdir test')
	# run('cd test')
	# run('sudo apt-get install python-numpy')
	# run('sudo apt-get install python-matplotlib')
	# run('aws s3 cp s3://antarin-test/media/userfiles/ruchikas300@gmail.com/new/instance1/algo-files/linear_reg.py linear_reg.py')
	# run('aws s3 cp s3://antarin-test/media/userfiles/ruchikas300@gmail.com/new/instance1/data-files/nasdaq00.txt nasdaq00.txt')
	# run('aws s3 cp s3://antarin-test/media/userfiles/ruchikas300@gmail.com/new/instance1/data-files/nasdaq01.txt nasdaq01.txt')
	# run('python linear_reg.py')

def stop_instance():
	print ("Stopping instance:" + str(ids[0]))
	time.sleep(20.0)
	client.instances.filter(InstanceIds=ids).stop()
