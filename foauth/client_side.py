import json
import secrets
import facebook
import requests
from flask import jsonify, request, Blueprint

client_flow = Blueprint('client-flow', __name__, url_prefix="/api/client-flow")


@client_flow.route('/google-login')
def google_login():
    print('request.data:', request.json())
    return jsonify(request.json())


@client_flow.route('/facebook-login')
def facebook_login():
    print('request.data', request.json())
    return jsonify(request.json())
