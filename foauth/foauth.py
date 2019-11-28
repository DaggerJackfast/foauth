from oauthlib.oauth1 import Client
from oauthlib.oauth2 import Client


class Provider(object):
    def get_login_page(self):
        NotImplementedError

    def authorize(self):
        NotImplementedError


@dataclass
class OAuth1Urls(object):
    access_token_url: str
    authorize_url: str
    user_info_url: str


facebook_urls = OAuth1Urls(
    access_token_url='https://graph.facebook.com/v5.0/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    user_info_url='https://graph.facebook.com/me',
)


class Facebook(Provider):
    def __init__(self, client_key: str, client_secret: str):
        self.__key = client_key,
        self.__secret = client_secret
        self.__client = Client(client_id=self.__key)
        self._urls = facebook_urls

    def get_login_page(self):
        pass

    def authorize(self):
        pass
