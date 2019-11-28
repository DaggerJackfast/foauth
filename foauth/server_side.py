import secrets
# TODO: usage aouthlib unstead facebook-sdk for usage only one lib
import facebook
import requests
from urllib import parse
from requests_oauthlib import OAuth1Session, OAuth2Session
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


server_flow = Blueprint('server-flow', __name__, url_prefix="/api/server-flow")


def get_google_provider_cfg():
    return requests.get(GOOGLE_DISCOVERY_URL).json()

# TODO: usage one session or service, delete dublicate code
@server_flow.route("/google-login")
def google_login():
    state = "%s" % secrets.token_urlsafe(24)
    session["google_state_param"] = state
    google_provider_cfg = get_google_provider_cfg()
    authorization_endpoint = google_provider_cfg["authorization_endpoint"]
    scope = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile"
    ]

    auth_session = OAuth2Session(
        client_id=GOOGLE_CLIENT_ID,
        scope=scope,
        redirect_uri=request.base_url + "/callback",
    )
    authorization_uri, state = auth_session.authorization_url(
        authorization_endpoint,
        access_type="offline",
        prompt="select_account",
        state=state
    )
    return redirect(authorization_uri)


@server_flow.route("/google-login/callback")
def google_callback():
    state = request.args.get('state')
    session_state = session.pop('google_state_param')
    if state != session_state:
        return "The state parameter is invalid", 400
    code_response = request.url
    google_provider_cfg = get_google_provider_cfg()
    token_endpoint = google_provider_cfg["token_endpoint"]
    scope = [
        "https://www.googleapis.com/auth/userinfo.email",
        "https://www.googleapis.com/auth/userinfo.profile",
        "openid"
    ]
    auth_session = OAuth2Session(
        GOOGLE_CLIENT_ID,
        scope=scope,
        redirect_uri=request.base_url
    )
    auth_session.fetch_token(
        token_url=token_endpoint,
        client_secret=GOOGLE_CLIENT_SECRET,
        authorization_response=code_response
    )
    userinfo_endpoint = google_provider_cfg["userinfo_endpoint"]
    userinfo_response = auth_session.get(userinfo_endpoint)

    if userinfo_response.json().get("email_verified"):
        unique_id = userinfo_response.json()["sub"]
        users_email = userinfo_response.json()["email"]
        picture = userinfo_response.json()["picture"]
        users_name = userinfo_response.json()["given_name"]
    else:
        return "User email not available or not verified by Google.", 400

    user = User(
        id_=unique_id, name=users_name, email=users_email, profile_pic=picture
    )

    if not User.get(unique_id):
        User.create(unique_id, users_name, users_email, picture)

    login_user(user)

    return redirect(url_for("index"))


@server_flow.route('/facebook-login')
def facebook_login():
    state_param = "{state=%s}" % secrets.token_urlsafe(24)
    login_url = "https://www.facebook.com/v5.0/dialog/oauth"
    fields = "email"
    params = parse.urlencode({
        'client_id': FACEBOOK_CLIENT_ID,
        'redirect_uri': f'{request.base_url}/callback',
        'state': state_param,
        'scope': fields
    })
    session['facebook_state_param'] = state_param
    request_uri = f'{login_url}?{params}'
    return redirect(request_uri)


@server_flow.route('/facebook-login/callback')
def facebook_callback():
    code = request.args.get("code")
    state_param = request.args.get("state")
    session_state_param = session.pop("facebook_state_param")
    if state_param != session_state_param:
        return "The state parameter is invalid", 400

    token_url = "https://graph.facebook.com/v5.0/oauth/access_token"
    params = parse.urlencode({
        'client_id': FACEBOOK_CLIENT_ID,
        'redirect_uri': request.base_url,
        'client_secret': FACEBOOK_CLIENT_SECRET,
        'code': code
    })
    request_uri = f'{token_url}?{params}'
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
    params = {
        'oauth_callback': callback_url,
        'oauth_token': token,
    }
    auth_url = f'{authorize_url}?{parse.urlencode(params)}'
    return redirect(auth_url)


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
