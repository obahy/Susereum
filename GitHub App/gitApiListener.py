# from github import Github tried to use PyGithub library but it was out of date
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
from subprocess import call

class RequestHandler:

	def beautifyContent(self, content):
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

		dictConvert = json.loads(content)
		tomlConvert = toml.dumps(dictConvert)
		return header + tomlConvert

	def addURLToSuseFile(self, payload):
		repoID = payload['repoID']
		url = payload['url']
		suseFile = self.getSuseFileContents(repoID)
		parsedSuseFile = toml.loads(suseFile)
		parsedSuseFile['about']['NewUserLink'] = url
		content = json.dumps(parsedSuseFile)
		
		content = self.beautifyContent(content)		# Converts json to toml with a license header

		URL = 'https://api.github.com/repositories/'+str(repoID)+'/contents/.suse'	
		contentEncoded = base64.b64encode(content)
		data = {"message": "Updating suse file with URL", "committer": {"name": "susereum", "email": "susereum@gmail.com"}, "content": contentEncoded}

		resultStatusCode = self.gitUPDATE(URL, str(data))
		if resultStatusCode == 200:
			print "\nSuse file updated successfully"
		else:
			print "Problem editing Suse file"

	def pushEvent(self, payload):
		senderID = payload['sender']['id']
		repoID = payload['repository']['id']
		repoName = payload['repository']['name']
		commitURL = payload['head_commit']['url']
		print "Sender ID: " + str(senderID)
		print "Repo ID: " + str(repoID)
		print "Repo Name: " + repoName
		print "Commit URL: " + commitURL

		# TODO: Check URL for spaces (if users input a malicious URL)		
		pushCommandFile = open("push_command", "r")
		pushCommandFile = pushCommandFile.read()
		pushCommandFile.rstrip()	# Remove newlines from command
		command = pushCommandFile.format(str(senderID), str(repoID), repoName, commitURL)
		print "Command I'm running: " + command
		os.system(command)

	def installationEvent(self, payload):
		repoID = payload['repositories_added'][0]['id']
		repoName = payload['repositories_added'][0]['name']
		suseFile = self.createSuseFile(repoID)
		starCount = self.getStarCount(repoID)
		
		print "Repo ID: " + str(repoID)
		print "Repo Name: " + repoName
		#print "Suse File: " + suseFile
		#print "Star Count: " + str(starCount)
		# Send information to server side script that creates the project's blockchain
		suseFile = suseFile.replace('"', "'")	# The Bash script requires single quotes, not double quotes

		newChainCommandFile = open("new_chain_command", "r")	# Read command from a file
		newChainCommand = newChainCommandFile.read()
		newChainCommand.rstrip()	# Remove newlines from command
	
		path = "/tmp/SuseFile" + str(repoID)	
		f = open(path, "w+")
		f.write(suseFile)
		f.close()
		command = newChainCommand.format(repoName, str(repoID), path)
		os.system(command)
		print "Sent information to server script"
	
	def installEventToIgnore(self, payload):
		x = 3

	def starEvent(self, payload):
		repoID = payload['repository']['id']
		starCount = self.getStarCount(repoID)
		print "Star Count: " + str(starCount)
		# TODO: Send this star count to Sawtooth so they can use it for calculating Suse

	def getStarCount(self, repoID):
		rawFileContents = self.gitGET('https://api.github.com/repositories/'+str(repoID)+'/stargazers')
		starCount = len(rawFileContents)
		return starCount

	def getSuseFile(self, repoID):
		rawFileContents = self.gitGET('https://api.github.com/repositories/'+str(repoID)+'/contents/.suse')
		return rawFileContents

	def getSuseFileContents(self, repoID):
		rawFileContents = self.getSuseFile(repoID)
		decodedContents = base64.b64decode(rawFileContents['content'])
		return decodedContents

	def createSuseFile(self, repoID):
		# First check if Suse file already exists in the repo
		fileFound = False
		reposCurrContents = self.gitGET('https://api.github.com/repositories/'+str(repoID)+'/contents')
		filename = ".suse"
		
		# Check if .suse already exists
		if ('message' not in reposCurrContents or (reposCurrContents['message'] != 'This repository is empty.' and reposCurrContents['message'] != 'Not Found')):	# Make sure there are files in the repo, if not suse file can't exist
			print reposCurrContents
			print reposCurrContents['message']
			for file in reposCurrContents:		# Loop through files in repo to see if suse file is there
				if file['name'] == filename:
					fileFound = True			# Suse file does already exist
					print "Suse Measures file already exists for this repo. Let's parse it for default params!"
				return self.getSuseFileContents(repoID)
		if not fileFound:
			# push Suse file	
			URL = 'https://api.github.com/repositories/'+str(repoID)+'/contents/'+filename
			commitMsg = "Creating initial Suse file"
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
LargeClass=500
SmallClass=100
GodClass=5
InappropriateIntimacy=2
[code_smells.method]
LargeMethod=250
SmallMethod=10
LargeParameterList=4
[code_smells.comments]
CommentsToCodeRationLower=0.2
CommentsToCodeRationUpper=0.1

