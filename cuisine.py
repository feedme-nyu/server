from firebase_admin import credentials, firestore, initialize_app
from hashlib import md5
import requests
import json
from flask import current_app

reference = {}
reverse = {}
initialGraph = []
graph = []
virtuals = []

#yelpkey = current_app.config["YELP_API_KEY"]
yelpkey = None
maxint = float("inf")

with open("weights.txt", "r") as f:
    line = f.readline()[:-1]
    i = 0
    while line != "----------VIRTUALS----------" :
        reference[line] = i
        reverse[i] = line
        i += 1
        line = f.readline()[:-1]
        # print line
    line = f.readline()[:-1]
    while line != "----------START----------" :
        virtuals.append(line)
        line = f.readline()[:-1]
    line = f.readline()[:-1]
    while line :
        initialGraph.append(list(map(float, line.split(","))))
        line = f.readline()[:-1]

graph = initialGraph
cred = credentials.Certificate('key.json')
default_app = initialize_app(cred)
db = firestore.client()
collection = db.collection('restaurants')


def Configure(key) :
    global yelpkey
    yelpkey = key

def dijkstra(graph, src): 
  
    dist = [maxint] * len(graph[src])
    dist[src] = 0
    sptSet = [False] * len(graph[src])

    for cout in range(len(graph[src])): 

        # Pick the minimum distance vertex from  
        # the set of vertices not yet processed.  
        # u is always equal to src in first iteration 
        
        # Initilaize minimum distance for next node 
        min = maxint 
  
        # Search not nearest vertex not in the  
        # shortest path tree 
        for v in range(len(graph[src])): 
            if dist[v] < min and sptSet[v] == False: 
                min = dist[v] 
                min_index = v 
  
        u = min_index 

        # Put the minimum distance vertex in the  
        # shotest path tree 
        sptSet[u] = True

        # Update dist value of the adjacent vertices  
        # of the picked vertex only if the current  
        # distance is greater than new distance and 
        # the vertex in not in the shotest path tree 
        for v in range(len(graph[src])): 
            if graph[u][v] > 0 and sptSet[v] == False and dist[v] > dist[u] + graph[u][v]: 
                dist[v] = dist[u] + graph[u][v]
        
    return dist

def GetClosestNeighbor(graph, row, n) :
    newGraph = []
    for r in graph :
        newGraph.append(r + [0.0])
    newGraph.append(row + [0.0])
    dijs = dijkstra(newGraph, len(graph))
    neighbors = []

    num = len(graph)

    for col in range(len(dijs)) :
        if col == num :
            continue
        elif reverse[col] in virtuals :
            continue
        if len(neighbors) < n :
            if len(neighbors) == 0:
                neighbors.append((reverse[col], dijs[col]))
            else :
                for i in range(len(neighbors)) :
                    if dijs[col] > neighbors[i][1] :
                        neighbors = neighbors[:i] + [(reverse[col], dijs[col])] + neighbors[i:]
                        break
                    else :
                        neighbors = neighbors + [dijs]
                        break
        else :
            for i in range(len(neighbors)) :
                if dijs[col] > neighbors[i][1] :
                    neighbors = neighbors[:i] + [(reverse[col], dijs[col])] + neighbors[i:]
                    neighbors = neighbors[1:]
                    break
                if i + 1 == len(neighbors) :
                    neighbors.append((reverse[col], dijs[col]))
                    neighbors = neighbors[1:]
                    break
    
    return neighbors

def GetCuisineScore(name, address) :
    c = FetchRestaurantWeights(name, address)
    return GetClosestNeighbor(graph, c, 5)

def FetchRestaurantWeights(name, address) :
    if not isinstance(address, list) :
        raise TypeError("Address parameter needs to be a list in format:\n\t[0] => Street Address\n\t[1] => City, State, Country")
    categories = FetchRestaurantCategory(name, address)
    if categories == None :
        return None
    c = []
    for i in categories :
        if len(c) == 0 :
            try :
                c += graph[reference[i]]
            except KeyError :
                pass
        else :
            for r in range(len(c)) :
                try :
                    c[r] = (c[r] + reference[i]) / 2
                except KeyError :
                    pass
    return c
        

