import requests
import spotipy

API_ROOT = "https://api.t4ils.dev/"


def get_artist_info(artist_id: str):
    response = requests.get(f"{API_ROOT}artistInsights", params={"artistid": artist_id})
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return get_artist_info(artist_id)
    return response.json()


def get_album_info(album_id: str):
    response = requests.get(f"{API_ROOT}albumPlayCount", params={"albumid": album_id})
    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return get_album_info(album_id)
    return response.json()


def get_artist_monthly_listeners(artist_id: str):
    response = get_artist_info(artist_id)
    return response["data"]["monthlyListeners"]


def get_song_play_count(song_id: str, *, album_id: str = None, spotify_client: spotipy.Spotify = None):
    """Provides the number of plays on a song.
    Album ID or an instance of Spotipy Client has to be provided.
    Better performance is achieved if album ID is provided."""

    if album_id is None and spotify_client is None:
        raise ValueError("Either album_id or spotify_client must be provided")

    if album_id:
        return _get_song_play_count_with_album_id(song_id, album_id)

    else:
        album_id = spotify_client.track(song_id)["album"]["id"]
        return _get_song_play_count_with_album_id(song_id, album_id)


def _get_song_play_count_with_album_id(song_id: str, album_id: str):
    disks = get_album_info(album_id)["data"]["discs"]

    for disk in disks:
        for track in disk["tracks"]:
            track_id = track["uri"].split(":")[-1]

            if track_id == song_id:
                return track["playcount"]
