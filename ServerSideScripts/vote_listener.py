from os.path import dirname, join, abspath
sys.path.insert(0, abspath(join(dirname(__file__), '../Sawtooth/families/code_smell/client')))
import code_smell_client
import sys
import getpass
import datetime
import subprocess
import uuid
import os

def deleteSelfFromCron(proposal_id,proposal_date,prj_path):
	cron_file = 'vote_cron_'+str(uuid.uuid4())
	p = subprocess.Popen(['crontab', '-l', '>', cron_file])
	cron_cmd = '* */1 * * * python3 vote_listener.py '+proposal_id+' '+proposal_date+' '+prj_path
	new_cron_name = cron_file+"2"
	new_cron = open(new_cron_name,'w')
	for line in open(cron_file,'r').read().split('\n'):
		if cron_cmd in line:
			continue
		new_cron.write(line+'\n')
	new_cron.close()
	subprocess.Popen(['crontab', new_cron_name])
	os.remove(cron_file)
	os.remove(new_cron_name)


proposal_id = sys.argv[1]
proposal_date = sys.argv[2]
prj_path = sys.argv[3]


repo_id = prj_path.split('_')[-1].replace('/','')
suse = open(prj_path+"etc/.suse","r").read()
api_line=3
line=1
api=1002
approval_treshold=0
proposal_active_days=0
for line in suse.split('\n'):
	if line == api_line:
		api=line
	if line.contains('approval_treshold='):
		approval_treshold = int(line.split('=')[1])
	if line.contains('proposal_active_days='):
		proposal_active_days = int(line.split('=')[1])
	line+=1

#get key
username = getpass.getuser()
home = os.path.expanduser("~")
key_dir = os.path.join(home, ".sawtooth", "keys")
keyfile = '{}/{}.priv'.format(key_dir, username)

client = codeSmellClient(base_url="http://127.0.0.1:{}".format(api), keyfile=keyfile, work_path=prj_path)


#check if enough 'yes' votes to pass proposal
votes = client.check_vote(propsoal_id)
yes_votes = votes.count('1')
if yes_votes >= approval_treshold:
	client.update_proposal(proposal_id,1,repo_id)
	deleteSelfFromCron(proposal_id,proposal_date,prj_path)
	return

#check if time has passed
now = datetime.datetime.today()
deadline = datetime.datetime.strptime(parse_date,"%Y-%m-%d-%H-%M-%S") + datetime.datetime.timedelta(days=proposal_active_days)
if now > deadline:
	if yes_votes >= int(len(votes)/2):
		client.update_proposal(proposal_id,1,repo_id)
	else:
		client.update_proposal(proposal_id,0,repo_id)
	deleteSelfFromCron(proposal_id,proposal_date,prj_path)

