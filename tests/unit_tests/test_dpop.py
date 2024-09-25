import secrets

import pytest
import requests
from binapy import BinaPy
from freezegun import freeze_time
from jwskate import Jwk, Jwt, KeyManagementAlgs, SignatureAlgs, SignedJwt

from requests_oauth2client import (
    DPoPKey,
    DPoPToken,
    InvalidDPoPAccessToken,
    InvalidDPoPAlg,
    InvalidDPoPKey,
    InvalidDPoPProof,
    OAuth2Client,
    validate_dpop_proof,
)
from tests.conftest import RequestsMocker


@pytest.mark.parametrize("alg", SignatureAlgs.ALL_ASYMMETRIC)
def test_dpop_key(alg: str) -> None:
    generated_dpopkey = DPoPKey.generate(alg=alg)
    assert generated_dpopkey.alg == alg

    private_key = Jwk.generate(alg=alg)
    choosen_dpop_key = DPoPKey(private_key=private_key)
    assert choosen_dpop_key.alg == alg
    assert choosen_dpop_key.private_key == private_key

    proof = choosen_dpop_key.proof(htm="POST", htu="https://myapi.local/")
    assert proof.alg == alg

    # you can also init a DPoPKey with any key material supported by `jwskate`
    choosen_dpop_key_cryptography = DPoPKey(private_key=private_key.cryptography_key, alg=alg)
    assert choosen_dpop_key_cryptography.alg == alg
    assert choosen_dpop_key_cryptography.private_key == private_key


@freeze_time()
def test_dpop_client_credentials_request(requests_mock: RequestsMocker) -> None:
    token_endpoint = "https://url.to.the/token_endpoint"
    client = OAuth2Client(
        token_endpoint=token_endpoint, client_id="foo", client_secret="bar", dpop_bound_access_tokens=True
    )

    access_token = "Kz~8mXK1EalYznwH-LC-1fBAo.4Ljp~zsPE_NeO.gxU"
    requests_mock.post(
        token_endpoint,
        json={
            "access_token": access_token,
            "token_type": "DPoP",
            "expires_in": 2677,
            "refresh_token": "Q..Zkm29lexi8VnWg2zPW1x-tgGad0Ibc3s3EwM_Ni4-g",
        },
    )

    dpop_token = client.client_credentials()
    assert isinstance(dpop_token, DPoPToken)
    assert dpop_token.token_type == "DPoP"
    dpop_key = dpop_token.dpop_key
    assert isinstance(dpop_key, DPoPKey)

    assert requests_mock.called_once
    token_request = requests_mock.last_request
    assert token_request is not None
    dpop = Jwt(token_request.headers["DPoP"])
    assert isinstance(dpop, SignedJwt)
    assert dpop.headers == {
        "typ": "dpop+jwt",
        "alg": "ES256",
        "jwk": dpop_key.private_key.public_jwk().minimize(),
    }
    assert dpop.claims["htm"] == "POST"
    assert dpop.claims["htu"] == token_endpoint
    assert dpop.claims["iat"] == Jwt.timestamp()
    assert len(dpop.claims["jti"]) > 16
    assert dpop.verify_signature(dpop_key.public_jwk)


@freeze_time()
@pytest.mark.parametrize("alg", SignatureAlgs.ALL_ASYMMETRIC)
def test_dpop_token_api_request(requests_mock: RequestsMocker, alg: str) -> None:
    private_key = Jwk.generate(alg=alg)
    dpop_key = DPoPKey(private_key=private_key)
    access_token = secrets.token_urlsafe(64)
    dpop_token = DPoPToken(access_token=access_token, _dpop_key=dpop_key)

    target_api = "https://my.api/resource"
    requests_mock.put(target_api)
    requests.put(target_api, params={"key": "value"}, auth=dpop_token)
    assert requests_mock.called_once
    api_request = requests_mock.last_request
    assert api_request is not None
    assert api_request.headers["Authorization"] == f"DPoP {access_token}"
    dpop = Jwt(api_request.headers["DPoP"])
    assert isinstance(dpop, SignedJwt)
    assert dpop.headers == {
        "typ": "dpop+jwt",
        "alg": alg,
        "jwk": dpop_token.dpop_key.private_key.public_jwk().minimize(),
    }
    assert dpop.claims["htm"] == "PUT"
    assert dpop.claims["htu"] == target_api  # must not include query parameters or fragment
    assert dpop.claims["iat"] == Jwt.timestamp()
    assert len(dpop.claims["jti"]) > 16
    assert dpop.claims["ath"] == BinaPy(access_token).to("sha256").to("b64u").ascii()
    assert dpop.verify_signature(private_key.public_jwk())


