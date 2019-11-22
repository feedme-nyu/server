import requests
import json
import csv
import time
import geopy.distance
from populartimes import get_id
import time
from flask import current_app
from firebase_admin import credentials, firestore, initialize_app
from google.api_core.exceptions import NotFound
from cuisine import GetCollection
from hashlib import md5
import threading

class PlaceData(object):
	"""docstring for PlaceData"""
	def __init__(self, name, rating_n, opening_hours, distance, price_level,rating,frequency, popular, time_spent, place_id, photo,address):
		super(PlaceData, self).__init__()
		self.name = name
		self.rating_n=rating_n
		self.opening_hours=opening_hours
		self.distance=distance
		self.price_level=price_level
		self.rating=rating
		self.frequency=frequency
		self.popular=popular
		self.time_spent=time_spent
		self.place_id=place_id
		self.photo=photo
		self.address=address
		
	def printd(self):
		print("===================PLACE===================")
		print("Name:", self.name)
		print("rating_n:", self.rating_n) # Number (unbounded)
		print("opening_hours:", self.opening_hours)
		print("distance", self.distance) # Number (unbounded)
		print("price_level", self.price_level) # Number (1-4)
		print("rating", self.rating) # Number (0-5)
		print("frequency", self.frequency) # Number (N/A)
		print("popular", self.popular) # Popularity
		print("time_spent", self.time_spent) # Timespent
		# Category History (our database) (use Yelp to get restaurant category)
		# Popularity
		print("==================REWIEVS==================")
 

class GooglePlaces():
	#one call does -124
	def __init__(self,key):
		# print("fetch_area() -> GooglePlaces()")
		self.apiKey = key
		
	def searchL(self, location, types):
		endpoint_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
		params = {'location': location,'types': types, 'radius' : "500" ,'key': self.apiKey}
		places = [] #storing the places
		data = requests.get(endpoint_url, params = params) #JSON request
		results = json.loads(data.content) #load the data from Json
		#print(results) #debug
		#Google returns max of 60.Need more for ML
		places.extend(results['results'])
		
		while "next_page_token" in results:
			params["pagetoken"] = results["next_page_token"]
			data = requests.get(endpoint_url, params = params) #JSON request
			results = json.loads(data.content) #load the data from Json
			places.extend(results['results'])
			
		return places

	def Pdetails(self,place_id, fields):
		endpoint_url = "https://maps.googleapis.com/maps/api/place/details/json?"
		params = {
		'place_id':place_id,
		#'fields':','.join(fields),
		#'fields':'name',
		'key':self.apiKey
		}
		data = requests.get(endpoint_url, params = params) #JSON request
		
		if(data.status_code==404):
			return None
		details = json.loads(data.content) #load the data from Json
		print(details)
		
		return details

def ranking(pdata,rank,day,index): #getting the rnaking
	# print("fetch_area -> ranking()")
	top = []
	for place in pdata:
		value = place.popular[day]['data'][index]
		place_id = place.place_id
		dic = (place_id,value)
		top.append(dic)
	results = sorted(top,reverse=True,key=lambda popularity:popularity[1])[0:rank]
	#print(results)
	final_result = []
	for i in results:
		#print(i)
		final_result.append(i[0])
	return final_result

def write(locations): #write the csv
	# print("fetch_area -> write()")
	timestr = time.strftime("%Y%m%d-%H%M%S")
	goal = 0
	cusine = 0
	field = ['place_id','name','rating_n', 'opening_hours','distance','price_level','rating','frequency','time_spent','Went?','photo','address']
	write_file = "Alpha"+timestr+".csv"
	with open(write_file, "w") as csvfile:
		writer = csv.DictWriter(csvfile,fieldnames=field)
		writer.writeheader()
		rank = 9
		for day in range(5): #five days
			for index in range(12,23):
				top = ranking(locations,rank,day,index)
				#print(top)
				for place in locations:
					for time_spent in place.time_spent:
						if(place.place_id in top):
							goal = 1
						else:
							goal = 0
						#goal = place.popular[day]['data'][index]
						writer.writerow({'place_id':place.place_id,'name':place.name,'rating_n':place.rating_n,
						 'opening_hours':place.opening_hours,'distance':place.distance,
						'price_level':place.price_level,'rating':place.rating,
						'frequency':place.frequency,'time_spent':time_spent,
						'Went?':goal,'photo':place.photo,'address':place.address})
	print("Done Writing")
	return write_file

def CacheTimes (toBeCached):
	print("Thread Started")
	for c in toBeCached :
		try :
			GetCollection().document(c["id"]).update(c)
		except NotFound:
			GetCollection().document(c["id"]).set(c)
	print("Thread Done")

