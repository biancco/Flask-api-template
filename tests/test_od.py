import requests
import json


# -------------------------------------------------
# Input: Image + Json
# Output: Json
# -------------------------------------------------
data = {'filename':"test2.jpg", 'req_task':"object detection"}
filename="test2.jpg"
files = [
    ('image', (filename, open(filename, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data), 'application/json')),
]
response=requests.post(
    'http://0.0.0.0:5000/object_detection',
    files=files
).json()
print(response)

data = {'filename':"test3.jpg", 'req_task':"object detection"}
filename="test3.jpg"
files = [
    ('image', (filename, open(filename, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data), 'application/json')),
]
response=requests.post(
    'http://0.0.0.0:5000/object_detection',
    files=files
).json()
print(response)