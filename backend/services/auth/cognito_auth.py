import os
from typing import Dict, Any, List

import requests
from fastapi import Header, HTTPException
from jose import jwt


class CognitoAuthService:
    def __init__(self):
        self.region = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
        self.user_pool_id = os.getenv("COGNITO_USER_POOL_ID")
        self.app_client_id = os.getenv("COGNITO_APP_CLIENT_ID")

        self.issuer = (
            f"https://cognito-idp.{self.region}.amazonaws.com/"
            f"{self.user_pool_id}"
        )

        self.jwks_url = f"{self.issuer}/.well-known/jwks.json"
        self.jwks = None

    def _load_jwks(self):
        if not self.user_pool_id:
            raise HTTPException(
                status_code=500,
                detail="COGNITO_USER_POOL_ID is not configured."
            )

        if not self.jwks:
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            self.jwks = response.json()

        return self.jwks

    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            jwks = self._load_jwks()

            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")

            key = None

            for jwk_key in jwks.get("keys", []):
                if jwk_key.get("kid") == kid:
                    key = jwk_key
                    break

            if not key:
                raise HTTPException(
                    status_code=401,
                    detail="Invalid token signing key."
                )

            claims = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=self.app_client_id,
                issuer=self.issuer
            )

            return claims

        except HTTPException:
            raise
        except Exception as error:
            raise HTTPException(
                status_code=401,
                detail=f"Token validation failed: {str(error)}"
            )

    def get_groups(self, claims: Dict[str, Any]) -> List[str]:
        return claims.get("cognito:groups", [])

    def require_any_group(
        self,
        claims: Dict[str, Any],
        allowed_groups: List[str]
    ):
        user_groups = self.get_groups(claims)

        if not any(group in user_groups for group in allowed_groups):
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to access this resource."
            )


auth_service = CognitoAuthService()


def get_current_user(
    authorization: str = Header(default=None)
) -> Dict[str, Any]:

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header."
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format."
        )

    token = authorization.replace("Bearer ", "").strip()
    claims = auth_service.verify_token(token)

    return {
        "username": claims.get("cognito:username"),
        "email": claims.get("email"),
        "groups": auth_service.get_groups(claims),
        "claims": claims
    }


def require_groups(user: Dict[str, Any], allowed_groups: List[str]):
    user_groups = user.get("groups", [])

    if not any(group in user_groups for group in allowed_groups):
        raise HTTPException(
            status_code=403,
            detail="Insufficient role permissions."
        )
