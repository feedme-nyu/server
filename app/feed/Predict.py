import pandas as pd
import sklearn
import pickle
import json
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


def vodoo(new_csv):
    print("Predict.py -> vodoo()")
    fd = open('app/feed/Logistic.sav0','rb') 
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
	    
    jayson = raw_data.to_json(orient="index")

    restaurants = json.loads(jayson)
    interface = []

    for r in restaurants :
	    addr = restaurants[r]["address"].split(",")
	    interface.append({
		    "name": restaurants[r]["name"],
		    "address": [addr[0], ",".join(addr[1:])]
	    })
	    
    print("doing cousineRater")
    print(CuisineRater("teddy", interface))	
    #print(raw_data.to_json(orient="index"))
    return jayson


if __name__=="__main__":
	new_csv = "Alpha20191120-070314 (copy).csv"
	vodoo(new_csv)
	

