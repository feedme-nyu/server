# Feed Me Server
This is the server (backend) for the Feed Me application.

## Build Instructions
We are using Docker to manage our production environment. To deploy the server for testing, please make sure you have installed Docker. Here are instructions on how to do so for your specific OS:

* [Installing Docker on Windows](https://docs.docker.com/docker-for-windows/install/)
* [Installing Docker on macOS](https://docs.docker.com/docker-for-mac/install/)
    - It is probably easiest to use homebrew with the command `brew cask install docker`
* [Installing Docker on Linux](https://runnable.com/docker/install-docker-on-linux)

Once you have docker installed, make sure that docker-engine is running with the command: `docker ps &> /dev/null; echo $?`, it should return 0. If it is not running (or on UNIX it does not recognize `docker`) you may need to manually start the Docker process (i.e. `open docker` or `sudo service docker start`)

For building the system, do the following:

### UNIX Systems
```
$ cd /path/to/feedme/server
$ docker build -t feedme .
...
Successfully built <build-number>

$ docker run -d -p 8080:8080 feedme
```

### Windows
This should work if you installed docker engine using the link provided previously as the installation process registers docker to the system PATH.

```
> cd C:/path/to/feedme/server
> docker build --tag feedme .
...
Successfully built <build-number>

> docker run --detach --publish 8080:8080 --name feedme
```

If you follow the above steps, the Feed Me server should be running and accessible from `http://localhost:8080`. You can check this by navigating to [http://localhost:8080/api/test](http://localhost:8080/api/test) and verifying that it prints `running`.

## Backend Architecture and Use of External Services

The Feed Me server is an API that serves the client applications with only a single hook: `/api/FEEDME`. It works using a single GET Request with the following parameters:

* `x`: the user's longitude
* `y`: the user's latitude
* `id`: the user's unique id

Additionally, the API requires an Authorization header with login parameters provided by the Google Firebase API. This protects the API from being used by non-authenticated users and applications.

The API returns a list of twenty restaurants that it has determined the querying user is interested in. The response has the following format:

```json
{
    "status" : "<HTTP_STATUS>",
    "decisions" : [
        {
            "name" : "<STRING>",
            "distance" : "<FLOAT>",
            "address" : "<STRING>",
            "google-place-id": "<STRING>",
            "score": "<FLOAT>",
            "images": [
                "<URL>",
                "<URL>",
                ...
            ]
        },
        ...
    ]
}
```

In case of error, the `decision` key is replaced with an "error" key with a string describing what went wrong (usually an authentication issues).

Feed Me depends on four external services:
* **Google Firebase Firestore**: a NoSQL database which stores information about the user's behavioral trends and caches API data for 24 hours (in order to facilitate repeated searches for the same area, 24 hours is the maximum storage time allowed by our APIs' terms of service).
* **Google Firebase Authentication**: An cross platform authentication service which allows for cross service authentication (i.e. Google Sign-in, Facebook sign-in, etc.). We use this service for authentication as it is quick, secure, cross platform and has built in traffic analytics.
* **Google Places API**: Given that we do not have the resources to catalog restaurants ourselves, we search for restaurants near the user using the Google Places API, the narrow down its results (100 restaurants) to a more reasonable selection (20 restaurants).
* **Yelp API**: while the Yelp API may not have the best selection, it is very good at restaurant categorization and we therefore use it to identify restaurant cuisine types and to aid in the selection process.

## Implementation:
Our server is implemented using Python and Flask. The following files are pertinant in this implementation:

```
/
    app
        feed
            __init__.py
            fetch_area.py
            Predict.py
            routes.py
        routes.py
    cuisine.py
    weights.txt
    fm.py
    Dockerfile
    config.py
```

### Server Architecture
The file `config.py` is used to configure the server on deployment. The file `fm.py` is the entry point for the server. `app/routes.py` and `app/feed/routes.py` define the logical routes for the server.

The `Dockfile` is used to build the docker image to run the server on. We chose to deploy our app to Google Cloud's flexible App Engine due to the "flexibility" of the service to allocate more resources to our service during high volume as well as its integration to the Firebase and Google Places API services. We are using an Ubuntu image due to our experience with that OS as well as the availability of the required packages (we were originally going to use Alpine, but it lacked a precompiled numpy module for Python 3).

### Machine Learning
We have implemented our machine learning in two steps:

_Step 1: Choosing Restaurants_

In this step we utilize a single, binary classification logistic regression to choose 20 restaurants nearby to the user which our algorithm has identified the user has the high probability of going to (i.e. the algorithm is predicting either YES the user would want to go there or NO they would not). This is based on many factors including: price, distance, wait time, user rating, user reviews, and frequency of visits from customers. This model will output 20 restaurants to be fed into Step 2. This is implemented in `app/feed/fetch_area.py` and `app/feed/Predict.py`.

_Step 2: User Preference_

Next we order the twenty restaurants according to how much the user will like it based upon their INDIVIDUAL food preferences as defined by their history and previously defined preferences. We used a basic Graph search to connect users and restaurants to each other by their proximity (attraction) to various standardized food types such as French food, fast food, quick food, Asian food, etc. We feed all twenty restaurants into the graph and order them by their proximity to the user. Then we return that sorted list to the user. The model is defined in `weights.txt` and the algorithm is defined in `cuisine.py`.