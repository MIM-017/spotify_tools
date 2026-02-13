"""Security endpoints and helper functions"""

from fastapi.security import APIKeyCookie
from fastapi import Security, APIRouter, Response, HTTPException, status, Depends
from starlette.responses import RedirectResponse
from typing import Annotated

from .token_manager import TokenManager
from ..config import ACCESS_TOKEN_EXPIRE, REFRESH_TOKEN_EXPIRE, WEBSITE_URI, DASHBOARD_URI

access_scheme = APIKeyCookie(name="access_token", auto_error=False)
refresh_scheme = APIKeyCookie(name="refresh_token", auto_error=False)

auth_router = APIRouter()

token_manager = TokenManager()

unauthorized_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="The refresh token is not valid."
)


def set_access_token_cookie(response: Response, jwt: str):
    """Sets the access token cookie in the provided response"""

    response.set_cookie(key="access_token",
                        value=jwt,
                        max_age=ACCESS_TOKEN_EXPIRE,
                        httponly=True,
                        secure=False,
                        path="/")  # TODO: Change secure to True in production


def set_refresh_token_cookie(response: Response, refresh_token: str):
    """Sets the refresh token cookie in the provided response with the provided refresh token"""

    response.set_cookie(key="refresh_token",
                        value=refresh_token,
                        max_age=REFRESH_TOKEN_EXPIRE,
                        httponly=True,
                        secure=False,
                        path="/")  # TODO: Change secure to True in production


def remove_auth_cookies(response: Response):
    response.delete_cookie(key="access_token",
                           secure=False,
                           httponly=True,
                           path="/")  # TODO: Change secure to True in production

    response.delete_cookie(key="refresh_token",
                           secure=False,
                           httponly=True,
                           path="/")


@auth_router.get("/check_tokens")
def check_auth(response: Response, access_token=Security(access_scheme), refresh_token=Security(refresh_scheme)):
    """
    Checks the refresh and the access tokens. If the access token is not set, sets it with the provided refresh token.
    If the refresh token is not set, returns the 401 Http Error.

    :param response:
    :param access_token:
    :param refresh_token:
    :return:
    """

    # Checking whether the refresh token is unset AND whether it maps to a user
    if refresh_token is None:
        raise unauthorized_exception

    user_id = token_manager.retrieve_user_id_from_refresh_token(refresh_token)
    if user_id is None:
        raise unauthorized_exception

    if access_token is None:
        jwt = token_manager.create_jwt(user_id)
        set_access_token_cookie(response, jwt)


@auth_router.get("/authorize_user")
async def authorize_user(code: str):
    from ..main import playlist_cleaner

    playlist_cleaner.set_current_username("temp")
    access_token = playlist_cleaner.auth_manager.get_access_token(code)
    user_id = playlist_cleaner.get_spotify_user_user_id(access_token)
    playlist_cleaner.auth_manager.cache_handler.assign_temp_token_to_user(user_id)

    response = RedirectResponse(DASHBOARD_URI)

    jwt = token_manager.create_jwt(spotify_user_id=user_id)
    set_access_token_cookie(response, jwt)

    refresh_token = token_manager.save_refresh_token(spotify_user_id=user_id)
    set_refresh_token_cookie(response, refresh_token)

    return response


def get_user_id(access_token: Annotated[str, Security(access_scheme)]):
    if access_token is None:
        raise unauthorized_exception
    return token_manager.get_spotify_user_id(access_token)


@auth_router.get("/logout")
async def logout_user(user_id: Annotated[str, Depends(get_user_id)]):
    from ..main import playlist_cleaner

    playlist_cleaner.auth_manager.cache_handler.delete_access_tokens(user_id)
    response = RedirectResponse(WEBSITE_URI)
    remove_auth_cookies(response)

    return response
