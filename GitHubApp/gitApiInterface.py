#!/usr/bin/env python2

"""
GitHub API Interface responsible for how Susereum communicates with GitHub.
"""

import web
import os
import json
import hmac
import hashlib
import requests
from requests_oauthlib import OAuth1
import jwt
import datetime
import calendar
import base64
import toml

class RequestHandler:
	def _analyze_commit_history(self, repo_id, repo_name):
		"""
		Requests the commit history of a project repo and sends each commit to Central
		Server Scripts to run code analysis on it.

		Args:
			repo_id (int): The GitHub ID for the project repository
			repo_name (string): The name of the GitHub repository
		"""
		print("Getting commit history")
		try:
			url = "https://api.github.com/repositories/" + str(repo_id) + "/commits"
			commits = self._git_get(url)	# Retreives the list of commits
			for commit in commits:
				# Parse info
				commit_url = commit['url']

				# Commit URL from GET request comes in the following form:
				# https://api.github.com/repos/<repo_owner>/<repo_name>/commits/<commit_sha>
				# But, with push event we get it as
				# https://github.com/<repo_owner>/<repo_name>/commit/<commit_sha>
				# So we convert it to remove 'api.' and '/repos'
				commit_url = commit_url.replace('api.github.com/repos', 'github.com')
				commit_url = commit_url.replace('commits/', 'commit/')
				print("Commit URL: " + commit_url)
			
				sender_id = commit['committer']['id']
				timestamp = commit['commit']['author']['date']

				# Format timestamp as yyyy-mm-dd-hh-mm
				datetime_object = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
				formatted_ts = datetime_object.strftime('%Y-%m-%d-%H-%M-%S')

				# Call Central Server Script commit handler
				push_command_file = open("push_command", "r")
				push_command_file = push_command_file.read()
				push_command_file.rstrip()	# Remove newlines from command
				command = push_command_file.format(str(sender_id), str(repo_id), repo_name, commit_url, formatted_ts)
				print "Command I'm running: " + command
				os.system(command)
		except:
			print("An exception occured trying to analyze all the past commit history")
	def _handle_measure_change(self, payload):
		"""
		Handles when a proposal has passed and the code measures need to change.
		This function updates the .suse file on the GitHub repo with the new code measures.

		Args:
			payload (dict): The payload from Sawtooth with the new code measures
		"""	
		# Parses suse file into a dict
		updated_suse_file = payload['suse_file']
		str_suse_file = json.dumps(updated_suse_file)
		# Converts to toml string with a license header and encodes it as github requires
		content = self._beautify_content(str_suse_file)
		content_encoded = base64.b64encode(content)
		data = {"message": "New code measures", "commiter": {"name": "susereum", "email": "susereum@gmail.com"}, "content": content_encoded}
		
		# Trys to update the file on the git repo
		repo_id = payload['repo']
		URL = 'https://api.github.com/repositories/' + str(repo_id) + '/contents/.suse'
		result_status_code = self._git_update(URL, str(data))
		if result_status_code == 200:
			print "\nUpdated suse file with new code measures"
		else:
			print "Problem updating suse file with new code measures: " + str(result_status_code)	

	def _beautify_content(self, content):
		"""
		Convert a string json suse file into a toml string.
		Also, prepends a license header to the toml string to display on
		the GitHub repo.

		Args:
			content (string): A JSON encoded suse file string
		"""

		header = """# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

#
# Sawtooth -- Settings Transaction Processor Configuration
#
"""

		dict_convert = json.loads(content)		# Loads json string into dict
		toml_convert = toml.dumps(dict_convert)		# Converts to toml string
		return header + toml_convert	# Prepends header

	def _add_url_to_suse_file(self, payload):
		"""
		Adds the configuration url needed for a client to connect to their project's blockchain
		via the gui, to the .suse file in the GitHub repo.
		
		Args:
			payload (dict): A payload from Central Server Scripts with the configuration URL,
				and repoID
		"""
		# Parse payload
		repo_id = payload['repoID']
		url = payload['url']
		
		# Get current suse file
		suse_file = self._get_suse_file_contents(repo_id)
		parsed_suse_file = toml.loads(suse_file)

		# Add configuration url to suse file and prepare it to send to GitHub
		parsed_suse_file['about']['NewUserLink'] = url
		content = json.dumps(parsed_suse_file)
		content = self._beautify_content(content)		# Converts json to toml with a license header
		content_encoded = base64.b64encode(content)

		# Update the .suse file on GitHub
		URL = 'https://api.github.com/repositories/'+str(repo_id)+'/contents/.suse'	
		data = {"message": "Updating suse file with URL", "committer": {"name": "susereum", "email": "susereum@gmail.com"}, "content": content_encoded}

		result_status_code = self._git_update(URL, str(data))
		if result_status_code == 200:
			print "\nSuse file updated successfully"
		else:
			print "Problem editing Suse file: " + str(result_status_code)

	def _push_event(self, payload):
		"""
		Handles a GitHub Push Webhook event. Sends to Central Server Scripts commit handler script.

		Args:
			payload (dict): A push event payload from GitHub
		"""
		# Parsing useful info
		sender_id = payload['sender']['id']
		repo_id = payload['repository']['id']
		repo_name = payload['repository']['name']
		commit_url = payload['head_commit']['url']
		timestamp = payload['repository']['updated_at']		# At UTC time
		
		# Format timestamp as yyyy-mm-dd-hh-mm
		datetime_object = datetime.datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%SZ')
		formatted_ts = datetime_object.strftime('%Y-%m-%d-%H-%M-%S')
		
		print "Sender ID: " + str(sender_id)
		print "Repo ID: " + str(repo_id)
		print "Repo Name: " + repo_name
		print "Commit URL: " + commit_url
		print "Timestamp: " + formatted_ts

		# Call commit handler Central Server script
		# TODO: Check URL for spaces (if users input a malicious URL)		
		push_command_file = open("push_command", "r")
		push_command_file = push_command_file.read()
		push_command_file.rstrip()	# Remove newlines from command
		command = push_command_file.format(str(sender_id), str(repo_id), repo_name, commit_url, formatted_ts)
		print "Command I'm running: " + command
		os.system(command)

	def _installation_event(self, payload):
		"""
		Handles a GitHub Installation Webhook event. Sends to Central Server Scripts new chain script.
		
		Args:
			payload(dict): An integration installation repositories event payload from GitHub 
		"""
		# Parsing useful info
		repo_id = payload['repositories_added'][0]['id']
		repo_name = payload['repositories_added'][0]['name']
		suse_file = self._create_suse_file(repo_id)		# Creates a .suse file with default measures in the repo
		
		print "Repo ID: " + str(repo_id)
		print "Repo Name: " + repo_name
		#print "Suse File: " + suseFile
		# Send information to server side script that creates the project's blockchain

		# Create a suse file in /tmp so that Central Server Scripts can access
		suse_file = suse_file.replace('"', "'")	# The Bash script requires single quotes, not double quotes
		path = "/tmp/SuseFile" + str(repo_id)	
		f = open(path, "w+")
		f.write(suse_file)
		f.close()
		
		# Call new chain Central Server script
		new_chain_command_file = open("new_chain_command", "r")	# Read command from a file
		new_chain_command = new_chain_command_file.read()
		new_chain_command.rstrip()	# Remove newlines from command
		command = new_chain_command.format(repo_name, str(repo_id), path)
		print("Command run: " + command)
		os.system(command)
		print "Sent information to server script"
		
		self._analyze_commit_history(repo_id, repo_name)	# Get all of the repo's past commits and analyze them
	
	def _install_event_to_ignore(self, payload):
		"""
		When a repo installs a GitHub app, it sends two installation events.
		This function is meant to handle the installation repositories event, which we can just ignore.
		
		Args:
			payload (dict): An installation repositories event payload from GitHub
		"""
		pass

	def _get_suse_file_contents(self, repo_id):
		"""
		Gets the contents of .suse from a repo with Susereum installed

		Args:
			repo_id (int): The unique ID for the repo that the .suse file is gotten from
		"""
		url = 'https://api.github.com/repositories/'+str(repo_id)+'/contents/.suse'
		raw_file_contents = self._git_get(url)
		decoded_contents = base64.b64decode(raw_file_contents['content'])
		return decoded_contents

	def _create_suse_file(self, repo_id):
		"""
		Creates a new .suse file in the base directory of a GitHub repository. The .suse file
		will have the default code measures. If the .suse file already exists, it modifies it.
		
		Args:
			repo_id (int): The unique ID for the repo that the .suse file is added to
		"""
		# First check if Suse file already exists in the repo
		file_found = False
		repos_curr_contents = self._git_get('https://api.github.com/repositories/'+str(repo_id)+'/contents')
		filename = ".suse"
		# TODO: Checking if .suse already exists in file keeps crashing, I'm just going to skip that validation for now
		"""
		if ('message' not in repos_curr_contents or
			(repos_curr_contents['message'] != 'This repository is empty.' and repos_curr_contents['message'] != 'Not Found')):
			try:
				for file in repos_curr_contents:		# Loop through files in repo to see if suse file is there
					if file['name'] == filename:
						file_found = True			# Suse file does already exist
						print "Suse Measures file already exists for this repo. Update it with default params"
						#TODO
						return self._get_suse_file_contents(repo_id)
			except:
				print("An error occured when checking if the suse file already exists")
		if not file_found:
		"""		
		# push Suse file	
		URL = 'https://api.github.com/repositories/'+str(repo_id)+'/contents/'+filename
		commit_msg = "Creating initial Suse file"
		username = 'susereum'
		email = 'susereum@gmail.com'
		content = """

# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.

#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

#
# Sawtooth -- Settings Transaction Processor Configuration
#

[about]
Title = "Code Smell Family Configuration"
NewUserLink="#"

[code_smells.class]
LargeClass=[999,1,]
SmallClass=[1,1,]
GodClass=[5,1,]
InappropriateIntimacy=[2,1,]
[code_smells.method]
LargeMethod=[250,1,]
SmallMethod=[10,1,]
LargeParameterList=[4,1,]
[code_smells.comments]
CommentsToCodeRatioLower=[0.2,0.01,]
CommentsToCodeRatioUpper=[0.1,0.01,]

#vote settings
#proposal_active_days indicates the time that users have to cast their vote
#approval_treshold refers to the value of require votes to approve a proposal
[vote_setting]
proposal_active_days=5
approval_treshold=3
"""
		content_encoded = base64.b64encode(content)
		data = {"message": commit_msg, "committer": {"name": username, "email": email}, "content": content_encoded}
		result_status_code = self._git_put(URL, data)
		if result_status_code == 201:
			print "Suse file created successfully"
			return content
		else:
			print "Problem creating Suse file " + str(result_status_code)
			return ""

	# Github sends a signature in the payload header. Github created that signature by using their secret and hashing the entire payload with sha1
	# We encrypt the payload we received with our secret and sha1 and check if they match
	def _valid_signature(self, raw_sig, raw_payload):
		"""
		Github sends a signature in the payload header. Github created that signature by using their secret
		and hashing the entire payload with sha1. We encrypt the payload we received with our secret and sha1
		and check if they match.

		Args:
			raw_sig (string): Signature from GitHub payload header
			raw_payload (string): The contents of the payload 
		"""	
		global WEBHOOK_SECRET
		their_digest = raw_sig.split("sha1=", 1)[1]
		digest_maker = hmac.new(WEBHOOK_SECRET, raw_payload, hashlib.sha1)
		our_digest = digest_maker.hexdigest()
		return hmac.compare_digest(their_digest, our_digest)

	def _git_get(self, URL):
		"""
		Utility function for sending a GET request

		Args:
			URL (string): The URL to send the GET request to (ex. https://api.github.com/repositories/152342203)
		"""
		headers = {'Authorization': ('Token ' + TOKEN)}		# Adds token to authorize as the Susereum bot
		raw_data = requests.get(URL, headers=headers)
		json_data = json.loads(raw_data.text)
		return json_data

	def _git_put(self, URL, data):
		"""
		Utility function for sending a PUT request

		Args:
			URL (string): The URL to send the PUT request to (ex. https://api.github.com/repositories/155309878/contents/SuseMeasures.suse)
			data (string): The payload you want to put (ex. the contents of the .suse file to override the current contents)
		"""
		_create_installation_token()		# Token periodically expires, so generate new token anytime I will need it
		global TOKEN
		data = json.dumps(data)		# This encodes the data as json, which is necessary bc we have nested json data
		headers = {'Authorization': ('Token ' + TOKEN)}		# Adds token to authorize as the Susereum bot
		raw_data = requests.put(URL, data=data, headers=headers)
		return raw_data.status_code

	def _git_update(self, URL, data):
		"""
		Utility function for updating a file (ex. the .suse file)

		Args:
			URL (string): The URL of the file (ex. https://api.github.com/repositories/155309878/contents/SuseMeasures.suse)
			data (string): The contents you want to overwrite the file with
		"""
		json_data = self._git_get(URL)		# Get the old .suse file to retrieve the old sha
		old_sha = json_data['sha'].encode("ascii")	# It's returned in Unicode, need to encode in Ascii bc the rest of the data is ascii
		data = data.replace("'", '"')	# JSON strings require double quotes instead of single
		data = json.loads(data)
		data['sha'] = old_sha
		return self._git_put(URL, data)

	def POST(self):
		""" Handles POST messages to this web app """
		payload = web.data()
		json_payload = json.loads(payload)

		# Check if it's a Susereum internal message
		if 'sender' in json_payload and json_payload['sender'] == 'ConfigurationURL':
			print("Received ConfigurationURL from Central Server Scripts")
			self._add_url_to_suse_file(json_payload)
			return 'OK'
		if 'sender' in json_payload and json_payload['sender'] == 'Sawtooth':
			self._handle_measure_change(json_payload)
			return 'OK'
		
		# Assume that message is from GitHub
		# Verify POST request from GitHub
		signature = web.ctx.env.get('HTTP_X_HUB_SIGNATURE')
		if(not self._valid_signature(signature, payload)):
			return 'Unauthorized'		

		# Figure out which event happend, call the function to handle it
		event = web.ctx.env.get('HTTP_X_GITHUB_EVENT')
		print '\nReceived ' + event + ' event'
		#print 'PAYLOAD: ' + payload
		# Map events to functions that handle those events
		functionMapping = {
			'push': self._push_event,
			'integration_installation_repositories': self._installation_event,
			'installation_repositories': self._install_event_to_ignore,
		}
		generic_func = functionMapping.get(event)	# Figure out which handler function to use
		generic_func(json_payload)	# Call handler function with json payload
		return 'OK'
	
