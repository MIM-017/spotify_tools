from pydantic import BaseModel

from .artist import Artist
from .album import Album


class Track(BaseModel):
    name: str
    track_id: str
    album: Album | None = None
    artists: list[Artist] | None = None
    is_a_play: bool | None = None