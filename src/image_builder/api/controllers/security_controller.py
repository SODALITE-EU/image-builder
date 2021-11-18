from image_builder.api.settings import Settings
from image_builder.api.log import get_logger
from base64 import b64encode
import requests

logger = get_logger(__name__)

# use connection pool for OAuth tokeninfo
adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
session = requests.Session()
for protocol in Settings.connection_protocols:
    session.mount(protocol, adapter)

def check_api_key(apikey, required_scopes=None):
    if not Settings.apiKey or apikey != Settings.apiKey:
        return None

    return {'scope': ['apiKey']}


def token_info(access_token) -> dict:
    request = {'token': access_token}
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    token_info_url = Settings.oidc_introspection_endpoint_uri
    if not token_info_url:
        logger.warning("OAuth 2.0 Introspection endpoint not configured.")
        return None
    # TODO add multiple client support
    basic_auth_string = '{0}:{1}'.format(
        Settings.oidc_client_id,
        Settings.oidc_client_secret
    )
    basic_auth_bytes = bytearray(basic_auth_string, 'utf-8')
    headers['Authorization'] = 'Basic {0}'.format(
        b64encode(basic_auth_bytes).decode('utf-8')
    )
    try:
        token_request = session.post(token_info_url, data=request, headers=headers)
        if not token_request.ok:
            return None
        json = token_request.json()
        if "active" in json and json["active"] is False:
            return None
        return json
    except Exception as e:
        logger.error(str(e))
        return None


def validate_scope(required_scopes, token_scopes) -> bool:
    return True
