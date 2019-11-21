import pandas as pd
import sklearn
import pickle
import json
import numpy as np
from cuisine import CuisineRater, Configure
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

yelpkey = None

def ConfigureKey(key) :
	global yelpkey
	Configure(key)


def vodoo(new_csv, uid):
	print("Predict.py -> vodoo()")
	fd = open('app/feed/Logistic.sav','rb') 
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
		np.append(results, subsample)
		
	jayson = results.to_json(orient="index")

	restaurants = json.loads(jayson)
	interface = []
	decisions = []

	print(len(restaurants))

	for r in restaurants:
		addr = restaurants[r]["address"].split(",")
		interface.append({
			"name": restaurants[r]["name"],
			"address": [
				addr[0], 
				",".join(addr[1:])
			],
			"place_id": restaurants[r]["place_id"]
		})
		decisions.append({
			"name": restaurants[r]["name"],
			"distance": restaurants[r]["distance"],
			"address": [addr[0], ",".join(addr[1:])],
			"rating_n": restaurants[r]["rating_n"],
			"rating": restaurants[r]["rating"],
			"place_id": restaurants[r]["place_id"],
			"price": restaurants[r]["price_level"],
			"photo": restaurants[r]["photo"],
			"score": 0
		})

	print(len(decisions))

	print("Starting Level 2")
	level2 = CuisineRater(uid, interface) # Level 2 ML

	for d in level2 :
		for d1 in decisions :
			if d1["place_id"] == d[0] :
				d1[score] = d[1]

	return {"status" : 200, "decisions": decisions}
'''
if __name__=="__main__":
	new_csv = "Alpha20191120-070314 (copy).csv"
	vodoo(new_csv)
	
'''

