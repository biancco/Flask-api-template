import requests

response=requests.post('http://0.0.0.0:5000/prediction',json={"text":"KETI is a specialized production technology research institute established in 1988 to promote Korea's electronics and information communication industry. KETI conducts technology research and development, industry support, international standardization, and technology talent cultivation in the field of information and communication to serve as a central player in implementing and advancing the nation's ICT policies. Its main research areas include artificial intelligence, the Internet of Things (IoT), big data, cloud computing, and more."}).text

print(response)
