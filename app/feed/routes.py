from app.feed import bp
from flask import jsonify, request, current_app
from app.feed.fetch_area import main
from app.feed.Predict import vodoo, ConfigureKey


@bp.route("/try")
def try_out():
    print(current_app.config["GOOGLE_API_KEY"])    
    return jsonify("try_out()")
    
@bp.route("/find_restaurant/", methods=['GET', 'POST'])
def find_restaurant():
    #coords = request.arg.to_dict()
    coords = request.get_json()
    x = coords['x']
    y = coords['y']
    print("coords:", x, y)
    new_csv = main(x,y)
    ConfigureKey(current_app.config["YELP_API_KEY"])
    jayson_file = vodoo(new_csv)
    return jsonify(jayson_file)
    #return "ok",200
    
@bp.route("/FEEDME", methods=["GET", "POST"])
def FEEDME():
    #new_csv = main(40.6937957, -73.9858845)
    new_csv="app/feed/Alpha20191120-070314.csv"
    jayson_file = vodoo(new_csv)
    return jsonify(jayson_file)
      
