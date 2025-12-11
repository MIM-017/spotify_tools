import spotipy
from spotipy import Spotify
from backend.schemas import *
from backend.services.api_calls import get_song_play_count, get_artist_monthly_listeners
from backend.services.token_manager import TokenManager


class PlaylistCleaner(Spotify):
    A_PLAY_ARTIST_MONTHLY_LISTENERS = 1_500_000
    A_PLAY_SONG_STREAMS = 3_500_000

    """A Playlist Cleaner class with methods needed to detect A-Play, B-Play and Gray-Play songs.
       And manipulating playlists"""

    def __init__(self) -> None:
        """Initializes the Playlist Cleaner class"""

        # TODO: change inheritance to storing a spotipy instance
        cache_handler = TokenManager()

        auth = spotipy.SpotifyPKCE(client_id="03775c1ad3054917ae9f05d01caeb9ed",
                                   redirect_uri="http://127.0.0.1:8000/authorize_user",
                                   scope="playlist-read-private,"
                                         "playlist-read-collaborative,"
                                         "playlist-modify-private,"
                                         "playlist-modify-public",
                                   cache_handler=cache_handler)

        super().__init__(auth_manager=auth)

    def set_current_username(self, user: str):
        """Sets the username of the current user in cache_handler"""
        self.auth_manager.cache_handler.current_user = user

    def get_current_username(self):
        """Returns the username of the current user in cache_handler"""
        return self.auth_manager.cache_handler.current_user

    def get_spotify_user_username(self, access_token: str) -> str:
        self.set_auth(access_token)  # Setting the auth token manually to determine the username
        result = self.me()["id"]
        self.set_auth(None)  # Removing the auth token to allow the token manager provide further tokens
        return result

    def save_token_to_cache(self, username: str, access_token: str):
        """A helper method to access the method of TokenManager"""
        self.set_current_username(username)
        self.auth_manager.cache_handler.save_token_to_cache(access_token)

    def get_marked_playlists(self, flag=None, check_for_a_play: bool = False):
        """Returns the Playlist object of playlists marked with a provided flag"""

        if flag is None:
            flag = ""

        raw_playlists = super().current_user_playlists()  # Getting the user playlists
        playlists = raw_playlists["items"]

        while raw_playlists:  # Keep getting songs until there are no more
            raw_playlists = self.next(raw_playlists)
            if raw_playlists:
                playlists.extend(raw_playlists["items"])

        for playlist in playlists:
            name = playlist["name"]
            playlist_id = playlist["id"]
            public = playlist["public"]

            if not name.endswith(flag): continue
            is_a_play = self.is_playlist_A_play(playlist_id=playlist_id) if check_for_a_play else None

            yield Playlist(name=name,
                  playlist_id=playlist_id,
                  public=public,
                  is_a_play=is_a_play)

    def is_track_a_play(self, track: Track) -> bool:
        if track.album_id:
            play_count = get_song_play_count(track.track_id, album_id=track.album_id)
        else:
            play_count = get_song_play_count(track.track_id, spotify_client=self)

        return (play_count <= self.A_PLAY_SONG_STREAMS) and self.is_artist_a_play(track.artists[0])

    def is_artist_a_play(self, artist: Artist) -> bool:
        artist_monthly_listeners = get_artist_monthly_listeners(artist.artist_id)
        return artist_monthly_listeners <= self.A_PLAY_ARTIST_MONTHLY_LISTENERS

    def is_playlist_A_play(self, *, playlist: Playlist = None, playlist_id: str = None) -> bool:
        """Checks whether the playlist is A-Play"""

        if playlist_id is None and playlist is None:
            raise ValueError("Either playlist_id or a playlist instance is required")

        for track in self.check_playlist(playlist=playlist, playlist_id=playlist_id):
            if not track.is_a_play:
                return False
        return True

    def check_playlist(self, *, playlist: Playlist = None, playlist_id: str = None):
        """Checks every song in a playlist whether it's A-Play
        and adds the result of the check to the song's attribute .is_a_play.
        The playlist instance takes priority over the playlist_id"""

        if playlist_id is None and playlist is None:
            raise ValueError("Either playlist_id or a playlist instance is required")

        if playlist is None:
            result = self.playlist_items(playlist_id,
                                         fields="items(track(name, id, album.id, artists.id, artists.name)), next")
            # playlist_name = self.playlist(playlist_id, fields="name")["name"]

            tracks = result["items"]

            while result:  # Keep getting songs until there are no more
                result = self.next(result)
                if result:
                    tracks.extend(result["items"])

            for raw_track in tracks:
                track_name = raw_track["track"]["name"]
                track_id = raw_track["track"]["id"]
                album_id = raw_track["track"]["album"]["id"]
                artists = [Artist(name=i["name"], artist_id=i["id"]) for i in raw_track["track"]["artists"]]
                track = Track(name=track_name,
                              track_id=track_id,
                              album_id=album_id,
                              artists=artists)
                is_a_play = (self.is_track_a_play(track))
                track.is_a_play = is_a_play

                yield track

        else:
            for track in playlist.tracks:
                track.is_a_play = self.is_track_a_play(track)

                yield track

    def refine_playlist(self, *, playlist_id: str | None = None, playlist: Playlist | None = None):
        """Creates a new playlist with a name in format <Old playlist name Refined by Spotify Tools>
        with only A-Play tracks added"""

        if playlist_id is None and playlist is None:
            raise ValueError("Either playlist_id or a playlist instance is required")

        if playlist_id is None:
            playlist_id = playlist.playlist_id
            tracks = self.check_playlist(playlist=playlist)
        else:
            tracks = self.check_playlist(playlist_id=playlist_id)

        playlist_name = self.playlist(playlist_id, fields="name")["name"]

        result = self.user_playlist_create(self.me()["id"], playlist_name + " REFINED by Spotify Tools",
                                           description=f"Playlist {playlist_name} refined by Spotify Tools with B-Play and Gray-Play songs removed")
        new_playlist_id = result["id"]

        for track in tracks:
            if track.is_a_play:
                self.playlist_add_items(new_playlist_id, [track.track_id])

    def get_playlist_kuci_formatted(self, *, playlist_id: str | None = None, playlist: Playlist | None = None) -> str:
        """Provides a list of songs in the format <artist name> | <song name> | <album name>"""

        if playlist_id is None and playlist is None:
            raise ValueError("Either playlist_id or a playlist instance is required")

        if playlist is None:
            result = self.playlist_items(playlist_id,
                                         fields="items(track(name, artists.name, album.name)), next")

            tracks = result["items"]

            while result:  # Keep getting songs until there are no more
                result = self.next(result)
                if result:
                    tracks.extend(result["items"])
        else:
            tracks = playlist.tracks

        for track in [_["track"] for _ in tracks]:
            track_name = track["name"]
            artists_names = ", ".join(artist["name"] for artist in track["artists"])
            album_name = track["album"]["name"]

            yield f"{artists_names} | {track_name} | {album_name}"
