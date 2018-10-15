import web
import os
import json
import hmac
import hashlib

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
		print "Repo ID: " + str(repoID)
		print "Repo Name: " + repoName
		# TODO: Send this information to Christian somehow

	# Github sends a signature in the payload header. Github created that signature by using their secret and hashing the entire payload with sha1
	# We encrypt the payload we received with our secret and sha1 and check if they match
	def validSignature(self, rawSig, rawPayload):
		global WEBHOOK_SECRET
		theirDigest = rawSig.split("sha1=", 1)[1]
		digestMaker = hmac.new(WEBHOOK_SECRET, rawPayload, hashlib.sha1)
		ourDigest = digestMaker.hexdigest()
		return hmac.compare_digest(theirDigest, ourDigest)

	def POST(self):
		# Verify POST request from GitHub
		signature = web.ctx.env.get('HTTP_X_HUB_SIGNATURE')
		payload = web.data()
		if(not self.validSignature(signature, payload)):
			return 'Unauthorized'		

		# Figure out which event happend, call the function to handle it
		event = web.ctx.env.get('HTTP_X_GITHUB_EVENT')
		print 'Received ' + event + ' event'
		#print 'PAYLOAD: ' + payload
		# Map events to functions that handle those events
		functionMapping = {
			'push': self.pushEvent,
			'integration_installation_repositories': self.installationEvent
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
	
	# Used to instantiate an Octokit API client (bot that can change repos, files, issues, etc.)
	PRIVATE_KEY = os.environ['GITHUB_PRIVATE_KEY']
	APP_IDENTIFIER = os.environ['GITHUB_APP_IDENTIFIER']

if __name__ == '__main__':
	getEnvironmentVars() 
	app = createListener()
	app.run()
