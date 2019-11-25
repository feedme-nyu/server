import pandas as pd
import sklearn
import pickle
import json
import numpy as np
from cuisine import CuisineRater, Configure
from flask import current_app
import requests
import base64
# from flask import current_app
'''
Final Return
Json:{
	name
	address
	distance
	photoURL
	Need to edit CSV
}
'''

def image(photo,key):
	endpoint_url = "https://maps.googleapis.com/maps/api/place/photo?"
	payload = {
		'maxwidth': 300,
		'photoreference': photo,
		'key': key
	}
	r = requests.get(endpoint_url,params=payload)
	return str(base64.b64encode(r.content))

yelpkey = None

def ConfigureKey(key) :
	global yelpkey
	Configure(key)


def vodoo(new_csv, uid):
	print("Predict.py -> vodoo()")
	fd = open('Logistic.sav','rb') 
	model = pickle.load(fd, encoding = 'unicode_escape')
	
	raw_data = pd.read_csv(new_csv, header = 0)
	
	x_val = raw_data[raw_data.columns[2:9]]
	
	#  array of 0 and 1s 
	prediction = model.predict(x_val)
   
	raw_data.insert(0, "Chosen", prediction, True)
   
	results = raw_data[raw_data["Chosen"] == 1.0]
  
	unused_data = raw_data[raw_data["Chosen"] == 0.0]
	
	results.drop_duplicates(subset = "place_id", keep='last', inplace=True)

	if(results.shape[0] < 20):
		difference = 20 - results.shape[0]
		subsample = unused_data.sample(n = difference)
		results = pd.concat([results, subsample], axis=0)
		# np.concatenate(results, subsample)
		
		
	jayson = results.to_json(orient="index")

	restaurants = json.loads(jayson)
	interface = []
	decisions = []
	
	for r in restaurants:
		images = ""
		addr = restaurants[r]["address"].split(",")
		interface.append({
			"name": restaurants[r]["name"],
			"address": [
				addr[0], 
				",".join(addr[1:])
			],
			"place_id": restaurants[r]["place_id"]
		})
		
		if restaurants[r]["photo"] == "null" or restaurants[r]["photo"] == None:
			images = ""
		else :
			images = image(restaurants[r]["photo"][2:-2], current_app.config["GOOGLE_API_KEY"])
		
		decisions.append({
			"name": restaurants[r]["name"],
			"distance": restaurants[r]["distance"],
			"address": [addr[0], ",".join(addr[1:])],
			"rating_n": restaurants[r]["rating_n"],
			"rating": restaurants[r]["rating"],
			"place_id": restaurants[r]["place_id"],
			"price": restaurants[r]["price_level"],
			"photo": images[2:-1],
			"score": 0,
			"categories": [],
			"time": restaurants[r]["time_spent"],
		})
		
	level2 = CuisineRater(uid, interface) # Level 2 ML

	for d in level2 :
		for d1 in decisions :
			if d1["place_id"] == d[0] :
				d1["score"] = d[1]
				d1["categories"] = d[2]

	return {"status" : 200, "decisions": decisions}
'''
if __name__=="__main__":
	new_csv = "Alpha20191120-070314 (copy).csv"
	vodoo(new_csv)
	
'''

