import requests

# URL
url = 'http://localhost:5000/api/find_restaurant/'

payload = {
	'x':40.6937957,
	'y':-73.9858845
}

r = requests.post(url,json=payload)

print(r.json())
