from fastapi.security import APIKeyCookie
from fastapi import Security, APIRouter, Response
import jwt
import secrets

SECRET_KEY = "f34cad96ab843ae541fa90f269ecce855a94fa0937f01267b2097a55e5e102a4"
algorithm = "HS256"
ACCESS_TOKEN_EXPIRE = 60 * 60 * 24
REFRESH_TOKEN_EXPIRE = 60 * 60 * 24 * 14

access_scheme = APIKeyCookie(name="access_token", auto_error=False)
refresh_scheme = APIKeyCookie(name="refresh_token")

auth_router = APIRouter()

def create_JWT(spotify_user_id: str) -> str:
    """Creates a JWT token with a spotify user id"""
    return jwt.encode({"spotify_user_id": spotify_user_id}, SECRET_KEY, algorithm=algorithm)

def get_spotify_user_id(JWT: str) -> str:
    """Returns a spotify user id from a provided JWT"""
    return jwt.decode(JWT, SECRET_KEY, algorithms=algorithm)["spotify_user_id"]

def create_refresh_token() -> str:
    return secrets.token_hex(32)

def retrieve_spotify_token(JWT: str) -> str:
    """Returns the spotify user token from a database"""
    pass

def set_access_token_cookie(response: Response):
    """Sets the access token cookie in the provided response instance"""
    response.set_cookie(key="access_token",
                        value=create_JWT(), httponly=True)


@auth_router.get("/check_tokens")
def check_auth(access_token = Security(access_scheme), refresh_token = Security(refresh_scheme)):
    if refresh_token is None:
