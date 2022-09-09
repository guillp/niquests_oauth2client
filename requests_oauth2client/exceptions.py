"""This module contains all exception classes from `requests_oauth2client`."""

from typing import Optional

from jwskate import InvalidJwt


class OAuth2Error(Exception):
    """Base class for Exceptions raised by requests_oauth2client."""


class EndpointError(OAuth2Error):
    """Base class for exceptions raised from the token endpoint errors.

    An `EndpointError` contains the error message, description and uri that are returned by the AS in the OAuth 2.0 standardised way.

    Args:
        error: the `error` identifier as returned by the AS
        description: the `error_description` as returned by the AS
        uri: the `error_uri` as returned by the AS
    """

    def __init__(
        self, error: str, description: Optional[str] = None, uri: Optional[str] = None
    ):
        self.error = error
        self.description = description
        self.uri = uri


class InvalidTokenResponse(OAuth2Error):
    """Raised when the Token Endpoint returns a non-standard response."""


class ExpiredAccessToken(OAuth2Error):
    """Raised when an expired access token is used."""


class UnknownTokenEndpointError(EndpointError):
    """Raised when an otherwise unknown error is returned by the token endpoint."""


class ServerError(EndpointError):
    """Raised when the token endpoint returns `error = server_error`."""


class TokenEndpointError(EndpointError):
    """Base class for errors that are specific to the token endpoint."""


class InvalidScope(TokenEndpointError):
    """Raised when the Token Endpoint returns `error = invalid_scope`."""


class InvalidTarget(TokenEndpointError):
    """Raised when the Token Endpoint returns `error = invalid_target`."""


class InvalidGrant(TokenEndpointError):
    """Raised when the Token Endpoint returns `error = invalid_grant`."""


class AccessDenied(EndpointError):
    """Raised when the Authorization Server returns `error = access_denied`."""


class UnauthorizedClient(EndpointError):
    """Raised when the Authorization Server returns `error = unauthorized_client`."""


class RevocationError(EndpointError):
    """Base class for Revocation Endpoint errors."""


class UnsupportedTokenType(RevocationError):
    """Raised when the Revocation endpoint returns `error = unsupported_token_type`."""


class IntrospectionError(EndpointError):
    """Base class for Introspection Endpoint errors."""


class UnknownIntrospectionError(OAuth2Error):
    """Raised when the Introspection Endpoint retuns a non-standard error."""


class DeviceAuthorizationError(EndpointError):
    """Base class for Device Authorization Endpoint errors."""


class AuthorizationPending(TokenEndpointError):
    """Raised when the Token Endpoint returns `error = authorization_pending`."""


class SlowDown(TokenEndpointError):
    """Raised when the Token Endpoint returns `error = slow_down`."""


class ExpiredToken(TokenEndpointError):
    """Raised when the Token Endpoint returns `error = expired_token`."""


class InvalidDeviceAuthorizationResponse(OAuth2Error):
    """Raised when the Device Authorization Endpoint returns a non-standard error response."""


class InvalidIdToken(InvalidJwt):
    """Raised when trying to validate an invalid Id Token value."""


class AuthorizationResponseError(Exception):
    """Base class for error responses returned by the Authorization endpoint.

    An `AuthorizationResponseError` contains the error message, description and uri that are returned by the AS.

    Args:
        error: the `error` identifier as returned by the AS
        description: the `error_description` as returned by the AS
        uri: the `error_uri` as returned by the AS
    """

    def __init__(
        self, error: str, description: Optional[str] = None, uri: Optional[str] = None
    ):
        self.error = error
        self.description = description
        self.uri = uri


class InteractionRequired(AuthorizationResponseError):
    """Raised when the Authorization Endpoint returns `error = interaction_required`."""


class LoginRequired(InteractionRequired):
    """Raised when the Authorization Endpoint returns `error = login_required`."""


class AccountSelectionRequired(InteractionRequired):
    """Raised when the Authorization Endpoint returns `error = account_selection_required`."""


class SessionSelectionRequired(InteractionRequired):
    """Raised when the Authorization Endpoint returns `error = session_selection_required`."""


class ConsentRequired(InteractionRequired):
    """Raised when the Authorization Endpoint returns `error = consent_required`."""


class InvalidAuthResponse(OAuth2Error):
    """Raised when the Authorization Endpoint returns an invalid response."""


class MissingAuthCode(InvalidAuthResponse):
    """Raised when the Authorization Endpoint does not return the mandatory `code`.

    This happens when the Authorization Endpoint does not return an error, but does not return
    an authorization `code` either.
    """


class MissingIdToken(InvalidAuthResponse):
    """Raised when the Authorization Endpoint does not return a mandatory ID Token.

    This happens when the Authorization Endpoint does not return an error, but does not return
    an ID Token either.
    """


class MismatchingState(InvalidAuthResponse):
    """Raised on mismatching `state` value.

    This happens when the Authorization Endpoints returns a 'state' parameter that doesn't match
    the value passed in the Authorization Request.
    """


class MismatchingIssuer(InvalidAuthResponse):
    """Raised on mismatching `iss` value.

    This happens when the Authorization Endpoints returns an 'iss' that doesn't match the
    expected value.
    """


class MismatchingNonce(InvalidIdToken):
    """Raised on mismatching `nonce` value in an ID Token.

    This happens when the authorization request includes a `nonce` but the returned ID Token
    include a different value.
    """


class MismatchingAcr(InvalidIdToken):
    """Raised when the returned ID Token doesn't contain one of the requested ACR Values.

    This happens when the authorization request includes an `acr_values` parameter but the
    returned ID Token includes a different value.
    """


class MismatchingAudience(InvalidIdToken):
    """Raised when the ID Token audience does not include the requesting Client ID."""


class MismatchingAzp(InvalidIdToken):
    """Raised when the ID Token Authorized Presenter (azp) claim is not the Client ID."""


class MismatchingIdTokenAlg(InvalidIdToken):
    """Raised when the returned ID Token is signed with an unexpected alg."""


class ExpiredIdToken(InvalidIdToken):
    """Raised when the returned ID Token is expired."""


class BackChannelAuthenticationError(EndpointError):
    """Base class for errors returned by the BackChannel Authentication endpoint."""


class InvalidBackChannelAuthenticationResponse(OAuth2Error):
    """Raised when the BackChannel Authentication endpoint returns a non-standard response."""


class InvalidPushedAuthorizationResponse(OAuth2Error):
    """Raised when the Pushed Authorization Endpoint returns an error."""
