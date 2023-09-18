import requests
import json


# -------------------------------------------------
# Input: Json
# Output: text
# -------------------------------------------------
response=requests.post(
    'http://0.0.0.0:5000/prediction',
    json={"text":"KETI is a specialized production technology research institute established in 1988 to promote Korea's electronics and information communication industry. KETI conducts technology research and development, industry support, international standardization, and technology talent cultivation in the field of information and communication to serve as a central player in implementing and advancing the nation's ICT policies. Its main research areas include artificial intelligence, the Internet of Things (IoT), big data, cloud computing, and more."}
).text
print(response)


# -------------------------------------------------
# Input: Image + Json
# Output: Json
# -------------------------------------------------
data = {'filename':"test.jpg", 'req_task':"object detection"}
filename="test.jpg"
files = [
    ('image', (filename, open(filename, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data), 'application/json')),
]
response=requests.post(
    'http://0.0.0.0:5000/object_detection',
    files=files
).json()
print(response)


# -------------------------------------------------
# Input: Image + Json
# Output: Image
# -------------------------------------------------
from PIL import Image
import io
data = {'filename':"test.jpg", 'req_task':"depth estimation"}
filename="test.jpg"
files = [
    ('image', (filename, open(filename, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data), 'application/json')),
]
response=requests.post(
    'http://0.0.0.0:5000/depth_estimation',
    files=files
)
image = Image.open(io.BytesIO(response.content))
image.save("result_depth_estimation.png")


# -------------------------------------------------
# Input: Image + Json
# Output: Json(Base64(Image bytes))
# -------------------------------------------------
import base64
data = {'filename':"test.jpg", 'req_task':"depth estimation json"}
filename="test.jpg"
files = [
    ('image', (filename, open(filename, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data), 'application/json')),
]
response=requests.post(
    'http://0.0.0.0:5000/depth_estimation_json',
    files=files
)
data = response.json()["data"]
decoded_image = base64.decodebytes(data.encode("utf-8"))
image = Image.open(io.BytesIO(decoded_image))
image.save("result_depth_estimation_json.png")


# -------------------------------------------------
# Input: Json
# Output: Audio
# -------------------------------------------------
response=requests.post(
    'http://0.0.0.0:5000/text2speech',
    json={"text":"In a new interview, former President Donald Trump refused or avoided answering many specific questions about his conduct on Jan. 6"}
)
open("test.wav", "wb").write(response.content)


# -------------------------------------------------
# Input: Audio + Json
# Output: Json
# -------------------------------------------------
data = {'filename':"test.wav", 'req_task':"speech to text"}
filename="test.wav"
files = [
    ('audio', (filename, open(filename, 'rb'), 'application/octet')),
    ('data', ('data', json.dumps(data), 'application/json')),
]
response=requests.post(
    'http://0.0.0.0:5000/speech2text',
    files=files
).json()
print(response)