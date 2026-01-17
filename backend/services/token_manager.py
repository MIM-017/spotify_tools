import json
import logging
import os
import errno
from json import JSONDecodeError
from typing import Callable

from spotipy import CacheHandler


class TokenManager(CacheHandler):

    """
    Handles reading and writing cached Spotify authorization tokens
    as json files on disk.
    """

    logger = logging.getLogger(__name__)

    def __init__(self,
                 cache_path=None,
                 encoder_cls=None):
        """
        Parameters:
             * cache_path: May be supplied, will otherwise be generated
                           (takes precedence over `username`)
             * encoder_cls: May be supplied as a means of overwriting the
                        default serializer used for writing tokens to disk
        """
        self.encoder_cls = encoder_cls
        if cache_path:
            self.cache_path = cache_path
        else:
            cache_path = "backend/tokens/spotify_tokens.json"
            self.cache_path = cache_path

        self.current_user = None


    @staticmethod
    def check_for_username(function: Callable):
        """Decorator to check, whether the username has been set before executing"""

        def inner(self, *args, **kwargs):
            if self.current_user is None:
                self.logger.error(f"The username has not been set, cannot execute {function.__name__}")
                return None

            return function(self, *args, **kwargs)

        return inner


    @staticmethod
    def clear_username_afterwards(function: Callable):
        """Decorator to clear the username after executing function"""

        def inner(self, *args, **kwargs):
            result = function(self, *args, **kwargs)
            self.current_user = None
            return result

        return inner


    def get_cached_token(self):
        token_info = None
        if self.current_user is None: return None

        try:
            with open(self.cache_path, encoding='utf-8') as f:
                token_info_string = f.read()
            token_info = json.loads(token_info_string)[self.current_user]

        except OSError as error:
            if error.errno == errno.ENOENT:
                self.logger.info(f"Сache does not exist at: {self.cache_path}")
            else:
                self.logger.warning(f"Couldn't read cache at: {self.cache_path}")
        except json.JSONDecodeError:
            self.logger.warning(f"Couldn't decode JSON from cache at: {self.cache_path}")
        except KeyError:
            return None

        return token_info


    @clear_username_afterwards
    def save_token_to_cache(self, token_info):
        if self.current_user is None:
            self.current_user = "temp"

        try:
            with open(self.cache_path, "r", encoding="utf-8") as f:
                current_tokens = dict(json.loads(f.read()))

            with open(self.cache_path, "w", encoding='utf-8') as f:
                current_tokens[self.current_user] = token_info
                f.write(json.dumps(current_tokens, cls=self.encoder_cls))
                
            os.chmod(self.cache_path, 0o600)

        except FileNotFoundError:
            self.logger.info(f"Creating a new JSON token file at: {self.cache_path}")

            with open(self.cache_path, "w", encoding='utf-8') as f:
                current_tokens = {self.current_user: token_info}
                f.write(json.dumps(current_tokens, cls=self.encoder_cls))
            
        except OSError:
            self.logger.warning(f"Couldn't write token to cache at: {self.cache_path}")

        except JSONDecodeError:
            self.logger.error(f"Couldn't decode JSON from cache at: {self.cache_path}. Overwriting data.")

            with open(self.cache_path, "w", encoding='utf-8') as f:
                current_tokens = {self.current_user: token_info}
                f.write(json.dumps(current_tokens, cls=self.encoder_cls))

    @clear_username_afterwards
    def assign_temp_token_to_user(self, user_id):
        """Assigns the temporary saved token to a user"""

        self.current_user = "temp"
        token_info = self.get_cached_token()
        self.current_user = user_id
        self.save_token_to_cache(token_info)

    def delete_access_tokens(self, user_id):
        """Deletes the access token of a user"""

        try:
            with(open(self.cache_path, "r", encoding='utf-8')) as f:
                current_tokens = json.loads(f.read())
                del current_tokens[user_id]

            with open(self.cache_path, "w", encoding='utf-8') as f:
                f.write(json.dumps(current_tokens, cls=self.encoder_cls))

        except OSError:
            self.logger.warning(f"Couldn't write token to cache at: {self.cache_path}")

        except JSONDecodeError:
            self.logger.error(f"Couldn't decode JSON from cache at: {self.cache_path}.")

