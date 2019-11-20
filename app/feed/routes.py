from app.feed import bp
from flask import jsonify, request

@bp.route("/try")
def try_out():
    return jsonify("try_out()")
