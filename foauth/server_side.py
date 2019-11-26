# OAuth 2 client setup
import json
import secrets
import facebook
import requests
from urllib import parse
#TODO: usage only one library for oauth
from oauthlib.oauth2 import WebApplicationClient
from requests_oauthlib import OAuth1Session
from flask import redirect, url_for, Blueprint, request, jsonify, session
from config import GOOGLE_CLIENT_ID, GOOGLE_DISCOVERY_URL, GOOGLE_CLIENT_SECRET, \
    FACEBOOK_CLIENT_ID, FACEBOOK_CLIENT_SECRET, TWITTER_CLIENT_ID, TWITTER_CLIENT_SECRET
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from user import User


client = WebApplicationClient(GOOGLE_CLIENT_ID)

server_flow = Blueprint('server-flow', __name__, url_prefix="/api/server-flow")


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()


@server_flow.route("/google-login")
def google_login():
    # Find out what URL to hit for Google login
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]

    # Use library to construct the request for Google login and provide
    # scopes that let you retrieve user's profile from Google
    request_uri = client.prepare_request_uri(
        authorization_endpoint,
        redirect_uri=request.base_url + "/callback",
        scope=["openid", "email", "profile"],
    )
    return redirect(request_uri)


@server_flow.route("/google-login/callback")
def google_callback():
    # Get authorization code Google sent back to you
    code = request.args.get("code")

    # things on behalf of a user
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]

    # Prepare and send a request to get tokens! Yay tokens!
    token_url, headers, body = client.prepare_token_request(
        token_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url,
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET),
    )

    # Parse the tokens!
    client.parse_request_body_response(json.dumps(token_response.json()))

    # Now that you have tokens (yay) let's find and hit the URL
    # from Google that gives you the user's profile information,
    # including their Google profile image and email
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)

    # The user authenticated with Google, authorized your
    # app, and now you've verified their email through Google!
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

    # Send user back to homepage
    return redirect(url_for("index"))


@server_flow.route('/facebook-login')
def facebook_login():
    # TODO: save state_param to database
    state_param = "{state=%s}" % secrets.token_urlsafe(24)
    login_url = "https://www.facebook.com/v5.0/dialog/oauth"
    fields = "email"
    params = "?client_id={app_id}&redirect_uri={redirect_uri}&state={state_param}&scope={scope}".format(
        app_id=FACEBOOK_CLIENT_ID,
        redirect_uri="{}/callback".format(request.base_url),
        state_param=state_param,
        scope=fields
    )
    request_uri = login_url + params
    return redirect(request_uri)


@server_flow.route('/facebook-login/callback')
def facebook_callback():
    code = request.args.get("code")
    token_url = "https://graph.facebook.com/v5.0/oauth/access_token"
    params = "?client_id={app_id}&redirect_uri={redirect_uri}&client_secret={app_secret}&code={code}".format(
        app_id=FACEBOOK_CLIENT_ID,
        redirect_uri=request.base_url,
        app_secret=FACEBOOK_CLIENT_SECRET,
        code=code
    )
    request_uri = token_url + params
    response = requests.get(request_uri)
    data = response.json()
    access_token = data.get('access_token')
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
    return redirect(url_for("index"))


@server_flow.route('/twitter-login')
def twitter_login():
    request_token_url = "https://api.twitter.com/oauth/request_token"
    request_session = OAuth1Session(client_key=TWITTER_CLIENT_ID, client_secret=TWITTER_CLIENT_SECRET)
    callback_url = '{}/callback'.format(request.base_url)
    params = {'oauth_callback': callback_url}
    data = request_session.get(request_token_url, params=params)
    parsed_data = parse.parse_qsl(data.text)
    token_body = {key: value for key, value in parsed_data}
    token = token_body['oauth_token']
    authorize_url = 'https://api.twitter.com/oauth/authorize'
    # TODO: usage urllib.parse.urlencode
    return redirect('{url}?oauth_callback={callback_url}&oauth_token={oauth_token}'.format(
        url=authorize_url,
        callback_url=callback_url,
        oauth_token=token
        ))


@server_flow.route('/twitter-login/callback')
def twitter_login_callback():
    if 'oauth_verifier' not in request.args:
        return "Not exists verifier.", 400
    url = 'https://api.twitter.com/oauth/access_token'
    auth_session = OAuth1Session(client_key=TWITTER_CLIENT_ID, client_secret=TWITTER_CLIENT_SECRET)
    request_data = dict(request.args)
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
    params = {'include_email': 'true', 'skip_status': 'true'}
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
