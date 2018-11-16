import json
import os
import socket
import re

def downloadCommit(commitURL):
	startOfRepoName = re.search('https://github.com/[^/]+/', commitURL)	# [^/] skips all non '/' characters (skipping repo owner name)
	leftovers = commitURL[startOfRepoName.end():]
	endOfRepoName = leftovers.index('/')
	repoName = leftovers[:endOfRepoName]

	# Sends a ping to Google to see what this computer's public IP address is
	# TODO: Change the Susereum server to use a domain like susereum.com and check that instead
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	myIP = s.getsockname()[0]
	s.close()

	# PARSING INFORMATION
	projectURL = commitURL[:commitURL.index('/commit')]
	projectURL += ".git"

	shaIndex = commitURL.index('commit/') + len('commit/')
	commitSha = commitURL[shaIndex:]

	if(myIP == serverIP):
		#print("I am the server")

		# ADD SERVER CREDENTIALS TO GIT CLONE COMMAND
		f = open("susereumGitHubCredentials", "r")
		contents = f.read()
		contents = json.loads(contents)
		username = contents['username']
		password = contents['password']

		githubIndex = projectURL.index('github.com/')
		rightOfURL = projectURL[githubIndex:]
		leftOfURL = "https://" + username + ":" + password + "@"
		projectURL = leftOfURL + rightOfURL
		#print projectURL

		# DOWNLOADING FILES
		os.system('git clone ' + projectURL)
		os.chdir(repoName)
		os.system('git checkout ' + commitSha)
	else:
		#print("I am the client")
		# DOWNLOADING FILES
		os.system('git clone ' + projectURL)	# Assumes that user's credentials are stored in git
		os.chdir(repoName)
		os.system('git checkout ' + commitSha)

if __name__ == '__main__':
	serverIP = "129.108.7.2"	# TODO: use a domain name for the susereum server like susereum.com so that we don't have to hardcode server IP
	commitURL = "https://github.com/susereum/SampleProject2/commit/1d0349fda2d67abc294fd1476a5b0d8369555f6d"
	downloadCommit(commitURL)