@freeze_time()
def test_dpop_access_token_request_with_choosen_key(requests_mock: RequestsMocker) -> None:
    dpop_alg = "ES512"
    private_key = Jwk.generate(alg=dpop_alg)
    dpop_key = DPoPKey(private_key=private_key)
    token_endpoint = "https://url.to.the/token_endpoint"
    client = OAuth2Client(
        token_endpoint=token_endpoint, client_id="foo", client_secret="bar", dpop_bound_access_tokens=True
    )

    requests_mock.post(
        token_endpoint,
        json={
            "access_token": "Kz~8mXK1EalYznwH-LC-1fBAo.4Ljp~zsPE_NeO.gxU",
            "token_type": "DPoP",
            "expires_in": 2677,
            "refresh_token": "Q..Zkm29lexi8VnWg2zPW1x-tgGad0Ibc3s3EwM_Ni4-g",
        },
    )

    dpop_token = client.client_credentials(dpop_key=dpop_key)
    assert isinstance(dpop_token, DPoPToken)
    assert dpop_token.token_type == "DPoP"
    assert dpop_token.dpop_key == dpop_key

    assert requests_mock.called_once
    token_request = requests_mock.last_request
    assert token_request is not None
    dpop = Jwt(token_request.headers["DPoP"])
    assert isinstance(dpop, SignedJwt)
    assert dpop.headers == {"typ": "dpop+jwt", "alg": dpop_alg, "jwk": private_key.public_jwk().minimize()}
    assert dpop.claims["htm"] == "POST"
    assert dpop.claims["htu"] == token_endpoint
    assert dpop.claims["iat"] == Jwt.timestamp()
    assert len(dpop.claims["jti"]) > 16

    # make sure that passing a dpop_key is enough to toggle DPoP, even if dpop=False
    assert isinstance(client.client_credentials(dpop=False, dpop_key=dpop_key), DPoPToken)
    assert requests_mock.last_request is not None
    assert "DPoP" in requests_mock.last_request.headers


def test_dpop_proof() -> None:
    key = DPoPKey.generate(alg="ES256")
    htm = "GET"
    htu = "https://myapi.local"
    nonce = "this_is_a_nonce"
    ath = "fUHyO2r2Z3DZ53EsNrWBb0xWXoaNy59IiKCAqksmQEo"
    proof = key.proof(htm=htm, htu=htu, ath=ath, nonce=nonce)
    assert proof.claims["htm"] == htm
    assert proof.claims["htu"] == htu
    assert proof.claims["nonce"] == nonce
    assert proof.claims["ath"] == ath
    assert proof.verify_signature(key.private_key.public_jwk())


def test_dpop_errors() -> None:
    with pytest.raises(InvalidDPoPAccessToken, match="invalid characters"):
        DPoPToken(access_token="some_invalid_characters_follow: ?%", _dpop_key=DPoPKey.generate(alg="ES256"))

    with pytest.raises(InvalidDPoPAlg, match="DPoP proofing require an asymmetric signing alg."):
        DPoPToken(access_token="access_token", _dpop_key=DPoPKey.generate(alg="HS256"))

    with pytest.raises(InvalidDPoPKey, match="not an asymmetric private key"):
        DPoPKey(private_key=Jwk.generate(alg="HS256"))

    with pytest.raises(InvalidDPoPAlg):
        OAuth2Client(
            token_endpoint="https://as.local/token",
            client_id="client_id",
            client_secret="client_secret",
            dpop_alg=KeyManagementAlgs.ECDH_ES,
        )

    with pytest.raises(InvalidDPoPAlg):
        OAuth2Client(
            token_endpoint="https://as.local/token",
            client_id="client_id",
            client_secret="client_secret",
            dpop_alg="UnknownAlg",
        )


