from app.feed import bp
from flask import jsonify, request, current_app

@bp.route("/try")
def try_out():
    return jsonify("try_out()")
    
@bp.route("/find_restaurant/", methods=['GET', 'POST'])
def find_restaurant():
    coords = request.args.to_dict()
    x = coords["x"]
    y = coords["y"]
    print("coords:", x, y)
    return 'success', 200
    
def perform_something_with_api_key(params):
     request.get(url, apikey)   
