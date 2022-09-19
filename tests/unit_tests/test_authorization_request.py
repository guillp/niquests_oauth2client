from typing import Union

import pytest
from furl import furl  # type: ignore[import]
from jwskate import Jwk, Jwt, SignedJwt

from requests_oauth2client import (
    AuthorizationRequest,
    AuthorizationRequestSerializer,
    AuthorizationResponse,
    AuthorizationResponseError,
    MismatchingIssuer,
    MismatchingState,
    MissingAuthCode,
)
from tests.conftest import FixtureRequest


def test_authorization_url(authorization_request: AuthorizationRequest) -> None:
    url = furl(str(authorization_request))
    assert dict(url.args) == {
        key: val for key, val in authorization_request.args.items() if val is not None
    }


def test_authorization_signed_request(
    authorization_request: AuthorizationRequest, private_jwk: Jwk, public_jwk: Jwk
) -> None:
    args = {
        key: value for key, value in authorization_request.args.items() if value is not None
    }
    url = furl(str(authorization_request.sign(private_jwk)))
    request = url.args.get("request")
    jwt = Jwt(request)
    assert isinstance(jwt, SignedJwt)
    assert jwt.verify_signature(public_jwk)
    assert jwt.claims == args


@pytest.fixture(params=["consent_required"])
def error(request: FixtureRequest) -> str:
    return request.param


def test_error_response(
    authorization_request: AuthorizationRequest,
    authorization_response_uri: furl,
    error: str,
) -> None:
    authorization_response_uri.args.pop("code")
    authorization_response_uri.args.add("error", error)
    with pytest.raises(AuthorizationResponseError):
        authorization_request.validate_callback(authorization_response_uri)


def test_missing_code(
    authorization_request: AuthorizationRequest, authorization_response_uri: furl
) -> None:
    authorization_response_uri.args.pop("code")
    with pytest.raises(MissingAuthCode):
        authorization_request.validate_callback(authorization_response_uri)


def test_not_an_url(authorization_request: AuthorizationRequest) -> None:
    auth_response = "https://...$cz\\1.3ada////:@+++++z/"
    with pytest.raises(ValueError):
        authorization_request.validate_callback(auth_response)


def test_mismatching_state(
    authorization_request: AuthorizationRequest,
    authorization_response_uri: furl,
    state: Union[None, bool, str],
) -> None:
    authorization_response_uri.args["state"] = "foo"
    if state:
        with pytest.raises(MismatchingState):
            authorization_request.validate_callback(authorization_response_uri)


def test_missing_state(
    authorization_request: AuthorizationRequest,
    authorization_response_uri: furl,
    state: Union[None, bool, str],
) -> None:
    authorization_response_uri.args.pop("state", None)
    if state:
        with pytest.raises(MismatchingState):
            authorization_request.validate_callback(authorization_response_uri)


def test_mismatching_iss(
    authorization_request: AuthorizationRequest,
    authorization_response_uri: furl,
    expected_issuer: Union[str, bool, None],
) -> None:
    authorization_response_uri.args["iss"] = "foo"
    if isinstance(expected_issuer, str) or expected_issuer is False:
        with pytest.raises(MismatchingIssuer):
            authorization_request.validate_callback(authorization_response_uri)


def test_missing_issuer(
    authorization_request: AuthorizationRequest,
    authorization_response_uri: furl,
    expected_issuer: Union[str, bool, None],
) -> None:
    authorization_response_uri.args.pop("iss", None)
    if expected_issuer:
        with pytest.raises(MismatchingIssuer):
            authorization_request.validate_callback(authorization_response_uri)


def test_authorization_request_serializer(authorization_request: AuthorizationRequest) -> None:
    serializer = AuthorizationRequestSerializer()
    serialized = serializer.dumps(authorization_request)
    assert serializer.loads(serialized) == authorization_request