@freeze_time()
def test_dpop_authorization_code_flow(
    requests_mock: RequestsMocker, oauth2client: OAuth2Client, token_endpoint: str
) -> None:
    azreq = oauth2client.authorization_request(dpop=True)
    assert isinstance(azreq.dpop_key, DPoPKey)
    assert azreq.dpop_key.alg == oauth2client.dpop_alg

    assert azreq.dpop_jkt == azreq.dpop_key.private_key.thumbprint()

    az_code = "my_az_code"

    callback_uri = f"{azreq.redirect_uri}?code={az_code}&state={azreq.state}&iss={azreq.issuer}"

    azresp = azreq.validate_callback(callback_uri)
    assert azresp.dpop_key == azreq.dpop_key

    requests_mock.post(
        token_endpoint,
        json={
            "token_type": "DPoP",
            "access_token": "my_access_token",
            "refresh_token": "my_refresh_token",
            "expires_in": 3600,
        },
    )
    token = oauth2client.authorization_code(azresp)
    assert isinstance(token, DPoPToken)
    assert token.dpop_key == azreq.dpop_key

    assert requests_mock.last_request is not None
    assert "DPoP" in requests_mock.last_request.headers
    dpop_proof = validate_dpop_proof(
        requests_mock.last_request.headers["DPoP"], alg=oauth2client.dpop_alg, htm="POST", htu=token_endpoint
    )
    assert isinstance(dpop_proof, SignedJwt)
    assert dpop_proof.iat == Jwt.timestamp()

    refreshed_token = oauth2client.refresh_token(token)
    assert isinstance(refreshed_token, DPoPToken)
    assert refreshed_token.dpop_key == azreq.dpop_key
    dpop_proof2 = validate_dpop_proof(requests_mock.last_request.headers["DPoP"], htm="POST", htu=token_endpoint)
    assert isinstance(dpop_proof2, SignedJwt)
    assert dpop_proof2.iat == Jwt.timestamp()
    assert dpop_proof.jwt_token_id != dpop_proof2.jwt_token_id


