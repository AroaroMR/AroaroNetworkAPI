import requests

url = 'http://127.0.0.1:8000/networks/'
myobj = {'somekey': 'somevalue'}

x = requests.post(url, data = myobj)

print(x.text)
