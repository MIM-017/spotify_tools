from pydantic import BaseModel

class Album(BaseModel):
    name: str
    id: str | None = None
