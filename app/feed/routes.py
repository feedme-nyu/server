from app.feed import bp
from flask import jsonify, request, current_app
from app.feed.fetch_area import main
from app.feed.Predict import vodoo, ConfigureKey
import google.auth.transport.requests
import google.oauth2.id_token
import json

# For authorization
HTTP_REQUEST = google.auth.transport.requests.Request()

@bp.route("/try")
def try_out():
    return jsonify("running")

# This is for debugging  
# @bp.route("/find_restaurant/", methods=['GET', 'POST'])
# def find_restaurant():
#     print("routes.py -> find_restaurant()")
#     #coords = request.arg.to_dict() #?x=100&y=200
#     coords = request.get_json()
#     x = coords['x']
#     y = coords['y']
#     user_id = coords['user_id']
#     print("coords:", x, y)
#     new_csv = main(x,y,user_id)
#     ConfigureKey(current_app.config["YELP_API_KEY"])
#     jayson_file = vodoo(new_csv)
#     return jsonify(jayson_file)
#     #return "ok",200

# Main (and only) route
@bp.route("/FEEDME", methods=["GET","POST"])
def FEEDME():
    # Authentication BEGIN
    # From THIS tutorial: https://cloud.google.com/appengine/docs/standard/python/authenticating-users-firebase-appengine
    """
    try : 
        id_token = request.headers["Authorization"].split(' ').pop()
    except KeyError :
        return 'Unauthorized', 401
    claims = google.oauth2.id_token.verify_firebase_token(
        id_token, HTTP_REQUEST)
    if not claims:
        return 'Unauthorized', 401
    # Authentication END
    """
    
    arguments = request.args.to_dict()
    
    x = arguments['x']
    y = arguments['y']
    user_id = arguments['uid']
    
    new_csv = main(x,y,user_id)
    ConfigureKey(current_app.config["YELP_API_KEY"])
    jayson_file = vodoo(new_csv, user_id)
    print("DONE")
    return jsonify(jayson_file)
      
@bp.errorhandler(500)
def server_error(e):
    # Log the error and stacktrace.
    print(e)
    return 'An internal error occurred.', 500