def FetchRestaurantCategory(name, address) :
    categories = None
    if len(address) == 0 :
        identifier = md5((name).encode('utf8')).hexdigest()
    else :
        identifier = md5((name + address[0]).encode('utf8')).hexdigest()
    result = collection.document(identifier).get().to_dict()
    if result == None :
        if address[0] == None or address[1] == None:
            r = requests.get("https://api.yelp.com/v3/businesses/search", 
                        params={"term": name, 
                                "limit": 50, "categories": "restaurants" },
                        headers={'Authorization': 'Bearer ' + current_app.config["YELP_API_KEY"]})  
        else :
            r = requests.get("https://api.yelp.com/v3/businesses/search", 
                        params={"term": name,
                                "location": " ".join(address).encode("utf-8"), 
                                "limit": 50, "categories": "restaurants" },
                        headers={'Authorization': 'Bearer ' + current_app.config["YELP_API_KEY"]})
        yelpData = json.loads(r.content)
        if "error" in yelpData :
            return None
        upload = []
        for i in yelpData["businesses"] :
            if i['location']['address1'] == None :
                identifier = md5((i['name']).encode('utf8')).hexdigest()
            else :
                identifier = md5((i['name'] + i['location']['address1']).encode('utf8')).hexdigest()
            temp = {
                "id": identifier,
                "categories": []
            }
            for c in i["categories"] :
                temp["categories"].append(c['alias'])
            if (i["name"] == name) :
                categories = temp["categories"]
            upload.append(temp)
        for i in upload :
            result = collection.document(i["id"]).set(i)
        if categories is None :
            collection.document(identifier).set({"id": identifier, "categories": []})
    elif result["categories"] == [] :
        return None
    else :
        categories = result["categories"]
    return categories
        
def FetchUserWeights (firebase_id) :
    dbinfo = db.collection("user-trends").document(firebase_id).get().to_dict()
    c = []
    for i in dbinfo["history"] :
        if len(c) == 0 :
            c += graph[reference[i]]
        else :
            for r in range(len(c)) :
                c[r] = (c[r] + reference[i]) / 2
    return c

def CuisineRater (user, restaurants) :
    restaurantWeights = []
    userWeights = FetchUserWeights("teddy")
    for r in restaurants :
        w = FetchRestaurantWeights(r["name"], r["address"])
        if w is None :
            restaurantWeights.append([])
            for i in range(len(userWeights)) :
                restaurantWeights[-1].append(i)
        else :
            restaurantWeights.append(w)
    newGraph = []
    for r in graph :
        newGraph.append([])
        for c in r :
            newGraph[-1].append(c)
    for r in restaurantWeights :
        newGraph.append([])
        for c in r :
            newGraph[-1].append(c)
    newGraph.append([])
    for c in userWeights :
        newGraph[-1].append(c)
    newGraphLength = len(newGraph)
    for rI in range(len(graph)) : # for each row of old graph, copy edge from restaurants
        r = newGraph[rI]
        while len(r) != newGraphLength :
            r.append(newGraph[len(r)][rI])
    for rI in range(len(graph), newGraphLength) :
        r = newGraph[rI]
        while len(r) != newGraphLength :
            r.append(0.0)
    
    dijs = dijkstra(newGraph, len(newGraph) - 1) # the last node is the user
    
    dijs = dijs[len(graph) : -1] # don't include distance to user itself
    output = []
    for i in range(len(dijs)) :
        output.append((restaurants[i]["name"], dijs[i]))
    return output

# print FecthUserWeights("teddy")
# r = requests.get("https://api.yelp.com/v3/businesses/search", 
#                         params={"location": "6 Metrotech Center Brooklyn, NY 11201", 
#                                 "limit": 50, "categories": "restaurants" },
#                         headers={'Authorization': 'Bearer ' + yelpkey})

# yelpData = json.loads(r.content)
# restaurants = yelpData["businesses"][:10]
# for i in range(len(restaurants)) :
#     restaurants[i]["address"] = [
#         restaurants[i]["location"]["address1"],
#         restaurants[i]["location"]["address3"]
#     ]

# print(CuisineRater("teddy", restaurants))
