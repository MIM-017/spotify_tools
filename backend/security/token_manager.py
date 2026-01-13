import jwt
import secrets
import json
import errno
from datetime import datetime, timedelta, UTC
from jwt import ExpiredSignatureError, PyJWTError

from ..config import ACCESS_TOKEN_EXPIRE, SECRET_KEY
from ..services.logging import *


class TokenManager:
    """Token Manager class to manage the tokens issued by the app"""

    SECRET_KEY = SECRET_KEY
    algorithm = "HS256"

    def __init__(self, token_file_path: str = None):
        if token_file_path is None:
            self.token_file_path = "backend/tokens/app_tokens.json"
        else:
            self.token_file_path = token_file_path

        self.logger = setup_module_logger(__name__)

    @staticmethod
    def create_refresh_token() -> str:
        return secrets.token_hex(32)

    def save_refresh_token(self, spotify_user_id: str, refresh_token: str = None) -> str:
        """Saves the refresh token with the user id to the token file,
         if the token is not provided, generates it and returns"""

        if refresh_token is None:
            refresh_token = self.create_refresh_token()

        expiration_date = (datetime.now(UTC) + timedelta(hours=ACCESS_TOKEN_EXPIRE)).isoformat()

        try:
            with open(self.token_file_path, "r") as f:
                data = dict(json.loads(f.read()))
                data[refresh_token] = {"user_id": spotify_user_id, "expires": expiration_date}

            with open(self.token_file_path, "w") as f:
                f.write(json.dumps(data))

        except (json.JSONDecodeError, KeyError):
            self.logger.warning(f"Couldn't decode JSON from token file at: {self.token_file_path}. Overwriting data.")

            with open(self.token_file_path, "w") as f:
                data = {"data":
                            {refresh_token: {"user_id": spotify_user_id, "expires": expiration_date}}
                        }

                f.write(json.dumps(data))

        except FileNotFoundError:
            self.logger.info(f"Creating a new JSON token file at: {self.token_file_path}")

            with open(self.token_file_path, "w") as f:
                data = {"data":
                            {refresh_token: {"user_id": spotify_user_id, "expires": expiration_date}}
                        }

                f.write(json.dumps(data))

        return refresh_token

    def retrieve_user_id_from_refresh_token(self, refresh_token: str) -> str | None:
        """Returns the spotify user id from a database with the provided refresh token.
        Returns None if there is no user associated with the provided refresh token or if the token is expired

        :param refresh_token: refresh token"""

        spotify_user_id = None

        try:
            with open(self.token_file_path, encoding='utf-8') as f:
                token_info_string = f.read()
                data = dict(json.loads(token_info_string)[refresh_token])
                spotify_user_id = data["user_id"]
                expires_date = datetime.fromisoformat(data["expires"])

                if expires_date < datetime.now(UTC):
                    spotify_user_id = None

        except OSError as error:
            if error.errno == errno.ENOENT:
                self.logger.debug(f"Token file does not exist at: {self.token_file_path}")
            else:
                self.logger.warning(f"Couldn't read token file at: {self.token_file_path}")
        except json.JSONDecodeError:
            self.logger.warning(f"Couldn't decode JSON from token file at: {self.token_file_path}")
        except KeyError:
            return None

        return spotify_user_id

    def create_jwt(self, spotify_user_id: str) -> str:
        """Creates a JWT access token with a spotify user id"""
        expiration_date = datetime.now(UTC) + timedelta(hours=ACCESS_TOKEN_EXPIRE)

        return jwt.encode({"spotify_user_id": spotify_user_id,
                           "exp": expiration_date},
                          self.SECRET_KEY,
                          algorithm=self.algorithm)

    def get_spotify_user_id(self, JWT: str) -> str | None:
        """Returns a spotify user id from a provided JWT"""

        try:
            return jwt.decode(JWT, self.SECRET_KEY, algorithms=self.algorithm)["spotify_user_id"]
        except (ExpiredSignatureError, PyJWTError):
            return None