def _create_listener():
	""" Creates the web.py application """
	url_regex = '/.*'        # Captures requests at this URL
	class_handler = 'RequestHandler'	# Class to handle requests
	# Note: Sends POST requests to RequestHandler.POST(), GET requests to RequestHandler.GET(), etc.) 
	urls = (url_regex, class_handler)
	return web.application(urls, globals())	

def _get_environment_vars():
	"""
	Gets environment variables needed to verify GitHub requests
	and authenticate our app as a Susereum bot
	"""
	global PRIVATE_KEY, WEBHOOK_SECRET, APP_IDENTIFIER
	# Used to verify POST requests from GitHub
	WEBHOOK_SECRET = os.environ['GITHUB_WEBHOOK_SECRET']

	# Used to authenticate our app	
	PRIVATE_KEY = os.environ['GITHUB_PRIVATE_KEY']
	APP_IDENTIFIER = os.environ['GITHUB_APP_IDENTIFIER']

def _create_installation_token():
	"""
	Generates token needed to authenticate Git API commands. You can send GitHub your JWT and installation ID
	and GitHub will return an authentication token.
	"""
	global TOKEN
	print("Generating a new token")
	JWT = _generate_JWT()
	installation_id = "363304"	# This can be found in a integration_installation_repositories payload
	URL = 'https://api.github.com/app/installations/'+installation_id+'/access_tokens'
	headers = {'Accept': 'application/vnd.github.machine-man-preview+json',
				'Authorization': ('Bearer ' + JWT)}
	raw_data = requests.post(URL, headers = headers)
	json_data = json.loads(raw_data.text)
	TOKEN = json_data['token']
	#print TOKEN

def _generate_JWT():
	"""
	Creates a Json Web Token with a current time stamp and expiration time,
	and then uses it to create an authentication token

	Returns:
		The JWT
	"""
	global PRIVATE_KEY, APP_IDENTIFIER 
	current = datetime.datetime.utcnow()
	current_time = calendar.timegm(current.timetuple())
	
	future = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
	expiration_time = calendar.timegm(future.timetuple())
	
	payload = {'iat': current_time, 'exp': expiration_time, 'iss': APP_IDENTIFIER}
	JWT = jwt.encode({'iat': current_time, 'exp': expiration_time, 'iss': APP_IDENTIFIER}, PRIVATE_KEY, algorithm='RS256')
	return JWT
	
if __name__ == '__main__':
	""" Begins the GitHub API Interface """
	_get_environment_vars()
	_create_installation_token()
	app = _create_listener()
	app.run()
