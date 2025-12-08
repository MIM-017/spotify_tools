from pydantic import BaseModel


class Artist(BaseModel):
    name: str
    artist_id: str