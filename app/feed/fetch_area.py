import requests
import json
import csv
import time
import geopy.distance
import populartimes
import time
from app.feed import bp

class PlaceData(object):
	"""docstring for PlaceData"""
	def __init__(self, name, rating_n, opening_hours, distance, price_level,rating,frequency, popular, time_spent, place_id):
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
	    print("fetch_area() -> GooglePlaces()")
	    print(key)
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
		time.sleep(3)
		
		"""
		while "next_page_token" in results:
			params["pagetoken"] = results["next_page_token"]
			data = requests.get(endpoint_url, params = params) #JSON request
			results = json.loads(data.content) #load the data from Json
			places.extend(results['results'])
			time.sleep(3)
		"""
			
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
	top = []
	for place in pdata:
		value = place.popular[day]['data'][index]
		place_id = place.place_id
		dic = (place_id,value)
		top.append(dic)
	results = sorted(top,reverse=True,key=lambda popularity:popularity[1])[0:rank]
	print(results)
	final_result = []
	for i in results:
		print(i)
		final_result.append(i[0])
	return final_result

def write(locations): #write the csv
	timestr = time.strftime("%Y%m%d-%H%M%S")
	goal = 0
	cusine = 0
	fieldnames = ['name','rating_n', 'opening_hours','distance','price_level','rating','frequency','time_spent','Went?']
	write_file = "Alpha"+timestr+".csv"
	with open('Alpha.csv', "w") as csvfile:
		writer = csv.DictWriter(csvfile,fieldnames=fieldnames)
		rank = 9
		for day in range(5): #five days
			for index in range(12,23):
				#top = ranking(locations,rank,day,index)
				#print(top)
				for place in locations:
					for time_spent in place.time_spent:
						# if(place.place_id in top):
						# 	goal = 1
						# else:
						# 	goal = 0
						goal = place.popular[day]['data'][index]
						writer.writerow({'name':place.name,'rating_n':place.rating_n, 'opening_hours': place.opening_hours,'distance':place.distance,'price_level':place.price_level,'rating':place.rating,'frequency':place.frequency,'time_spent':time_spent,'Went?':goal})
						print(place.name)
	print("Done Writing")
				
def main(x,y):
    print("fetch_area() -> main(x, y)")
    print("x", x)
    print("y", y)
    
    api_key = bp.config["GOOGLE_API_KEY"]
    
	locations = []
	coords = str(x)+','+str(y)
	
	Search=GooglePlaces(api_key)
	
	places = Search.searchL(coords,"restaurant")
	fields = ['name', 'user_ratings_total', 'opening_hours', 'price_level', 'rating']
	for place in places:
		print(place['place_id'])
		details=None
		#details = Search.Pdetails(place['place_id'], fields)
		try:
			price_level = place['price_level']
			print(price_level)
		except KeyError:
			price_level = 2
		try:
			details = populartimes.get_id(key,place['place_id'])
			#print(detail)
		except:
			print("Failed")
		if(details is not None):
			print(details)
			try:
				name = details['name']
			except KeyError:
				name = ""
			try:
				location = details['coordinates']
				print(location)
				coord1=(40.6937957,-73.9858845)
				coord2=(location['lat'],location['lng'])
				distance = geopy.distance.vincenty(coord1, coord2).m
			except KeyError:
				distance = 210 #average of my research files
			try:
				rating_n = details['rating_n']
			except KeyError:
				rating_n = 333

			try:
				cool = details['opening_hours']
				if(cool):
					opening_hours = 1
				else:
					opening_hours = 0
			except KeyError:
				opening_hours = 0
			try:
				rating = details['rating']
			except KeyError:
				rating = 2.3
			try:
				popular = details['populartimes']
			except KeyError:
				popular = [{'name': 'Monday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 34, 56, 66, 58, 39, 24, 21, 29, 37, 33, 20, 0, 0]}, {'name': 'Tuesday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 47, 81, 86, 59, 32, 26, 33, 43, 43, 33, 20, 0, 0]}, {'name': 'Wednesday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 36, 68, 85, 74, 52, 43, 48, 52, 46, 32, 17, 0, 0]}, {'name': 'Thursday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 43, 82, 100, 84, 61, 52, 47, 41, 40, 38, 29, 0, 0]}, {'name': 'Friday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 38, 75, 98, 88, 61, 47, 55, 65, 60, 42, 21, 0, 0]}, {'name': 'Saturday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 20, 32, 41, 44, 40, 32, 27, 30, 35, 32, 18, 0, 0]}, {'name': 'Sunday', 'data': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 11, 22, 33, 37, 37, 36, 34, 36, 41, 33, 14, 0, 0]}]
			try:
				time_spent = details['time_spent']
			except KeyError:
				time_spent = [15,15]
			frequency=0
			pdata = PlaceData(name, rating_n, opening_hours, distance, price_level,rating,frequency, popular, time_spent,place['place_id'])
			locations.append(pdata)
	#now sort
	#get top 7 rest
	write(locations)

"""
if __name__=="__main__":
	x = 40.6937957
	y = -73.9858845
	main(x,y)
"""

