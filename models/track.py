from pydantic import BaseModel

from .artist import Artist


class Track(BaseModel):
    name: str
    track_id: str
    album_id: str | None = None
    artists: list[Artist] | None = None
    is_a_play: bool | None = None