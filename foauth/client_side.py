import json
import secrets
from urllib import parse
import facebook
import requests
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth1Session
from flask import jsonify, request, Blueprint
from flask_login import (
    login_user
)
from flask_cors import cross_origin
from config import GOOGLE_DISCOVERY_URL, GOOGLE_CLIENT_ID, TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET
from user import User

client_flow = Blueprint('client-flow', __name__, url_prefix="/api/client-flow")
google_client = WebApplicationClient(GOOGLE_CLIENT_ID)


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@client_flow.route('/google-login', methods=['POST'])
@cross_origin()
def google_login():
    print('request.data:', request.json)
    google_client.parse_request_body_response(json.dumps(request.json.get('tokenObj')))
    google_provider_cfg = get_google_provider_cfg()
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = google_client.add_token(userinfo_endpoint)
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


@client_flow.route('/twitter-login', methods=['POST'])
@cross_origin()
def twitter_login():
    request_data = dict(request.args)
    url = 'https://api.twitter.com/oauth/access_token'
    auth_session = OAuth1Session(client_key=TWITTER_CLIENT_ID, client_secret=TWITTER_CLIENT_SECRET)
    access_token_data = auth_session.post(url, request_data)
    parsed_data = parse.parse_qsl(access_token_data.text)
    access_token_body = {key: value for key, value in parsed_data}
    key = access_token_body.get('oauth_token')
    secret = access_token_body.get('oauth_token_secret')
    user_data_session = OAuth1Session(
        client_key=TWITTER_CLIENT_ID, 
        client_secret=TWITTER_CLIENT_SECRET, 
        resource_owner_key=key,
        resource_owner_secret=secret
        )
    url_user = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    params = {'include_email': 'true'}
    user_data = user_data_session.get(url_user, params=params)
    user_info = user_data.json()
    user_name = user_info.get('name')
    user_email = user_info.get('email')
    user_picture = user_info.get('profile_image_url_https')
    user_id = user_info.get('id')
    user_email = user_email+'_twitter'
    user = User(
        id_=user_id, name=user_name, email=user_email, profile_pic=user_picture
    )
    if not User.get(user_id):
        User.create(user_id, user_name, user_email, user_picture)
    login_user(user)
    return jsonify(user.to_dict())


@client_flow.route('/twitter-login/request', methods=['POST'])
@cross_origin()
def twitter_login_request():
    request_token_url = "https://api.twitter.com/oauth/request_token"
    request_session = OAuth1Session(client_key=TWITTER_CLIENT_ID, client_secret=TWITTER_CLIENT_SECRET)
    data = request_session.get(request_token_url)
    parsed_data = parse.parse_qsl(data.text)
    token_body = {key: value for key, value in parsed_data}
    return jsonify(token_body)
