"""Main module for `requests_oauth2client`.

You can import any class from any submodule directly from this main module.

"""

import requests
from jwskate import EncryptionAlgs, KeyManagementAlgs, SignatureAlgs

from .api_client import ApiClient
from .auth import (
    BaseOAuth2RenewableTokenAuth,
    BearerAuth,
    OAuth2AccessTokenAuth,
    OAuth2AuthorizationCodeAuth,
    OAuth2ClientCredentialsAuth,
    OAuth2DeviceCodeAuth,
    OAuth2ResourceOwnerPasswordAuth,
)
from .authorization_request import (
    AuthorizationRequest,
    AuthorizationRequestSerializer,
    AuthorizationResponse,
    PkceUtils,
    RequestParameterAuthorizationRequest,
    RequestUriParameterAuthorizationRequest,
)
from .backchannel_authentication import (
    BackChannelAuthenticationPoolingJob,
    BackChannelAuthenticationResponse,
)
from .client import (
    GrantType,
    OAuth2Client,
)
from .client_authentication import (
    BaseClientAuthenticationMethod,
    ClientAssertionAuthenticationMethod,
    ClientSecretBasic,
    ClientSecretJwt,
    ClientSecretPost,
    PrivateKeyJwt,
    PublicApp,
)
from .device_authorization import (
    DeviceAuthorizationPoolingJob,
    DeviceAuthorizationResponse,
)
from .discovery import (
    oauth2_discovery_document_url,
    oidc_discovery_document_url,
    well_known_uri,
)
from .exceptions import (
    AccessDenied,
    AccountSelectionRequired,
    AuthorizationPending,
    AuthorizationResponseError,
    BackChannelAuthenticationError,
    ConsentRequired,
    DeviceAuthorizationError,
    EndpointError,
    ExpiredAccessToken,
    ExpiredIdToken,
    ExpiredToken,
    InteractionRequired,
    IntrospectionError,
    InvalidAuthResponse,
    InvalidBackChannelAuthenticationResponse,
    InvalidClient,
    InvalidDeviceAuthorizationResponse,
    InvalidGrant,
    InvalidIdToken,
    InvalidPushedAuthorizationResponse,
    InvalidRequest,
    InvalidScope,
    InvalidTarget,
    InvalidTokenResponse,
    LoginRequired,
    MismatchingAcr,
    MismatchingAudience,
    MismatchingAzp,
    MismatchingIdTokenAlg,
    MismatchingIssuer,
    MismatchingNonce,
    MismatchingState,
    MissingAuthCode,
    MissingIdToken,
    MissingIssuer,
    OAuth2Error,
    RevocationError,
    ServerError,
    SessionSelectionRequired,
    SlowDown,
    TokenEndpointError,
    UnauthorizedClient,
    UnknownIntrospectionError,
    UnknownTokenEndpointError,
    UnsupportedTokenType,
)
from .pooling import (
    TokenEndpointPoolingJob,
)
from .tokens import (
    BearerToken,
    BearerTokenSerializer,
    IdToken,
)

__all__ = [
    "AccessDenied",
    "AccountSelectionRequired",
    "ApiClient",
    "AuthorizationPending",
    "AuthorizationRequest",
    "AuthorizationRequestSerializer",
    "AuthorizationResponse",
    "AuthorizationResponseError",
    "BackChannelAuthenticationError",
    "BackChannelAuthenticationPoolingJob",
    "BackChannelAuthenticationResponse",
    "BaseClientAuthenticationMethod",
    "BaseOAuth2RenewableTokenAuth",
    "BearerAuth",
    "BearerToken",
    "BearerTokenSerializer",
    "ClientAssertionAuthenticationMethod",
    "ClientSecretBasic",
    "ClientSecretJwt",
    "ClientSecretPost",
    "ConsentRequired",
    "DeviceAuthorizationError",
    "DeviceAuthorizationPoolingJob",
    "DeviceAuthorizationResponse",
    "EncryptionAlgs",
    "EndpointError",
    "ExpiredAccessToken",
    "ExpiredIdToken",
    "ExpiredToken",
    "GrantType",
    "IdToken",
    "InteractionRequired",
    "IntrospectionError",
    "InvalidAuthResponse",
    "InvalidBackChannelAuthenticationResponse",
    "InvalidClient",
    "InvalidDeviceAuthorizationResponse",
    "InvalidGrant",
    "InvalidIdToken",
    "InvalidPushedAuthorizationResponse",
    "InvalidRequest",
    "InvalidScope",
    "InvalidTarget",
    "InvalidTokenResponse",
    "KeyManagementAlgs",
    "LoginRequired",
    "MismatchingAcr",
    "MismatchingAudience",
    "MismatchingAzp",
    "MismatchingIdTokenAlg",
    "MismatchingIssuer",
    "MismatchingNonce",
    "MismatchingState",
    "MissingAuthCode",
    "MissingIdToken",
    "MissingIssuer",
    "OAuth2AccessTokenAuth",
    "OAuth2AuthorizationCodeAuth",
    "OAuth2Client",
    "OAuth2ClientCredentialsAuth",
    "OAuth2DeviceCodeAuth",
    "OAuth2Error",
    "OAuth2ResourceOwnerPasswordAuth",
    "PkceUtils",
    "PrivateKeyJwt",
    "PublicApp",
    "RequestParameterAuthorizationRequest",
    "RequestUriParameterAuthorizationRequest",
    "RevocationError",
    "ServerError",
    "SessionSelectionRequired",
    "SignatureAlgs",
    "SlowDown",
    "TokenEndpointError",
    "TokenEndpointPoolingJob",
    "UnauthorizedClient",
    "UnknownIntrospectionError",
    "UnknownTokenEndpointError",
    "UnsupportedTokenType",
    "requests",
    "oauth2_discovery_document_url",
    "oidc_discovery_document_url",
    "well_known_uri",
]
