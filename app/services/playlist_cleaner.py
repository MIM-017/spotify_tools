import spotipy
import math
from spotipy import Spotify
from app.schemas import *
from app.services.api_calls import get_song_play_count, get_artist_monthly_listeners


class PlaylistCleaner(Spotify):
    A_PLAY_ARTIST_MONTHLY_LISTENERS = 1_500_000
    A_PLAY_SONG_STREAMS = 3_500_000

    """A Playlist Cleaner class with methods needed to detect A-Play, B-Play and Gray-Play songs.
       And manipulating playlists"""

    def __init__(self) -> None:
        """Initializes the Playlist Cleaner class"""

        auth = spotipy.SpotifyPKCE(client_id="03775c1ad3054917ae9f05d01caeb9ed",
                                   redirect_uri="https://127.0.0.1",
                                   scope="playlist-read-private,"
                                         "playlist-read-collaborative,"
                                         "playlist-modify-private,"
                                         "playlist-modify-public")

        super().__init__(auth_manager = auth)


    def get_marked_playlists(self, flag=None) -> list[Playlist]:
        """Returns the Playlist object of playlists marked with a provided flag"""

        result = []

        if flag is None:
            flag = ""

        playlists = super().current_user_playlists()  # Getting the user playlists
        if playlists["total"] > 50:  # If more than 50 playlists, make additional requests
            playlists = playlists["items"]
            number_of_additional_requests = math.ceil(playlists["total"] / 50) - 1

            for i in range(number_of_additional_requests):
                playlists.extend(super().current_user_playlists(50, (i + 1) * 50)["items"])
        else:
            playlists = playlists["items"]

        for playlist in playlists:
            name = playlist["name"]
            playlist_id = playlist["id"]
            public = playlist["public"]

            if not name.endswith(flag): continue

            result.append(Playlist(name=name,
                                   playlist_id=playlist_id,
                                   public=public))

        return result


    def is_track_a_play(self, track: Track) -> bool:
        if track.album_id:
            play_count = get_song_play_count(track.track_id, album_id=track.album_id)
        else:
            play_count = get_song_play_count(track.track_id, spotify_client=self)

        return (play_count <= self.A_PLAY_SONG_STREAMS) and self.is_artist_a_play(track.artists[0])


    def is_artist_a_play(self, artist: Artist) -> bool:
        artist_monthly_listeners = get_artist_monthly_listeners(artist.artist_id)
        return artist_monthly_listeners <= self.A_PLAY_ARTIST_MONTHLY_LISTENERS


    def check_playlist(self, *, playlist: Playlist = None, playlist_id: str = None):
        """Checks every song in a playlist whether it's A-Play
        and adds the result of the check to the song's attribute .is_a_play"""

        if playlist_id is None and playlist is None:
            raise ValueError("Either playlist_id or a playlist instance is required")

        if playlist is None:
            result = self.playlist_items(playlist_id, fields="items(track(name, id, album.id, artists.id, artists.name)), next")
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
            tracks = self.check_playlist(playlist = playlist)
        else:
            tracks = self.check_playlist(playlist_id = playlist_id)

        playlist_name = self.playlist(playlist_id, fields="name")["name"]

        result = self.user_playlist_create(self.me()["id"], playlist_name + " REFINED by Spotify Tools",
                                  description=f"Playlist {playlist_name} refined by Spotify Tools with B-Play and Gray-Play songs removed")
        new_playlist_id = result["id"]

        for track in tracks:
            if track.is_a_play:
                self.playlist_add_items(new_playlist_id, [track.track_id])

