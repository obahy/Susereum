import requests
import json

data = json.dumps({'sender': 'Sawtooth', 'name': 'Martin', 'password': 'MyPassword', 'age': 23})
r = requests.post('http://localhost:3000', data=data)
print("Payload: " + r.text)
