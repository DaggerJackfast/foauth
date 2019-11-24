import json
import secrets
import facebook
import requests
from oauthlib.oauth2 import WebApplicationClient
from flask import jsonify, request, Blueprint
from flask_login import (
    login_user
)
from flask_cors import cross_origin
from config import GOOGLE_DISCOVERY_URL, GOOGLE_CLIENT_ID
from user import User

client_flow = Blueprint('client-flow', __name__, url_prefix="/api/client-flow")
client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@client_flow.route('/google-login', methods=['POST'])
@cross_origin()
def google_login():
    print('request.data:', request.json)
    client.parse_request_body_response(json.dumps(request.json.get('tokenObj')))
    google_provider_cfg = get_google_provider_cfg()
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    # Create a user in your db with the information provided
    # by Google
    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    # Doesn't exist? Add it to the database.
    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    # Begin user session by logging the user in
    login_user(user)

    return jsonify(user.to_dict())


@client_flow.route('/facebook-login', methods=['POST'])
@cross_origin()
def facebook_login():
    data = request.json
    access_token = data.get('accessToken')
    graph = facebook.GraphAPI(access_token=access_token)
    fields = ",".join([
        'email',
        'name',
        'picture.type(large)',
    ])
    user_info = graph.get_object(
        id="me",
        fields=fields
    )
    email = user_info.get('email')
    name = user_info.get('name')
    user_id = user_info.get('id')
    picture = user_info.get('picture')
    picture_url = picture['data']['url']
    user = User(
        id_=user_id, name=name, email=email, profile_pic=picture_url
    )
    if not User.get(user_id):
        User.create(user_id, name, email, picture_url)
    login_user(user)
    return jsonify(user.to_dict())
