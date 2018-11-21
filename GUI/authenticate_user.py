import os
import json

def authenticate(username, password):
	"""
	Authenticates a GitHub user.

	Args:
		username (string): The GitHub username
		password (string): The GitHub password

	Returns:
		Whether the user credentials are valid or not (true valid, false invalid)
	"""

	command = 'curl -u "' + username + '":"' + password + '" https://api.github.com'
	out = os.popen(command).read()
	out_dict = json.loads(out)
	
	if('message' in out_dict):		# response contains only has message if it's bad credentials
		return False
	else:
		return True

if __name__ == '__main__':
	print("Authenticating user")
	print authenticate("martin-morales", "wrong_password")	
