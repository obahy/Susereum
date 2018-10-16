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

class RequestHandler:

	def pushEvent(self, payload):
		senderID = payload['sender']['id']
		repoID = payload['repository']['id']
		commitURL = payload['head_commit']['url']
		print "Sender ID: " + str(senderID)
		print "Repo ID: " + str(repoID)
		print "Commit URL: " + commitURL
		print "In order to download a specific commit refer to https://stackoverflow.com/questions/3489173/how-to-clone-git-repository-with-specific-revision-changeset"

	def installationEvent(self, payload):
		repoID = payload['repositories_added'][0]['id']
		repoName = payload['repositories_added'][0]['name']
		suseFile = self.createSuseFile(repoID)
		starCount = self.getStarCount(repoID)
		
		print "Repo ID: " + str(repoID)
		print "Repo Name: " + repoName
		#print "Suse File: " + suseFile
		print "Star Count: " + str(starCount)
		# TODO: Send this information to Sawtooth to handle creating new blockchains

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
		rawFileContents = self.gitGET('https://api.github.com/repositories/'+str(repoID)+'/contents/SuseMeasures.suse')
		decodedContents = base64.b64decode(rawFileContents['content'])
		return decodedContents

	def createSuseFile(self, repoID):
		# First check if Suse file already exists in the repo
		fileFound = False
		reposCurrContents = self.gitGET('https://api.github.com/repositories/'+str(repoID)+'/contents')
		filename = "SuseMeasures.suse"
		for file in reposCurrContents:
			if file['name'] == filename:
				fileFound = True
				print "Suse Measures file already exists for this repo. Let's parse it for default params!"
				return self.getSuseFile(repoID)
	
		if not fileFound:
			# push Suse file	
			URL = 'https://api.github.com/repositories/'+str(repoID)+'/contents/'+filename
			commitMsg = "Creating initial Suse file"
			username = 'susereum'
			email = 'susereum@gmail.com'
			content = """title = "Susereum Information"
[about]
NewUserLink = https://www.google.com
[code_smells]
[code_smells.class]
LargeClass = 500
SmallClass = 100
GodClass = 5
InappropriateIntimacy = 2
[code_smells.method]
LargeMethod = 250
SmallMethod = 10
LargeParameterList = 4
[code_smells.comments]
CommentsToCodeRatioUpper = 0.2
CommentsToCodeRatioLower = 0.1
"""
			content = base64.b64encode(content)
			data = {"message": commitMsg, "committer": {"name": username, "email": email}, "content": content}
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
		rawData = requests.get(URL)
		jsonData = json.loads(rawData.text)
		return jsonData

	def gitPUT(self, URL, data):
		global TOKEN
		data = json.dumps(data)		# This encodes the data as json, which is necessary bc we have nested json data
		headers = {'Authorization': ('Token ' + TOKEN)}
		rawData = requests.put(URL, data=data, headers=headers)
		return rawData.status_code

	def POST(self):
		# Verify POST request from GitHub
		signature = web.ctx.env.get('HTTP_X_HUB_SIGNATURE')
		payload = web.data()
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
			'watch': self.starEvent
		}
		genericFunc = functionMapping.get(event)	# Figure out which handler function to use
		genericFunc(json.loads(payload))	# Call handler function with json payload
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
