from urllib.parse import parse_qs

import niquests
from requests_mock import Mocker

from niquests_oauth2client import (
    ClientSecretPost,
    OAuth2Client,
    OAuth2ClientCredentialsAuth,
)


def test_client_credentials_get_token(
    niquests_mock: Mocker,
    client_id: str,
    client_secret: str,
    token_endpoint: str,
    target_api: str,
    access_token: str,
) -> None:
    niquests_mock.post(
        token_endpoint,
        json={"access_token": access_token, "token_type": "Bearer", "expires_in": 3600},
    )
    client = OAuth2Client(token_endpoint, ClientSecretPost(client_id, client_secret))
    token_response = client.client_credentials()
    assert token_response.access_token == access_token

    assert niquests_mock.last_request is not None
    params = parse_qs(niquests_mock.last_request.text)
    assert params["client_id"][0] == client_id
    assert params["client_secret"][0] == client_secret
    assert params["grant_type"][0] == "client_credentials"


def test_client_credentials_api(
    niquests_mock: Mocker,
    access_token: str,
    token_endpoint: str,
    client_id: str,
    client_secret: str,
    target_api: str,
) -> None:
    client = OAuth2Client(token_endpoint, ClientSecretPost(client_id, client_secret))
    auth = OAuth2ClientCredentialsAuth(client)

    niquests_mock.post(
        token_endpoint,
        json={"access_token": access_token, "token_type": "Bearer", "expires_in": 3600},
    )
    niquests_mock.get(target_api, request_headers={"Authorization": f"Bearer {access_token}"})
    response = niquests.get(target_api, auth=auth)
    assert response.ok
    assert len(niquests_mock.request_history) == 2
    token_request = niquests_mock.request_history[0]
    api_request = niquests_mock.request_history[1]
    params = parse_qs(token_request.text)
    assert params.get("client_id") == [client_id]
    assert params.get("client_secret") == [client_secret]
    assert params.get("grant_type") == ["client_credentials"]

    assert api_request.headers.get("Authorization") == f"Bearer {access_token}"
