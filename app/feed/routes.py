from app.feed import bp
from flask import jsonify, request, current_app
from app.feed.fetch_area import main


@bp.route("/try")
def try_out():
    print(current_app.config["GOOGLE_API_KEY"])    
    return jsonify("try_out()")
    
@bp.route("/find_restaurant/", methods=['GET', 'POST'])
def find_restaurant():
    coords = request.args.to_dict()
    x = coords["x"]
    y = coords["y"]
    print("coords:", x, y)
    return 'success', 200

    
@bp.route("/try_fetch", methods=["GET", "POST"])
def try_fetch():
    main(40.6937957, -73.9858845)
    return "success", 200
      