def test_validate_dpop_proof() -> None:
    private_key = Jwk.generate(alg="ES256")
    htm = "POST"
    htu = "https://foo.bar"

    valid_proof = DPoPKey(private_key=private_key).proof(htm=htm, htu=htu).value

    assert isinstance(validate_dpop_proof(valid_proof, htm=htm, htu=htu), SignedJwt)

    with pytest.raises(InvalidDPoPProof, match="not a syntactically valid JWT"):
        validate_dpop_proof("not.a.jwt", htm=htm, htu=htu)
    with pytest.raises(InvalidDPoPProof, match=r"not the expected 'dpop\+jwt'"):
        validate_dpop_proof(
            DPoPKey(private_key=private_key, jwt_typ="not-a-dpop-jwt").proof(htm=htm, htu=htu).value, htm=htm, htu=htu
        )
    with pytest.raises(InvalidDPoPProof, match=r"'jwk' header is missing"):
        validate_dpop_proof(
            SignedJwt.sign_arbitrary(
                {"iat": Jwt.timestamp(), "htm": htm, "htu": htu, "jti": "random"},
                headers={"alg": private_key.alg, "typ": "dpop+jwt"},
                key=private_key,
            ).value,
            htm=htm,
            htu=htu,
        )
    with pytest.raises(InvalidDPoPProof, match=r"'jwk' header is not a valid JWK"):
        validate_dpop_proof(
            SignedJwt.sign_arbitrary(
                {"iat": Jwt.timestamp(), "htm": htm, "htu": htu, "jti": "random"},
                headers={"alg": private_key.alg, "typ": "dpop+jwt", "jwk": {"foo": "bar"}},
                key=private_key,
            ).value,
            htm=htm,
            htu=htu,
        )
    with pytest.raises(InvalidDPoPProof, match=r"'jwk' header is a private or symmetric key"):
        validate_dpop_proof(
            SignedJwt.sign_arbitrary(
                {"iat": Jwt.timestamp(), "htm": htm, "htu": htu, "jti": "random"},
                headers={"alg": private_key.alg, "typ": "dpop+jwt", "jwk": private_key},
                key=private_key,
            ).value,
            htm=htm,
            htu=htu,
        )

    with pytest.raises(InvalidDPoPProof, match=r"signature does not verify"):
        validate_dpop_proof(valid_proof[:-4] + b"aaaa", htm=htm, htu=htu)

    with pytest.raises(InvalidDPoPProof, match=r"Issued At \(iat\) claim is missing"):
        validate_dpop_proof(
            SignedJwt.sign_arbitrary(
                {"htm": htm, "htu": htu, "jti": "random"},
                headers={"alg": private_key.alg, "typ": "dpop+jwt", "jwk": private_key.public_jwk()},
                key=private_key,
            ).value,
            htm=htm,
            htu=htu,
        )
    with pytest.raises(InvalidDPoPProof, match=r"Issued At timestamp \(iat\) is too far away in the past or future"):
        validate_dpop_proof(
            SignedJwt.sign_arbitrary(
                {"iat": Jwt.timestamp(-50000), "htm": htm, "htu": htu, "jti": "random"},
                headers={"alg": private_key.alg, "typ": "dpop+jwt", "jwk": private_key.public_jwk()},
                key=private_key,
            ).value,
            htm=htm,
            htu=htu,
        )
    with pytest.raises(InvalidDPoPProof, match=r"a Unique Identifier \(jti\) claim is missing"):
        validate_dpop_proof(
            SignedJwt.sign_arbitrary(
                {"iat": Jwt.timestamp(), "htm": htm, "htu": htu},
                headers={"alg": private_key.alg, "typ": "dpop+jwt", "jwk": private_key.public_jwk()},
                key=private_key,
            ).value,
            htm=htm,
            htu=htu,
        )
    with pytest.raises(InvalidDPoPProof, match=r"the HTTP method \(htm\) claim is missing."):
        validate_dpop_proof(
            SignedJwt.sign_arbitrary(
                {"iat": Jwt.timestamp(), "htu": htu, "jti": "random"},
                headers={"alg": private_key.alg, "typ": "dpop+jwt", "jwk": private_key.public_jwk()},
                key=private_key,
            ).value,
            htm=htm,
            htu=htu,
        )
    with pytest.raises(InvalidDPoPProof, match=rf"HTTP Method \(htm\) does not matches expected '{htm}'"):
        validate_dpop_proof(
            SignedJwt.sign_arbitrary(
                {"iat": Jwt.timestamp(), "htm": "PATCH", "htu": htu, "jti": "random"},
                headers={"alg": private_key.alg, "typ": "dpop+jwt", "jwk": private_key.public_jwk()},
                key=private_key,
            ).value,
            htm=htm,
            htu=htu,
        )
    with pytest.raises(InvalidDPoPProof, match=r"the HTTP URI \(htu\) claim is missing"):
        validate_dpop_proof(
            SignedJwt.sign_arbitrary(
                {"iat": Jwt.timestamp(), "htm": htm, "jti": "random"},
                headers={"alg": private_key.alg, "typ": "dpop+jwt", "jwk": private_key.public_jwk()},
                key=private_key,
            ).value,
            htm=htm,
            htu=htu,
        )
    with pytest.raises(InvalidDPoPProof, match=rf"HTTP URI \(htu\) does not matches expected '{htu}'"):
        validate_dpop_proof(
            SignedJwt.sign_arbitrary(
                {"iat": Jwt.timestamp(), "htm": htm, "htu": "https://something.else", "jti": "random"},
                headers={"alg": private_key.alg, "typ": "dpop+jwt", "jwk": private_key.public_jwk()},
                key=private_key,
            ).value,
            htm=htm,
            htu=htu,
        )

    with pytest.raises(InvalidDPoPProof, match=r"the Access Token hash \(ath\) claim is missing"):
        validate_dpop_proof(valid_proof, htm=htm, htu=htu, ath="my_ath")
    with pytest.raises(InvalidDPoPProof, match=r"the DPoP Nonce \(nonce\) claim is missing"):
        validate_dpop_proof(valid_proof, htm=htm, htu=htu, nonce="my_nonce")
    with pytest.raises(InvalidDPoPProof, match=r"Access Token Hash \(ath\) value 'foo' does not match expected 'bar'"):
        validate_dpop_proof(
            DPoPKey(private_key=private_key).proof(htm=htm, htu=htu, ath="foo").value, htm=htm, htu=htu, ath="bar"
        )
    with pytest.raises(InvalidDPoPProof, match=r"DPoP Nonce \(nonce\) value 'foo' does not match expected 'bar'"):
        validate_dpop_proof(
            DPoPKey(private_key=private_key).proof(htm=htm, htu=htu, nonce="foo").value, htm=htm, htu=htu, nonce="bar"
        )

    ath = "my_ath"
    nonce = "my_nonce"
    assert isinstance(
        validate_dpop_proof(
            DPoPKey(private_key=private_key).proof(htm=htm, htu=htu, ath=ath, nonce=nonce).value,
            htm=htm,
            htu=htu,
            ath=ath,
            nonce=nonce,
        ),
        SignedJwt,
    )
