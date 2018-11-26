import os
import sys
sys.path.insert(0, os.path.join(
    os.path.dirname(os.path.dirname(os.path.realpath(__file__))),
    'Sawtooth/families/code-smell'))
from client.code_smell_client import CodeSmellClient
#import client.code_smell_client
import getpass
import datetime
import subprocess
import uuid
import time

def deleteSelfFromCron(proposal_id,proposal_date,prj_path):
	cron_file = 'vote_cron_'+str(uuid.uuid4())
	print('deleting cron.. temp:',cron_file,['./tmp_cron.sh', cron_file])
	p = subprocess.Popen(['./tmp_cron.sh', cron_file])
	time.sleep(2)
	cron_cmd = '* 1 * * * python3 /home/practicum2018/Suserium/Susereum/ServerSideScripts/vote_listener.py '+proposal_id+' '+proposal_date+' '+prj_path
	print(cron_cmd)
	new_cron_name = cron_file+"2"
	new_cron = open(new_cron_name,'w')
	for line in open(cron_file,'r').read().split('\n'):
		if cron_cmd in line:
			continue
		new_cron.write(line+'\n')
	new_cron.close()
	subprocess.Popen(['crontab', new_cron_name])
	time.sleep(2)
	os.remove(cron_file)
	os.remove(new_cron_name)


proposal_id = sys.argv[1]
proposal_date = sys.argv[2]
prj_path = sys.argv[3]


repo_id = prj_path.split('_')[-1].replace('/','')
suse = open(prj_path+"etc/.suse","r").read()
api_line=3
line_num=1
api=1002
approval_treshold=0
proposal_active_days=0
for line in open(prj_path+"etc/.ports","r").read().split('\n'):
	if line_num == api_line:
		api=line
	line_num+=1
for line in suse.split('\n'):
	if 'approval_treshold=' in line:
		approval_treshold = int(line.split('=')[1])
	if 'proposal_active_days=' in line:
		proposal_active_days = int(line.split('=')[1])

#get key
username = getpass.getuser()
home = os.path.expanduser("~")
key_dir = os.path.join(home, ".sawtooth", "keys")
keyfile = '{}/{}.priv'.format(key_dir, username)

client = CodeSmellClient(base_url="http://127.0.0.1:"+str(api), keyfile=keyfile, work_path=prj_path)


#check if enough 'yes' votes to pass proposal
print('pid:',proposal_id,api)
votes = client.check_votes(proposal_id)
yes_votes = votes.count(1)

print('VOTES:',votes, (yes_votes >= approval_treshold))
if yes_votes >= approval_treshold:
	print('pass by vote threshold pass')
	client.update_proposal(proposal_id,1,repo_id)
	deleteSelfFromCron(proposal_id,proposal_date,prj_path)
	sys.exit(0)

#check if time has passed
now = datetime.datetime.today()
deadline = datetime.datetime.strptime(proposal_date,"%Y-%m-%d-%H-%M-%S") + datetime.timedelta(days=proposal_active_days)
print("TIMEs:",now,deadline)
if now > deadline:
	if yes_votes >= int(len(votes)/2):
		client.update_proposal(proposal_id,1,repo_id)
	else:
		client.update_proposal(proposal_id,0,repo_id)
	deleteSelfFromCron(proposal_id,proposal_date,prj_path)