#vote settings
#proposal_active_days indicates the time that users have to cast their vote
#approval_treshold refers to the value of require votes to approve a proposal
[vote_setting]
proposal_active_days=5
approval_treshold=3
"""
			contentEncoded = base64.b64encode(content)
			data = {"message": commitMsg, "committer": {"name": username, "email": email}, "content": contentEncoded}
			resultStatusCode = self.gitPUT(URL, data)
			if resultStatusCode == 201:
				print "Suse file created successfully"
				return content
			else:
				print "Problem creating Suse file"
				return ""

	# Github sends a signature in the payload header. Github created that signature by using their secret and hashing the entire payload with sha1
	# We encrypt the payload we received with our secret and sha1 and check if they match
	def validSignature(self, rawSig, rawPayload):
		global WEBHOOK_SECRET
		theirDigest = rawSig.split("sha1=", 1)[1]
		digestMaker = hmac.new(WEBHOOK_SECRET, rawPayload, hashlib.sha1)
		ourDigest = digestMaker.hexdigest()
		return hmac.compare_digest(theirDigest, ourDigest)

	def gitGET(self, URL):
		headers = {'Authorization': ('Token ' + TOKEN)}
		rawData = requests.get(URL, headers=headers)
		jsonData = json.loads(rawData.text)
		return jsonData

	def gitPUT(self, URL, data):
		global TOKEN
		data = json.dumps(data)		# This encodes the data as json, which is necessary bc we have nested json data
		headers = {'Authorization': ('Token ' + TOKEN)}
		rawData = requests.put(URL, data=data, headers=headers)
		return rawData.status_code

	def gitUPDATE(self, URL, data):
		jsonData = self.gitGET(URL)		# Get the old .suse file to retrieve the old sha
		oldSha = jsonData['sha'].encode("ascii")	# It's returned in Unicode, need to encode in Ascii bc the rest of the data is ascii
		data = data.replace("'", '"')	# JSON strings require double quotes instead of single
		data = json.loads(data)
		data['sha'] = oldSha
		return self.gitPUT(URL, data)

	def POST(self):
		payload = web.data()
		jsonPayload = json.loads(payload)

		# Check if POST is from Sawtooth
		if 'sender' in jsonPayload and jsonPayload['sender'] == 'Sawtooth':		# Check if sender is in headers
			self.addURLToSuseFile(jsonPayload)
			return 'OK'

		# Verify POST request from GitHub
		signature = web.ctx.env.get('HTTP_X_HUB_SIGNATURE')
		if(not self.validSignature(signature, payload)):
			return 'Unauthorized'		

		# Figure out which event happend, call the function to handle it
		event = web.ctx.env.get('HTTP_X_GITHUB_EVENT')
		print '\nReceived ' + event + ' event'
		#print 'PAYLOAD: ' + payload
		# Map events to functions that handle those events
		functionMapping = {
			'push': self.pushEvent,
			'integration_installation_repositories': self.installationEvent,
			'installation_repositories': self.installEventToIgnore,
			'watch': self.starEvent
		}
		genericFunc = functionMapping.get(event)	# Figure out which handler function to use
		genericFunc(jsonPayload)	# Call handler function with json payload
		return 'OK'
	
def createListener():
	urlRegex = '/.*'        # Captures requests at this URL
	classHandler = 'RequestHandler'
	urls = (urlRegex, classHandler)
	return web.application(urls, globals())	

def getEnvironmentVars():
	global PRIVATE_KEY, WEBHOOK_SECRET, APP_IDENTIFIER
	# Used to verify POST requests from GitHub
	WEBHOOK_SECRET = os.environ['GITHUB_WEBHOOK_SECRET']

	# Used to authenticate our app	
	PRIVATE_KEY = os.environ['GITHUB_PRIVATE_KEY']
	APP_IDENTIFIER = os.environ['GITHUB_APP_IDENTIFIER']

# Generates token needed to authenticate Git API commands
def createInstallationToken(JWT):
	global TOKEN
	installationID = "363304"	# This can be found in a integration_installation_repositories payload
	URL = 'https://api.github.com/app/installations/'+installationID+'/access_tokens'
	headers = {'Accept': 'application/vnd.github.machine-man-preview+json',
				'Authorization': ('Bearer ' + JWT)}
	rawData = requests.post(URL, headers = headers)
	jsonData = json.loads(rawData.text)
	TOKEN = jsonData['token']
	#print TOKEN

# Creates a Json Web Token with a current time stamp and expiration time, which is used to create an installation token
def generateJWT():
	global PRIVATE_KEY, APP_IDENTIFIER 
	current = datetime.datetime.utcnow()
	currentTime = calendar.timegm(current.timetuple())
	future = datetime.datetime.utcnow() + datetime.timedelta(minutes=10)
	expirationTime = calendar.timegm(future.timetuple())
	payload = {'iat': currentTime, 'exp': expirationTime, 'iss': APP_IDENTIFIER}
	JWT = jwt.encode({'iat': currentTime, 'exp': expirationTime, 'iss': APP_IDENTIFIER}, PRIVATE_KEY, algorithm='RS256')
	createInstallationToken(JWT)
	
if __name__ == '__main__':
	getEnvironmentVars()
	generateJWT()
	app = createListener()
	app.run()
