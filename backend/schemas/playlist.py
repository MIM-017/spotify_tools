from pydantic import BaseModel

from .track import Track


class Playlist(BaseModel):
    name: str
    playlist_id: str
    public: bool | None = None
    tracks: list[Track] | None = None
    is_a_play: bool | None = None