def main(x,y,user_id):
	# print("fetch_area() -> main(x, y)")
	# print("x", x)
	# print("y", y)
	newCache = []

	api_key = current_app.config["GOOGLE_API_KEY"]
	
	locations = []
	coords = str(x)+','+str(y)
	
	Search=GooglePlaces(api_key)
	
	places = Search.searchL(coords,"restaurant")
	fields = ['name', 'user_ratings_total', 'opening_hours', 'price_level', 'rating']
	print(len(places))
	for place in places:
		# time.sleep(0.1)
		details=None
		try :
			name = place['name'].encode('utf-8')
		except :
			name = ""
		try:
			photo_reference = []
			for p in place['photos'] :
				photo_reference.append(p['photo_reference'])
		except KeyError:
			photo_reference = "null"
		try:
			place_id = place['place_id']
		except KeyError:
			place_id = "null"
		try:
			price_level = place['price_level']
		except KeyError:
			price_level = 2
		try: 
			location = place['geometry']['location']
			coord1=(x,y)
			coord2=(location['lat'], location['lng'])
			distance = geopy.distance.vincenty(coord1, coord2).m
		except KeyError:
			distance = 210 # average of my research files
		try:
			rating_n = place['user_ratings_total']
		except KeyError:
			rating_n = 333
		try:
			rating = place['rating']
		except KeyError:
			rating = 2.3
		try:
			cool = place['opening_hours']['open_now']
			if(cool):
				opening_hours = 1
			else:
				opening_hours = 0
		except KeyError :
			opening_hours = 0
		try:
			address = place['formatted_address'].encode('utf-8')
		except KeyError:
			try:
				address = place['vicinity'].encode('utf-8')
			except KeyError :
				address = "Earth"
		try :
			if address == "Earth" :
				identifier = md5((name.lower()).encode('utf8')).hexdigest()
			else :
				identifier = md5((name.lower() + address.split(',')[0].lower()).encode('utf8')).hexdigest()
			restaurantCache = GetCollection().document(identifier).get().to_dict()
			frequency = restaurantCache["frequency"]
		except :
			frequency = 0 #need to update freq
		try:
			# First try to get cached results:
			details = restaurantCache["popularity"]
			popular = details['populartimes']
			time_spent = details['time_spent'].encode('utf-8')
		except:
			# Otherwise, get it from the other source
			details = get_id(api_key, place['place_id'])
			if(details is not None):	
				try:
					popular = details['populartimes']
				except KeyError:
					popular = [{'name': 'Monday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 34, 56, 66, 58, 39, 24, 21, 29, 37, 33, 20, 0, 0]}, {'name': 'Tuesday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 47, 81, 86, 59, 32, 26, 33, 43, 43, 33, 20, 0, 0]}, {'name': 'Wednesday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 68, 85, 74, 52, 43, 48, 52, 46, 32, 17, 0, 0]}, {'name': 'Thursday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 43, 82, 100, 84, 61, 52, 47, 41, 40, 38, 29, 0, 0]}, {'name': 'Friday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 38, 75, 98, 88, 61, 47, 55, 65, 60, 42, 21, 0, 0]}, {'name': 'Saturday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 32, 41, 44, 40, 32, 27, 30, 35, 32, 18, 0, 0]}, {'name': 'Sunday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 22, 33, 37, 37, 36, 34, 36, 41, 33, 14, 0, 0]}]
				try:
					time_spent = details['time_spent'].encode('utf-8')
				except KeyError:
					time_spent = [15,15]
				newCache.append({"id": identifier, "popularity": {"populartimes": popular, "time_spent": time_spent}})
			else :
				popular = [{'name': 'Monday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 34, 56, 66, 58, 39, 24, 21, 29, 37, 33, 20, 0, 0]}, {'name': 'Tuesday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 47, 81, 86, 59, 32, 26, 33, 43, 43, 33, 20, 0, 0]}, {'name': 'Wednesday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 68, 85, 74, 52, 43, 48, 52, 46, 32, 17, 0, 0]}, {'name': 'Thursday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 43, 82, 100, 84, 61, 52, 47, 41, 40, 38, 29, 0, 0]}, {'name': 'Friday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 38, 75, 98, 88, 61, 47, 55, 65, 60, 42, 21, 0, 0]}, {'name': 'Saturday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 32, 41, 44, 40, 32, 27, 30, 35, 32, 18, 0, 0]}, {'name': 'Sunday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 22, 33, 37, 37, 36, 34, 36, 41, 33, 14, 0, 0]}]
				time_spent = [15,15]

		pdata = PlaceData(name, rating_n, opening_hours, distance, price_level,rating,frequency, popular, time_spent, place_id, photo_reference,address)
		locations.append(pdata)
	
	threading.Thread(target=CacheTimes, args=(newCache,)).start()
	return write(locations)
	

'''
if __name__=="__main__":
	x = 40.6937957
	y = -73.9858845
	main(x,y)

'''
