
from fastapi import FastAPI

from app.services.playlist_cleaner import PlaylistCleaner

app = FastAPI()
playlist_cleaner = PlaylistCleaner()
@app.get("/playlist_formatted/{playlist_id}")
async def get_playlist_kuci_formatted(playlist_id: str):
    result = playlist_cleaner.get_playlist_kuci_formatted(playlist_id=playlist_id)
    return list(result)

@app.get("/refine_playlist/{playlist_id}")
async def refine_playlist(playlist_id: str):
    playlist_cleaner.refine_playlist(playlist_id=playlist_id)

